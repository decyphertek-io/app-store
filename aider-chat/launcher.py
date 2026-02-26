#!/usr/bin/env python3
import os
import sys
import yaml
import getpass
from pathlib import Path


class Colors:
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    RESET = '\033[0m'
    BOLD = '\033[1m'


APP_DIR = Path.home() / ".decyphertek.ai"
APP_STORE_DIR = APP_DIR / "app-store" / "aider-chat"
CONFIG_DIR = APP_DIR / "configs" / "aider-chat"
CONFIG_FILE = CONFIG_DIR / "config.yaml"

PROVIDERS = {
    "1": {"name": "deepseek",   "model": "deepseek",  "key_prefix": "deepseek"},
    "2": {"name": "anthropic",  "model": "sonnet",    "key_prefix": "anthropic"},
    "3": {"name": "openai",     "model": "o3-mini",   "key_prefix": "openai"},
    "4": {"name": "openrouter", "model": "",          "key_prefix": "openrouter"},
}


def info(msg):
    print(f"{Colors.CYAN}[aider-chat]{Colors.RESET} {msg}")


def ok(msg):
    print(f"{Colors.GREEN}[ok]{Colors.RESET} {msg}")


def error(msg):
    print(f"{Colors.RED}[error]{Colors.RESET} {msg}")


def ensure_dirs():
    APP_STORE_DIR.mkdir(parents=True, exist_ok=True)
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)


def load_config():
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE) as f:
            return yaml.safe_load(f) or {}
    return {}


def save_config(cfg):
    with open(CONFIG_FILE, "w") as f:
        yaml.dump(cfg, f)


def setup():
    print(f"""
{Colors.CYAN}{Colors.BOLD}
╔═══════════════════════════════════════════════════════════════╗
║                                                               ║
║               {Colors.GREEN}A I D E R - C H A T{Colors.CYAN}                          ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝
{Colors.RESET}""")
    info("First run setup - selecting AI provider.")
    print(f"\n{Colors.CYAN}Select provider:{Colors.RESET}")
    for k, v in PROVIDERS.items():
        print(f"  {Colors.BOLD}{k}{Colors.RESET}. {v['name']}")

    while True:
        choice = input("\nEnter number: ").strip()
        if choice in PROVIDERS:
            break
        error("Invalid choice.")

    provider = PROVIDERS[choice]

    if provider["name"] == "openrouter":
        model = input(f"  OpenRouter model [{Colors.YELLOW}anthropic/claude-sonnet-4-6{Colors.RESET}]: ").strip()
        provider["model"] = model if model else "anthropic/claude-sonnet-4-6"

    api_key = getpass.getpass(f"  Enter {provider['name']} API key (hidden): ")
    if not api_key:
        error("API key cannot be empty.")
        sys.exit(1)

    cfg = {
        "provider": provider["name"],
        "model": provider["model"],
        "key_prefix": provider["key_prefix"],
        "api_key": api_key,
    }
    save_config(cfg)
    ok(f"Config saved to {CONFIG_FILE}")
    return cfg


def run_aider(cfg, extra_args, decyphertek_mode=False):
    model = cfg["model"]
    key_prefix = cfg["key_prefix"]
    api_key = cfg["api_key"]

    info(f"Launching: aider --model {model} [api-key hidden] {' '.join(extra_args)}")

    if key_prefix == "openrouter":
        os.environ["OPENROUTER_API_KEY"] = api_key
        full_model = f"openrouter/{model}"
    else:
        os.environ[f"{key_prefix.upper()}_API_KEY"] = api_key
        full_model = model

    print(f"""
{Colors.CYAN}{Colors.BOLD}╔═══════════════════════════════════════════════════════════════╗
║                   AIDER QUICK REFERENCE                       ║
╚═══════════════════════════════════════════════════════════════╝{Colors.RESET}
  {Colors.GREEN}/add <path>{Colors.RESET}     Add a file or directory to the chat
  {Colors.GREEN}/drop <file>{Colors.RESET}    Remove a file from the chat
  {Colors.GREEN}/ls{Colors.RESET}             List files currently in the chat
  {Colors.GREEN}/diff{Colors.RESET}           Show changes made
  {Colors.GREEN}/undo{Colors.RESET}           Undo last change
  {Colors.GREEN}/run <cmd>{Colors.RESET}      Run a shell command
  {Colors.GREEN}/clear{Colors.RESET}          Clear the chat history
  {Colors.GREEN}/exit{Colors.RESET}           Quit aider

  {Colors.YELLOW}Tip:{Colors.RESET} Use /add with full absolute paths, e.g:
  {Colors.YELLOW}/add /home/user/Documents/git/my-repo/{Colors.RESET}
""")

    os.chdir(Path.home())

    from aider.main import main as aider_main
    aider_args = ["aider", "--model", full_model, "--api-key", f"{key_prefix}={api_key}",
                  "--no-gitignore", "--no-git",
                  "--chat-history-file", str(APP_STORE_DIR / ".aider.chat.history.md"),
                  "--input-history-file", str(APP_STORE_DIR / ".aider.input.history")]
    if decyphertek_mode:
        aider_args += ["--no-pretty", "--yes"]
    sys.argv = aider_args + extra_args
    aider_main()


def main():
    ensure_dirs()
    cfg = load_config()

    if not cfg or "--setup" in sys.argv:
        cfg = setup()

    extra_args = [a for a in sys.argv[1:] if a not in ("--setup", "--decyphertek")]
    decyphertek_mode = "--decyphertek" in sys.argv
    run_aider(cfg, extra_args, decyphertek_mode)


if __name__ == "__main__":
    main()
