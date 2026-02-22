#!/usr/bin/env python3
"""
cloudtek-tui - Unified TUI for AWS, GCP, and Azure cloud management
Pure Python implementation using native SDKs (boto3, google-cloud-*, azure-*)
"""
from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import Header, Footer, Button, Static, Label
from textual.binding import Binding
from pathlib import Path
import yaml
import sys

HOME = Path.home()
APP_DIR = HOME / ".decyphertek.ai/app-store/cloudtek-tui"
CONFIG_FILE = APP_DIR / "config.yaml"
AWS_CREDS_DIR = APP_DIR / "aws"
GCP_CREDS_DIR = APP_DIR / "gcp"
AZURE_CREDS_DIR = APP_DIR / "azure"

class ProviderCard(Static):
    """Card widget for cloud provider selection"""
    
    def __init__(self, provider_name: str, status: str = "Inactive", **kwargs):
        super().__init__(**kwargs)
        self.provider_name = provider_name
        self.status = status
    
    def compose(self) -> ComposeResult:
        yield Label(f"[bold]{self.provider_name}[/bold]")
        yield Label(f"Status: {self.status}")

def check_credentials() -> dict:
    """Check which providers have credentials configured"""
    return {
        'aws': (AWS_CREDS_DIR / "credentials").exists(),
        'gcp': (GCP_CREDS_DIR / "application_default_credentials.json").exists(),
        'azure': (AZURE_CREDS_DIR / "credentials.json").exists()
    }

class Dashboard(Container):
    """Main dashboard showing provider cards"""
    
    def compose(self) -> ComposeResult:
        creds_status = check_credentials()
        
        yield Static("[bold cyan]cloudtek-tui[/bold cyan] - Multi-Cloud Management", id="title")
        yield Static("")
        
        aws_status = "Configured" if creds_status['aws'] else "Not Configured"
        gcp_status = "Configured" if creds_status['gcp'] else "Not Configured"
        azure_status = "Configured" if creds_status['azure'] else "Not Configured"
        
        yield Static("[bold]Cloud Providers:[/bold]")
        with Horizontal(id="provider-grid"):
            yield ProviderCard("AWS", aws_status, id="aws-card", classes="provider-card")
            yield ProviderCard("GCP", gcp_status, id="gcp-card", classes="provider-card")
            yield ProviderCard("Azure", azure_status, id="azure-card", classes="provider-card")
        
        yield Static("")
        yield Static("[bold]Security & Compliance:[/bold]")
        with Horizontal(id="security-grid"):
            yield ProviderCard("Cloud Custodian", "Ready", id="custodian-card", classes="tool-card")
        
        yield Static("")
        yield Static("[bold]IaC & Automation:[/bold]")
        with Horizontal(id="iac-grid"):
            yield ProviderCard("Ansible", "Ready", id="ansible-card", classes="tool-card")
            yield ProviderCard("Pulumi", "Ready", id="pulumi-card", classes="tool-card")
        
        yield Static("")
        yield Static("[bold]Quick Actions:[/bold]")
        yield Static("  [1] AWS  [2] GCP  [3] Azure")
        yield Static("  [4] Cloud Custodian  [5] Ansible  [6] Pulumi")
        yield Static("  [s] Setup  [?] Help  [q] Quit")

