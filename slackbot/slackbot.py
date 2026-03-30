#!/usr/bin/env python3
"""
slackbot — Slack Socket Mode bot for Decyphertek AI.
Connects to Slack via outbound WebSocket. No public IP required.
Credentials: ~/.decyphertek.ai/app-store/slackbot/slackbot.yaml
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


def get_resource_path(relative_path):
    try:
        base_path = Path(sys._MEIPASS)
    except Exception:
        base_path = Path(__file__).parent
    return base_path / relative_path


class Colors:
    CYAN   = '\033[96m'
    GREEN  = '\033[92m'
    BLUE   = '\033[94m'
    RED    = '\033[91m'
    YELLOW = '\033[93m'
    RESET  = '\033[0m'
    BOLD   = '\033[1m'
    DIM    = '\033[2m'


logging.basicConfig(level=logging.WARNING)
log = logging.getLogger("slackbot")

_ANSI = re.compile(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")
strip_ansi = lambda t: _ANSI.sub("", t)

CONFIG_PATH = Path.home() / ".decyphertek.ai" / "app-store" / "slackbot" / "slackbot.yaml"

_AGENT_SEARCH_PATHS = [
    Path.home() / ".decyphertek.ai" / "agent-store" / "adminotaur" / "adminotaur.py",
    Path.home() / "Documents" / "git" / "agent-store" / "adminotaur" / "adminotaur.py",
]


# ── Onboarding ────────────────────────────────────────────────────────────────

def show_banner():
    print(f"""
{Colors.CYAN}{Colors.BOLD}
╔═══════════════════════════════════════════════════════════════╗
║                                                               ║
║              {Colors.GREEN}S L A C K B O T  —  D E C Y P H E R T E K{Colors.CYAN}      ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝
{Colors.RESET}
{Colors.BLUE}    ▸ SOCKET MODE — NO PUBLIC IP REQUIRED
    ▸ ROUTES MESSAGES TO ADMINOTAUR AGENT
    ▸ FIRST RUN: FOLLOW THE SETUP STEPS BELOW
{Colors.RESET}""")


def show_setup_instructions():
    print(f"""{Colors.CYAN}{Colors.BOLD}  SLACK APP SETUP{Colors.RESET}
{Colors.DIM}  ─────────────────────────────────────────────────────{Colors.RESET}

  {Colors.YELLOW}1.{Colors.RESET} Go to {Colors.BLUE}https://api.slack.com/apps{Colors.RESET}
     → Create New App → From scratch → name it {Colors.GREEN}Adminotaur{Colors.RESET}

  {Colors.YELLOW}2.{Colors.RESET} {Colors.BOLD}Enable Socket Mode{Colors.RESET}
     → Left sidebar: Socket Mode → toggle ON
     → Generate App-Level Token — scope: {Colors.GREEN}connections:write{Colors.RESET}
     → Copy the {Colors.GREEN}xapp-...{Colors.RESET} token

  {Colors.YELLOW}3.{Colors.RESET} {Colors.BOLD}Bot Token Scopes{Colors.RESET} (OAuth & Permissions → Bot Token Scopes)
     → Add: {Colors.GREEN}app_mentions:read  chat:write  im:history  im:read  im:write{Colors.RESET}

  {Colors.YELLOW}4.{Colors.RESET} {Colors.BOLD}Subscribe to Bot Events{Colors.RESET} (Event Subscriptions → toggle ON)
     → Add: {Colors.GREEN}app_mention  message.im{Colors.RESET}

  {Colors.YELLOW}5.{Colors.RESET} {Colors.BOLD}Install App{Colors.RESET} → Install to Workspace → Allow
     → Copy the {Colors.GREEN}xoxb-...{Colors.RESET} Bot User OAuth Token

