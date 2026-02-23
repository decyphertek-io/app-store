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
        log = self.query_one("#log", RichLog)
        
        # Intro story
        log.write("[bold cyan]═══════════════════════════════════════════[/bold cyan]")
        log.write("[bold cyan]         GLOBALTARIAN - YEAR 2184          [/bold cyan]")
        log.write("[bold cyan]═══════════════════════════════════════════[/bold cyan]\n")
        
        log.write("[yellow]You are Chase, ex-Multitek security specialist.[/yellow]")
        log.write("[yellow]Three months ago, you discovered Project Globaltarian -[/yellow]")
        log.write("[yellow]a rogue AI designed for digital immortality.[/yellow]\n")
        
        log.write("[red]They burned you. Erased your identity. Made you a ghost.[/red]\n")
        
        log.write("[white]Now, a polymorphic AI tears through the network.[/white]")
        log.write("[white]The corps blame hackers. Hackers blame corps.[/white]")
        log.write("[white]But you know the truth: This is the Globaltarian AI.[/white]")
        log.write("[white]And it's waking up.[/white]\n")
        
        log.write("[cyan]Your only ally: The Guardian, an ancient network AI.[/cyan]")
        log.write("[cyan]But can you trust it? Or is it part of the Globaltarian?[/cyan]\n")
        
        # Check for API key (non-blocking)
        if CONFIG_FILE.exists():
            try:
                with open(CONFIG_FILE, 'r') as f:
                    for line in f:
                        if line.startswith("OPENROUTER_API_KEY="):
                            self.state.api_key = line.split("=", 1)[1].strip()
                            os.environ['OPENROUTER_API_KEY'] = self.state.api_key
                            break
            except:
                pass
        
        if self.state.api_key:
            log.write("[green]✓ AI GAME MASTER: ONLINE[/green]")
            log.write("[green]The story adapts to your choices...[/green]\n")
            
            # Trigger initial AI story event
            log.write("[bold magenta]>>> The Guardian materializes...[/bold magenta]")
            log.write("[cyan]Guardian: 'Chase. I've been waiting for you.'[/cyan]")
            log.write("[cyan]Guardian: 'The Globaltarian AI is not what it seems.'[/cyan]")
            log.write("[cyan]Guardian: 'Every choice you make teaches it. Every move feeds it.'[/cyan]")
            log.write("[cyan]Guardian: 'Are you ready to face the truth?'[/cyan]\n")
            log.write("[dim]Type 'event' to continue the story...[/dim]\n")
        else:
            log.write("[yellow]⚠ AI GAME MASTER: OFFLINE[/yellow]")
            log.write("[yellow]Type 'setup' to enable AI-driven storytelling[/yellow]\n")
        
        log.write(f"[bold green]>>> {NETWORK[self.state.location]['desc']}[/bold green]\n")
        log.write("[dim]Type 'help' for commands[/dim]")
        self.update_status()
        
    def update_status(self):
        status = self.query_one("#status", Static)
        status.update(f"Location: {self.state.location} | Health: {self.state.health}% | Threat: {self.state.threat}%")
        
    def on_input_submitted(self, event):
        cmd = event.value.strip().lower()
        event.input.value = ""
        log = self.query_one("#log", RichLog)
        
        if cmd == "help":
            log.write("[cyan]Commands: scan, move <location>, traceroute, event, setup, help, quit[/cyan]")
        elif cmd == "setup":
            log.write("[bold yellow]═══ API KEY SETUP ═══[/bold yellow]")
            log.write("[cyan]To enable AI Game Master features:[/cyan]")
            log.write("[cyan]1. Visit: https://openrouter.ai/keys[/cyan]")
            log.write("[cyan]2. Sign up and create an API key[/cyan]")
            log.write("[cyan]3. Save key to: ~/.decyphertek.ai/app-store/globaltarian-rpg/config[/cyan]")
            log.write("[cyan]4. Format: OPENROUTER_API_KEY=your-key-here[/cyan]")
            log.write("[cyan]5. Restart the game[/cyan]")
            log.write("[yellow]Or run setup manually before launching game[/yellow]")
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
        elif cmd == "event":
            if self.state.api_key:
                log.write("[cyan]>>> AI Event Flow Triggered...[/cyan]")
                try:
                    from event_flow import run_event_cycle
                    result = run_event_cycle({
                        "location": self.state.location,
                        "health": self.state.health,
                        "threat_level": self.state.threat,
                        "worms_found": 0
                    })
                    evt = result.get("current_event", {})
                    log.write(f"[yellow]{evt.get('desc', 'Unknown event')}[/yellow]")
                    for resp in result.get("agent_responses", []):
                        log.write(f"[cyan]{resp}[/cyan]")
                    self.state.health = result.get("health", self.state.health)
                    self.state.threat = result.get("threat_level", self.state.threat)
                except Exception as e:
                    log.write(f"[red]Error: {str(e)}[/red]")
            else:
                log.write("[yellow]AI offline - API key required[/yellow]")
        elif cmd == "quit":
            self.exit()
        else:
            log.write("[red]Unknown command. Type 'help'[/red]")
            
        self.update_status()

if __name__ == "__main__":
    app = GlobaltarianRPG()
    app.run()