class CloudTekTUI(App):
    """Main TUI application"""
    
    CSS = """
    Screen {
        background: $surface;
    }
    
    #title {
        text-align: center;
        padding: 1;
        background: $primary;
    }
    
    #provider-grid {
        height: auto;
        padding: 1;
        align: center middle;
    }
    
    .provider-card {
        width: 30;
        height: 5;
        border: solid $accent;
        padding: 1;
        margin: 1;
        background: $panel;
    }
    
    .provider-card:hover {
        border: solid $success;
        background: $boost;
    }
    
    .tool-card {
        width: 30;
        height: 5;
        border: solid $primary;
        padding: 1;
        margin: 1;
        background: $panel;
    }
    
    .tool-card:hover {
        border: solid $warning;
        background: $boost;
    }
    """
    
    BINDINGS = [
        Binding("q", "quit", "Quit"),
        Binding("1", "show_aws", "AWS"),
        Binding("2", "show_gcp", "GCP"),
        Binding("3", "show_azure", "Azure"),
        Binding("4", "show_custodian", "Custodian"),
        Binding("5", "show_ansible", "Ansible"),
        Binding("6", "show_pulumi", "Pulumi"),
        Binding("s", "setup", "Setup"),
        Binding("?", "help", "Help"),
    ]
    
    def __init__(self):
        super().__init__()
        self.config = self.load_config()
    
    def compose(self) -> ComposeResult:
        yield Header()
        yield Dashboard()
        yield Footer()
    
    def load_config(self) -> dict:
        """Load or create default configuration"""
        if not CONFIG_FILE.exists():
            default_config = {
                "default_provider": "aws",
                "default_regions": {
                    "aws": "us-east-1",
                    "gcp": "us-central1",
                    "azure": "eastus"
                },
                "aws": {
                    "profile": "default",
                    "regions": ["us-east-1", "us-west-2"]
                },
                "gcp": {
                    "project": "",
                    "regions": ["us-central1", "europe-west1"]
                },
                "azure": {
                    "subscription_id": "",
                    "regions": ["eastus", "westus2"]
                },
                "ui": {
                    "theme": "dark",
                    "refresh_interval": 30
                }
            }
            APP_DIR.mkdir(parents=True, exist_ok=True)
            AWS_CREDS_DIR.mkdir(parents=True, exist_ok=True)
            GCP_CREDS_DIR.mkdir(parents=True, exist_ok=True)
            AZURE_CREDS_DIR.mkdir(parents=True, exist_ok=True)
            
            with open(CONFIG_FILE, 'w') as f:
                yaml.dump(default_config, f, default_flow_style=False)
            return default_config
        
        return yaml.safe_load(CONFIG_FILE.read_text())
    
    def action_show_aws(self) -> None:
        """Show AWS resources screen"""
        self.notify("AWS Resources - Coming soon!")
    
    def action_show_gcp(self) -> None:
        """Show GCP resources screen"""
        self.notify("GCP Resources - Coming soon!")
    
    def action_show_azure(self) -> None:
        """Show Azure resources screen"""
        self.notify("Azure Resources - Coming soon!")
    
    def action_show_custodian(self) -> None:
        """Show Cloud Custodian policy management"""
        self.notify("Cloud Custodian - Policy-as-code (uses AWS/GCP/Azure creds)")
    
    def action_show_ansible(self) -> None:
        """Show Ansible automation"""
        self.notify("Ansible - Automation & configuration management")
    
    def action_show_pulumi(self) -> None:
        """Show Pulumi IaC management"""
        self.notify("Pulumi - Pure Python Infrastructure as Code (local, no account required)")
    
    def action_setup(self) -> None:
        """Show credential setup wizard"""
        setup_text = """
[bold]Credential Setup[/bold]

[bold cyan]Custom Credential Storage:[/bold cyan]
Credentials stored in: ~/.decyphertek.ai/app-store/cloudtek-tui/

[bold cyan]Setup Instructions:[/bold cyan]

[bold]AWS:[/bold]
Edit: ~/.decyphertek.ai/app-store/cloudtek-tui/aws/credentials
[default]
aws_access_key_id = YOUR_ACCESS_KEY
aws_secret_access_key = YOUR_SECRET_KEY

[bold]GCP:[/bold]
Place service account JSON at:
~/.decyphertek.ai/app-store/cloudtek-tui/gcp/application_default_credentials.json

[bold]Azure:[/bold]
Create: ~/.decyphertek.ai/app-store/cloudtek-tui/azure/credentials.json
{
  "tenant_id": "xxx",
  "client_id": "xxx",
  "client_secret": "xxx",
  "subscription_id": "xxx"
}

Restart cloudtek-tui after adding credentials.
        """
        self.notify(setup_text, timeout=15)
    
    def action_help(self) -> None:
        """Show help information"""
        help_text = """
[bold]cloudtek-tui Help[/bold]

[bold cyan]Keyboard Shortcuts:[/bold cyan]
  1 - AWS Resources
  2 - GCP Resources
  3 - Azure Resources
  4 - Cloud Custodian (Policy)
  5 - Ansible (Automation)
  6 - Pulumi (IaC)
  s - Setup Credentials
  ? - This help screen
  q - Quit application

[bold cyan]Configuration:[/bold cyan]
  Config: ~/.decyphertek.ai/app-store/cloudtek-tui/config.yaml
  AWS:    ~/.decyphertek.ai/app-store/cloudtek-tui/aws/
  GCP:    ~/.decyphertek.ai/app-store/cloudtek-tui/gcp/
  Azure:  ~/.decyphertek.ai/app-store/cloudtek-tui/azure/

[bold cyan]Features:[/bold cyan]
  - Pure Python implementation (no CLI dependencies)
  - Isolated credential storage
  - Multi-cloud resource management
  - Policy enforcement (Cloud Custodian)
  - Automation (Ansible)
  - Infrastructure as Code (Pulumi - pure Python, local)
        """
        self.notify(help_text, timeout=10)

def main():
    """Entry point"""
    try:
        app = CloudTekTUI()
        app.run()
    except KeyboardInterrupt:
        print("\n[cloudtek-tui] Exiting...")
        sys.exit(0)
    except Exception as e:
        print(f"[cloudtek-tui] Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