{Colors.DIM}  ─────────────────────────────────────────────────────{Colors.RESET}
""")


def onboard() -> dict:
    show_banner()
    show_setup_instructions()

    print(f"{Colors.BLUE}[SETUP]{Colors.RESET} No config found. Let's configure slackbot.\n")

    bot_token = input(f"  {Colors.GREEN}Bot Token{Colors.RESET} (xoxb-...): ").strip()
    if not bot_token.startswith("xoxb-"):
        print(f"\n{Colors.RED}[ERROR]{Colors.RESET} Bot token must start with xoxb-. Exiting.\n")
        sys.exit(1)

    app_token = input(f"  {Colors.GREEN}App Token{Colors.RESET} (xapp-...): ").strip()
    if not app_token.startswith("xapp-"):
        print(f"\n{Colors.RED}[ERROR]{Colors.RESET} App token must start with xapp-. Exiting.\n")
        sys.exit(1)

    cfg = {"bot_token": bot_token, "app_token": app_token, "allowed_users": []}

    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(CONFIG_PATH, "w") as f:
        yaml.dump(cfg, f, default_flow_style=False)

    print(f"\n{Colors.GREEN}[✓]{Colors.RESET} Config saved to {CONFIG_PATH}\n")
    return cfg


def load_config() -> dict:
    if not CONFIG_PATH.exists():
        return onboard()

    with open(CONFIG_PATH) as f:
        cfg = yaml.safe_load(f) or {}

    cfg["bot_token"] = os.environ.get("SLACK_BOT_TOKEN", cfg.get("bot_token", ""))
    cfg["app_token"] = os.environ.get("SLACK_APP_TOKEN", cfg.get("app_token", ""))

    if not cfg.get("bot_token") or not cfg.get("app_token"):
        print(f"{Colors.RED}[ERROR]{Colors.RESET} Missing tokens in {CONFIG_PATH}. Delete it to re-run setup.")
        sys.exit(1)

    return cfg


# ── Adminotaur loader ─────────────────────────────────────────────────────────

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
            print(f"{Colors.GREEN}[✓]{Colors.RESET} Adminotaur loaded from {path}")
            return mod
    raise RuntimeError(
        "Adminotaur not found. Checked:\n" + "\n".join(str(p) for p in _AGENT_SEARCH_PATHS)
    )


def get_agent(user_id: str):
    if user_id not in _agents:
        mod = _load_agent_module()
        print(f"{Colors.BLUE}[AGENT]{Colors.RESET} New session for user {user_id}")
        _agents[user_id] = mod.Adminotaur()
    return _agents[user_id]


def ask_adminotaur(user_id: str, text: str) -> str:
    try:
        agent = get_agent(user_id)
        response = agent.process(text)
        return strip_ansi(response or "").strip() or "(no response)"
    except Exception as exc:
        log.exception("Adminotaur error for user %s", user_id)
        return f"Error: {exc}"


# ── Slack helpers ─────────────────────────────────────────────────────────────

def clean_message(text: str, bot_user_id: str) -> str:
    return re.sub(rf"<@{re.escape(bot_user_id)}>", "", text).strip()


def split_blocks(text: str, limit: int = 3000) -> list[str]:
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
    for chunk in split_blocks(response):
        client.chat_postMessage(channel=channel, thread_ts=thread_ts, text=chunk, mrkdwn=True)


# ── App ───────────────────────────────────────────────────────────────────────

def build_app(cfg: dict) -> App:
    app = App(token=cfg["bot_token"])
    allowed = set(filter(None, cfg.get("allowed_users", [])))

    def _allowed(user_id: str) -> bool:
        return not allowed or user_id in allowed

    def _handle(user_id, text, say, client, channel, thread_ts):
        if not _allowed(user_id):
            log.warning("Blocked unauthorized user %s", user_id)
            return
        if not text:
            say(text="Send me a message and I'll pass it to Adminotaur.", thread_ts=thread_ts)
            return

        print(f"{Colors.CYAN}[MSG]{Colors.RESET} {user_id}: {text[:120]}")
        start = time.time()
        response = ask_adminotaur(user_id, text)
        print(f"{Colors.GREEN}[REPLY]{Colors.RESET} {time.time()-start:.1f}s — {response[:120]}")
        post_response(client, channel, thread_ts, response)

    @app.event("app_mention")
    def handle_mention(event, say, client):
        try:
            bot_id = client.auth_test()["user_id"]
        except Exception:
            bot_id = ""
        _handle(
            event.get("user", "unknown"),
            clean_message(event.get("text", ""), bot_id),
            say, client,
            event.get("channel", ""),
            event.get("thread_ts") or event.get("ts"),
        )

    @app.event("message")
    def handle_dm(event, say, client):
        if event.get("channel_type") != "im":
            return
        if event.get("subtype") or event.get("bot_id"):
            return
        _handle(
            event.get("user", "unknown"),
            event.get("text", "").strip(),
            say, client,
            event.get("channel", ""),
            event.get("thread_ts") or event.get("ts"),
        )

    return app


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    cfg = load_config()
    show_banner()
    print(f"{Colors.BLUE}[SYSTEM]{Colors.RESET} Starting slackbot via Socket Mode...\n")

    try:
        _load_agent_module()
    except RuntimeError as e:
        print(f"{Colors.YELLOW}[WARN]{Colors.RESET} {e}")

    app = build_app(cfg)
    handler = SocketModeHandler(app, cfg["app_token"])
    print(f"{Colors.GREEN}[✓]{Colors.RESET} Slackbot is running. Press Ctrl+C to stop.\n")
    handler.start()


if __name__ == "__main__":
    main()
