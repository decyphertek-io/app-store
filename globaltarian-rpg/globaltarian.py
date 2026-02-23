#!/usr/bin/env python3
"""GLOBALTARIAN - Cyberpunk AI Worm Hunt RPG - Year 2184"""
import os
from textual.app import App, ComposeResult
from textual.containers import Container
from textual.widgets import Header, Footer, Static, Input, RichLog
from textual.binding import Binding
from pathlib import Path

HOME = Path.home()
GAME_DIR = HOME / ".decyphertek.ai/app-store/globaltarian-rpg"
CONFIG_FILE = GAME_DIR / "config"

# ANSI colors for terminal output
CYAN = "\033[96m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
MAGENTA = "\033[95m"
RESET = "\033[0m"

def setup_api_key():
    """First-run setup for OpenRouter API key"""
    print(f"\n{CYAN}═══ GLOBALTARIAN FIRST RUN SETUP ═══{RESET}\n")
    print(f"{YELLOW}Configuration storage: {GAME_DIR}{RESET}\n")
    
    print(f"{GREEN}OpenRouter API Key Setup:{RESET}")
    print(f"{CYAN}To get your OpenRouter API key:{RESET}")
    print(f"{CYAN}1. Visit: https://openrouter.ai/keys{RESET}")
    print(f"{CYAN}2. Sign up or log in{RESET}")
    print(f"{CYAN}3. Create a new API key{RESET}")
    print(f"{CYAN}4. Copy the key and paste it below{RESET}\n")
    
    api_key = input(f"{CYAN}OpenRouter API Key:{RESET} ").strip()
    
    if api_key:
        CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(CONFIG_FILE, 'w') as f:
            f.write(f"OPENROUTER_API_KEY={api_key}\n")
        CONFIG_FILE.chmod(0o600)  # Secure permissions
        print(f"{GREEN}✓ API key saved securely{RESET}\n")
        return api_key
    else:
        print(f"{RED}⚠ No API key provided. AI features will be disabled.{RESET}\n")
        return None

def load_api_key():
    """Load OpenRouter API key from config"""
    if not CONFIG_FILE.exists():
        return setup_api_key()
    
    try:
        with open(CONFIG_FILE, 'r') as f:
            for line in f:
                if line.startswith("OPENROUTER_API_KEY="):
                    key = line.split("=", 1)[1].strip()
                    os.environ['OPENROUTER_API_KEY'] = key
                    return key
    except Exception:
        return setup_api_key()
    
    return setup_api_key()

class GameState:
    def __init__(self):
        self.player = "Chase"
        self.location = "central_hub"
        self.health = 100
        self.threat = 0
        self.api_key = None

NETWORK = {
    "central_hub": {"desc": "Central Hub - Neon data streams pulse. Amber warnings glow.", "exits": ["vault", "security"]},
    "vault": {"desc": "Data Vault - Encrypted archives. Something moves in shadows.", "exits": ["central_hub"]},
    "security": {"desc": "Security Core - Firewalls flicker. Worm traces detected.", "exits": ["central_hub"], "worm": True},
}

class GlobaltarianRPG(App):
    CSS = """
    #log { height: 70%; border: solid #00ff41; background: #000; color: #00ff41; }
    #status { height: 5; border: solid #ff00ff; background: #0a0a0a; color: #ff00ff; }
    #input { dock: bottom; height: 3; border: solid #00ffff; }
    """
    
    BINDINGS = [Binding("ctrl+q", "quit", "Quit")]
    
    def __init__(self):
        super().__init__()
        self.state = GameState()
        GAME_DIR.mkdir(parents=True, exist_ok=True)
        
    def compose(self) -> ComposeResult:
        yield Header()
        with Container():
            yield RichLog(id="log")
            yield Static(id="status")
            yield Input(placeholder="Command...", id="input")
        yield Footer()
        
    def on_mount(self):
        # Load API key before starting game
        self.state.api_key = load_api_key()
        
        log = self.query_one("#log", RichLog)
        log.write("[bold cyan]GLOBALTARIAN[/bold cyan] - Year 2184")
        log.write("[red]⚠ Polymorphic AI Worm Detected[/red]")
        log.write("[yellow]Mission: Traceroute network and neutralize worm[/yellow]\n")
        
        if self.state.api_key:
            log.write("[green]✓ OpenRouter AI: ONLINE[/green]")
        else:
            log.write("[yellow]⚠ OpenRouter AI: OFFLINE (AI features disabled)[/yellow]")
        
        log.write(f"\n[green]{NETWORK[self.state.location]['desc']}[/green]")
        self.update_status()
        
    def update_status(self):
        status = self.query_one("#status", Static)
        status.update(f"Location: {self.state.location} | Health: {self.state.health}% | Threat: {self.state.threat}%")
        
    def on_input_submitted(self, event):
        cmd = event.value.strip().lower()
        event.input.value = ""
        log = self.query_one("#log", RichLog)
        
        if cmd == "help":
            log.write("[cyan]Commands: scan, move <location>, traceroute, event, help, quit[/cyan]")
        elif cmd == "scan":
            loc = NETWORK[self.state.location]
            log.write(f"[yellow]Scanning... Exits: {', '.join(loc['exits'])}[/yellow]")
            if loc.get("worm"):
                log.write("[red]⚠ WORM SIGNATURE DETECTED![/red]")
                self.state.threat += 20
        elif cmd.startswith("move "):
            dest = cmd.split()[1] if len(cmd.split()) > 1 else ""
            if dest in NETWORK[self.state.location]["exits"]:
                self.state.location = dest
                log.write(f"[green]Moving to {dest}...[/green]")
                log.write(NETWORK[dest]["desc"])
            else:
                log.write("[red]Invalid destination[/red]")
        elif cmd == "traceroute":
            log.write("[cyan]Tracing network paths...[/cyan]")
            for node in NETWORK:
                if NETWORK[node].get("worm"):
                    log.write(f"[red]Worm detected at: {node}[/red]")
        elif cmd == "quit":
            self.exit()
        else:
            log.write("[red]Unknown command. Type 'help'[/red]")
            
        self.update_status()

if __name__ == "__main__":
    app = GlobaltarianRPG()
    app.run()
