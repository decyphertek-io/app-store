# cloudtek-tui Architecture

## Overview
CloudTek is a traditional terminal interface for multi-cloud management (AWS, GCP, Azure) with simplified commands. First-run setup wizard configures credentials automatically. Built as standalone PyInstaller executable.

## Design Principles
- **Traditional Terminal**: Standard terminal I/O (input/print), NOT TUI widgets
- **Simplified Commands**: `aws`, `gcp`, `azure`, `custodian`, `pulumi`, `ansible` (easier to remember)
- **First-Run Setup**: Interactive wizard saves credentials to `~/.decyphertek.ai/app-store/cloudtek-tui/`
- **Auto-Configuration**: Sets environment paths so CLI tools use custom credential locations
- **Nice Output**: Pretty JSON formatting, colored output, tables
- **Standalone Binary**: Single executable via PyInstaller, no Python runtime required

## Technology Stack
- **Language**: Python 3.13
- **Interface**: Traditional terminal (input/print with ANSI colors)
- **Package Manager**: UV (no pyproject.toml needed)
- **Bundler**: PyInstaller 6.19.0 (--onefile)
- **Cloud CLI Tools**:
  - AWS: awscli (called via subprocess)
  - GCP: gcloud (called via subprocess)
  - Azure: az CLI (called via subprocess)
- **Security/Compliance Tools**:
  - Cloud Custodian: c7n (policy-as-code for cloud governance)
- **IaC Tools**:
  - Ansible: ansible-core (automation and configuration)
  - Pulumi: pulumi (pure Python IaC, local, no account required)

## Simplified Command Mapping

CloudTek uses simplified commands that map to actual CLI tools:

| Simplified Command | Maps To | Description |
|-------------------|---------|-------------|
| `aws <args>` | `aws <args>` | AWS CLI commands |
| `gcp <args>` | `gcloud <args>` | Google Cloud CLI commands |
| `azure <args>` | `az <args>` | Azure CLI commands |
| `custodian <args>` | `c7n <args>` | Cloud Custodian policy commands |
| `pulumi <args>` | `pulumi <args>` | Pulumi IaC commands |
| `ansible <args>` | `ansible <args>` | Ansible automation commands |

## First-Run Setup Flow

1. Launch CloudTek executable
2. Check if credentials exist at `~/.decyphertek.ai/app-store/cloudtek-tui/`
3. If not found → Run interactive setup wizard:
   - Prompt for AWS credentials (access key, secret key)
   - Prompt for GCP service account JSON path
   - Prompt for Azure login
4. Save credentials to custom directory
5. Set environment variables:
   - `AWS_SHARED_CREDENTIALS_FILE`
   - `AWS_CONFIG_FILE`
   - `GOOGLE_APPLICATION_CREDENTIALS`
6. Display CloudTek banner
7. Drop to terminal prompt: `cloudtek>`

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    cloudtek-tui.app                          │
├─────────────────────────────────────────────────────────────┤
│  Textual TUI Layer                                           │
│  ├─ Dashboard Screen                                         │
│  ├─ Cloud Provider Screens (AWS/GCP/Azure)                   │
│  └─ Tool Screens (Custodian/Ansible/Pulumi)                  │
├─────────────────────────────────────────────────────────────┤
│  Provider Abstraction Layer                                  │
│  ├─ AWS Provider (boto3)                                     │
│  ├─ GCP Provider (google-cloud-*)                            │
│  └─ Azure Provider (azure-mgmt-*)                            │
├─────────────────────────────────────────────────────────────┤
│  Tool Integration Layer                                      │
│  ├─ Cloud Custodian (uses AWS/GCP/Azure credentials)         │
│  ├─ Ansible (separate inventory/playbook management)         │
│  └─ Pulumi (pure Python IaC, local state)                    │
├─────────────────────────────────────────────────────────────┤
│  Core Services                                               │
│  ├─ Configuration Manager                                    │
│  ├─ Credential Manager (shared across tools)                 │
│  └─ Cache Layer (in-memory for API responses)                │
└─────────────────────────────────────────────────────────────┘
```

## Directory Structure

### Development Structure
```
cloudtek-tui/
├── build.sh                    # UV + PyInstaller build script
├── cloudtek_tui.py             # Main entry point
├── ARCHITECTURE.md             # This file
├── CLI_COMMANDS.md             # Command mapping reference
├── providers/
│   ├── aws.py                  # AWS boto3 wrapper
│   ├── gcp.py                  # GCP SDK wrapper
│   ├── azure.py                # Azure SDK wrapper
│   ├── custodian.py            # Cloud Custodian wrapper
│   ├── ansible_provider.py     # Ansible automation
│   └── pulumi_provider.py      # Pulumi IaC wrapper
├── screens/
│   ├── dashboard.py            # Main dashboard
│   ├── aws_screen.py           # AWS resource management
│   ├── gcp_screen.py           # GCP resource management
│   ├── azure_screen.py         # Azure resource management
│   ├── custodian_screen.py     # Policy management
│   ├── ansible_screen.py       # Playbook execution
│   └── pulumi_screen.py        # Pulumi IaC management
└── dist/
    └── cloudtek-tui.app        # Built executable
