#!/usr/bin/env python3
"""
slackbot — Slack Socket Mode bot for Decyphertek AI.
Connects to Slack via outbound WebSocket. No public IP required.
Credentials: slackbot.yaml or SLACK_BOT_TOKEN / SLACK_APP_TOKEN env vars.
"""

import os
import re
import sys
import time
import logging
import importlib.util
from pathlib import Path

import yaml
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

# ── Logging ───────────────────────────────────────────────────────────────────

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
log = logging.getLogger("slackbot")

# ── ANSI strip ────────────────────────────────────────────────────────────────

_ANSI = re.compile(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")


def strip_ansi(text: str) -> str:
    return _ANSI.sub("", text)


# ── Config loader ─────────────────────────────────────────────────────────────

def load_config() -> dict:
    """Load config from slackbot.yaml next to this file, then env vars override."""
    cfg = {}
    yaml_path = Path(__file__).parent / "slackbot.yaml"
    if yaml_path.exists():
        with open(yaml_path) as f:
            cfg = yaml.safe_load(f) or {}
        log.info("Loaded config from %s", yaml_path)

    # Env vars always win
    cfg["bot_token"] = os.environ.get("SLACK_BOT_TOKEN", cfg.get("bot_token", ""))
    cfg["app_token"] = os.environ.get("SLACK_APP_TOKEN", cfg.get("app_token", ""))
    cfg["allowed_users"] = os.environ.get(
        "SLACK_ALLOWED_USERS", ",".join(cfg.get("allowed_users", []))
    ).split(",") if os.environ.get("SLACK_ALLOWED_USERS") else cfg.get("allowed_users", [])
    cfg["bot_name"] = cfg.get("bot_name", "Adminotaur")

    if not cfg["bot_token"]:
        log.error("SLACK_BOT_TOKEN is not set.")
        sys.exit(1)
    if not cfg["app_token"]:
        log.error("SLACK_APP_TOKEN is not set.")
        sys.exit(1)

    return cfg


# ── Adminotaur loader ─────────────────────────────────────────────────────────

# Locations to search for adminotaur.py, most specific first
_AGENT_SEARCH_PATHS = [
    Path.home() / ".decyphertek.ai" / "agent-store" / "adminotaur" / "adminotaur.py",
    Path.home() / "Documents" / "git" / "agent-store" / "adminotaur" / "adminotaur.py",
]

# Cached agent instances keyed by Slack user_id for isolated memory per user
_agents: dict = {}
_agent_module = None


def _load_agent_module():
    global _agent_module
    if _agent_module is not None:
        return _agent_module
    for path in _AGENT_SEARCH_PATHS:
        if path.exists():
            spec = importlib.util.spec_from_file_location("adminotaur", str(path))
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            _agent_module = mod
            log.info("Adminotaur module loaded from %s", path)
            return mod
    raise RuntimeError(
        "Adminotaur not found. Checked:\n" + "\n".join(str(p) for p in _AGENT_SEARCH_PATHS)
    )


def get_agent(user_id: str):
    """Return a per-user Adminotaur instance (creates one on first use)."""
    if user_id not in _agents:
        mod = _load_agent_module()
        log.info("Creating Adminotaur instance for user %s", user_id)
        _agents[user_id] = mod.Adminotaur()
    return _agents[user_id]


def ask_adminotaur(user_id: str, text: str) -> str:
    """Send text to the user's Adminotaur instance and return the response."""
    try:
        agent = get_agent(user_id)
        response = agent.process(text)
        return strip_ansi(response or "").strip() or "(no response)"
    except Exception as exc:
        log.exception("Adminotaur error for user %s", user_id)
        return f"Error talking to Adminotaur: {exc}"


# ── Slack helpers ─────────────────────────────────────────────────────────────

def clean_message(text: str, bot_user_id: str) -> str:
    """Strip @bot mentions and leading/trailing whitespace from a message."""
    text = re.sub(rf"<@{re.escape(bot_user_id)}>", "", text)
    return text.strip()


def split_blocks(text: str, limit: int = 3000) -> list[str]:
    """Split long responses into chunks that fit Slack's block limit."""
    chunks = []
    while len(text) > limit:
        split_at = text.rfind("\n", 0, limit)
        if split_at == -1:
            split_at = limit
        chunks.append(text[:split_at])
        text = text[split_at:].lstrip()
    if text:
        chunks.append(text)
    return chunks


def post_response(client, channel: str, thread_ts: str | None, response: str):
    """Post a (possibly multi-chunk) response back to Slack."""
    chunks = split_blocks(response)
    for i, chunk in enumerate(chunks):
        client.chat_postMessage(
            channel=channel,
            thread_ts=thread_ts,
            text=chunk,
            mrkdwn=True,
        )


# ── App setup ─────────────────────────────────────────────────────────────────

def build_app(cfg: dict) -> App:
    app = App(token=cfg["bot_token"])
    allowed = set(filter(None, cfg.get("allowed_users", [])))

    def _allowed(user_id: str) -> bool:
        return not allowed or user_id in allowed

    def _handle(user_id: str, text: str, say, client, channel: str, thread_ts: str | None):
        if not _allowed(user_id):
            log.warning("Blocked unauthorized user %s", user_id)
            return

        if not text:
            say(text="Say something and I'll pass it to Adminotaur.", thread_ts=thread_ts)
            return

        # Show typing indicator
        try:
            client.assistant_threads_setStatus(
                channel_id=channel,
                thread_ts=thread_ts or "",
                status="is thinking...",
            )
        except Exception:
            pass  # Not all app configs support this — ignore

        log.info("User %s → %s", user_id, text[:120])
        start = time.time()
        response = ask_adminotaur(user_id, text)
        elapsed = time.time() - start
        log.info("Response in %.1fs: %s", elapsed, response[:120])

        post_response(client, channel, thread_ts, response)

    # ── Event: app_mention (@bot in a channel) ────────────────────────────────
    @app.event("app_mention")
    def handle_mention(event, say, client):
        user_id = event.get("user", "unknown")
        raw_text = event.get("text", "")
        channel = event.get("channel", "")
        thread_ts = event.get("thread_ts") or event.get("ts")

        # Resolve bot user ID to strip mention prefix
        try:
            bot_id = client.auth_test()["user_id"]
        except Exception:
            bot_id = ""

        text = clean_message(raw_text, bot_id)
        _handle(user_id, text, say, client, channel, thread_ts)

    # ── Event: direct message ─────────────────────────────────────────────────
    @app.event("message")
    def handle_dm(event, say, client):
        # Only handle DMs (channel_type == "im"), skip bot messages and edits
        if event.get("channel_type") != "im":
            return
        if event.get("subtype"):
            return
        if event.get("bot_id"):
            return

        user_id = event.get("user", "unknown")
        text = event.get("text", "").strip()
        channel = event.get("channel", "")
        thread_ts = event.get("thread_ts") or event.get("ts")

        _handle(user_id, text, say, client, channel, thread_ts)

    return app


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    cfg = load_config()
    log.info("Starting %s via Socket Mode...", cfg["bot_name"])

    # Pre-load the agent module at startup so first message isn't slow
    try:
        _load_agent_module()
    except RuntimeError as e:
        log.warning("Agent pre-load skipped: %s", e)

    app = build_app(cfg)
    handler = SocketModeHandler(app, cfg["app_token"])
    log.info("%s is running. Press Ctrl+C to stop.", cfg["bot_name"])
    handler.start()


if __name__ == "__main__":
    main()