```

### Runtime Structure (User's Home Directory)
```
~/.decyphertek.ai/
└── app-store/
    └── cloudtek-tui/
        ├── config.yaml         # Application configuration
        ├── aws/
        │   ├── credentials     # AWS credentials (standard format)
        │   └── config          # AWS config (standard format)
        ├── gcp/
        │   └── application_default_credentials.json
        └── azure/
            └── credentials.json
```

## Provider Implementation

### AWS Provider (awscli)
```python
# Uses custom credential path: ~/.decyphertek.ai/app-store/cloudtek-tui/aws/
# Calls AWS CLI via subprocess

import subprocess
import os
from pathlib import Path

AWS_CREDS_DIR = Path.home() / ".decyphertek.ai/app-store/cloudtek-tui/aws"
os.environ['AWS_SHARED_CREDENTIALS_FILE'] = str(AWS_CREDS_DIR / "credentials")
os.environ['AWS_CONFIG_FILE'] = str(AWS_CREDS_DIR / "config")

# List EC2 instances
result = subprocess.run(
    ['aws', 'ec2', 'describe-instances', '--region', 'us-east-1'],
    capture_output=True, text=True
)
```

### GCP Provider (gcloud)
```python
# Uses custom credential path: ~/.decyphertek.ai/app-store/cloudtek-tui/gcp/
# Calls gcloud CLI via subprocess

import subprocess
import os
from pathlib import Path

GCP_CREDS_FILE = Path.home() / ".decyphertek.ai/app-store/cloudtek-tui/gcp/application_default_credentials.json"
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = str(GCP_CREDS_FILE)

# List Compute Engine instances
result = subprocess.run(
    ['gcloud', 'compute', 'instances', 'list', '--format=json'],
    capture_output=True, text=True
)
```

### Azure Provider (azure-cli)
```python
# Uses custom credential path: ~/.decyphertek.ai/app-store/cloudtek-tui/azure/
# Calls Azure CLI via subprocess

import subprocess
import json
from pathlib import Path

AZURE_CREDS_FILE = Path.home() / ".decyphertek.ai/app-store/cloudtek-tui/azure/credentials.json"

# Azure CLI uses service principal login
# az login --service-principal -u <client-id> -p <client-secret> --tenant <tenant-id>

# List VMs
result = subprocess.run(
    ['az', 'vm', 'list', '--output', 'json'],
    capture_output=True, text=True
)
```

## Core Features

### 1. VM Management
- **List VMs**: Display running instances across all providers
- **Start/Stop**: Control VM power state
- **SSH Info**: Show connection details
- **Create VM**: Launch new instances with templates

### 2. Storage Management
- **List Buckets/Containers**: Show storage resources
- **Upload/Download**: File operations
- **Permissions**: Manage access controls

### 3. Network Management
- **List VPCs/VNets**: Show network topology
- **Security Groups**: Manage firewall rules
- **Load Balancers**: View and configure

### 4. IAM Management
- **List Users/Roles**: Identity overview
- **Permissions**: View and modify access
- **Service Accounts**: Manage automation credentials

## Configuration

### Config File: `~/.decyphertek.ai/app-store/cloudtek-tui/config.yaml`
```yaml
default_provider: aws
default_regions:
  aws: us-east-1
  gcp: us-central1
  azure: eastus

aws:
  profile: default
  regions:
    - us-east-1
    - us-west-2

gcp:
  project: my-project-id
  regions:
    - us-central1
    - europe-west1

azure:
  subscription_id: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
  regions:
    - eastus
    - westus2

ui:
  theme: dark
  refresh_interval: 30
```

## Build Process

### build.sh Workflow
```bash
1. Check/install UV
2. Create clean venv with Python 3.13
3. Install dependencies: textual boto3 google-cloud-* azure-* pyinstaller
4. Clean previous builds
5. Run PyInstaller with --onefile
6. Remove .venv, build/, *.spec
7. Output: dist/cloudtek-tui.app
```

### PyInstaller Configuration
- **--onefile**: Single executable
- **--clean**: Remove temp files
- **--hidden-import**: Include cloud SDK modules
- **--collect-all**: Bundle provider packages

## Credential Management

### Custom Credential Storage
- **Isolated credentials**: Stored in `~/.decyphertek.ai/app-store/cloudtek-tui/`
- **Standard formats**: Follows AWS/GCP/Azure credential file formats
- **No system pollution**: Doesn't interfere with system-wide CLI configs
- **Secure permissions**: Files created with 0600 permissions

### Credential File Formats

**AWS** (`~/.decyphertek.ai/app-store/cloudtek-tui/aws/credentials`):
```ini
[default]
aws_access_key_id = AKIAIOSFODNN7EXAMPLE
aws_secret_access_key = wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
```

**AWS Config** (`~/.decyphertek.ai/app-store/cloudtek-tui/aws/config`):
```ini
[default]
region = us-east-1
output = json
```

**GCP** (`~/.decyphertek.ai/app-store/cloudtek-tui/gcp/application_default_credentials.json`):
```json
{
  "type": "service_account",
  "project_id": "my-project",
  "private_key_id": "key-id",
  "private_key": "-----BEGIN PRIVATE KEY-----\n...",
  "client_email": "service-account@project.iam.gserviceaccount.com",
  "client_id": "123456789",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token"
}
```

**Azure** (`~/.decyphertek.ai/app-store/cloudtek-tui/azure/credentials.json`):
```json
{
  "tenant_id": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
  "client_id": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
  "client_secret": "your-client-secret",
  "subscription_id": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
}
```

### Setup Workflow
TUI includes interactive setup wizard:
1. First run detects missing credentials
2. Prompts for provider selection (AWS/GCP/Azure)
3. Guides through credential input
4. Creates properly formatted credential files
5. Sets correct file permissions (0600)
6. Validates credentials with test API call

## TUI Navigation

### Keyboard Shortcuts
- `1-3`: Switch provider (1=AWS, 2=GCP, 3=Azure)
- `Tab`: Navigate panels
- `Enter`: Select/Execute
- `r`: Refresh current view
- `q`: Quit
- `/`: Search/Filter
- `?`: Help

### Screen Flow
```
Dashboard → Provider Selection → Resource Type → Resource List → Actions
    ↑                                                               ↓
    └─────────────────── Back (Esc) ──────────────────────────────┘
```

## Extension Points

### Future Integrations
- Cloud Custodian: Policy compliance checking
- Ansible: Playbook execution from TUI
- OpenTofu: IaC state management
- Decyphertek AI: MCP server integration (no hardcoding)

### Plugin Architecture (Future)
- Provider interface for new clouds
- Action hooks for custom commands
- Theme system for UI customization

## Performance Considerations

### Caching Strategy
- Cache API responses for 30s (configurable)
- Lazy load resources on demand
- Async operations via Textual workers
- Pagination for large result sets

### Binary Size Optimization
- Exclude unused SDK modules
- UPX compression
- Lazy imports where possible
- Target size: <100MB per platform

## Error Handling

### User-Friendly Errors
- **No credentials**: Show setup instructions
- **API errors**: Display provider error messages
- **Network issues**: Retry with exponential backoff
- **Invalid input**: Inline validation feedback

## Testing Strategy

### Manual Testing
- Test on clean system without credentials
- Verify credential chain detection
- Test all CRUD operations per provider
- Cross-platform binary testing (Linux, macOS, Windows)

### Validation
- No system CLI calls (pure Python only)
- Clean build leaves no artifacts
- Binary runs without Python installed
- All provider SDKs bundled correctly
