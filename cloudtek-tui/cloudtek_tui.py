#!/usr/bin/env python3
"""
CloudTek - Multi-Cloud Terminal Management System
"""
from pathlib import Path
import subprocess
import json
import yaml
import sys
import os

HOME = Path.home()
APP_DIR = HOME / ".decyphertek.ai/app-store/cloudtek-tui"
AWS_CREDS_DIR = APP_DIR / "aws"
GCP_CREDS_DIR = APP_DIR / "gcp"
AZURE_CREDS_DIR = APP_DIR / "azure"

GREEN = "\033[92m"
CYAN = "\033[96m"
YELLOW = "\033[93m"
RED = "\033[91m"
MAGENTA = "\033[95m"
RESET = "\033[0m"

BANNER = f"""{GREEN}
╔═════════════════════════════════════════════════════════════════╗
║  ██████╗██╗      ██████╗ ██╗   ██╗██████╗ ████████╗███████╗██╗  ██╗ ║
║ ██╔════╝██║     ██╔═══██╗██║   ██║██╔══██╗╚══██╔══╝██╔════╝██║ ██╔╝ ║
║ ██║     ██║     ██║   ██║██║   ██║██║  ██║   ██║   █████╗  █████╔╝  ║
║ ██║     ██║     ██║   ██║██║   ██║██║  ██║   ██║   ██╔══╝  ██╔═██╗  ║
║ ╚██████╗███████╗╚██████╔╝╚██████╔╝██████╔╝   ██║   ███████╗██║  ██╗ ║
║  ╚═════╝╚══════╝ ╚═════╝  ╚═════╝ ╚═════╝    ╚═╝   ╚══════╝╚═╝  ╚═╝ ║
║                                                                   ║{RESET}
{MAGENTA}║                ▓▓▓ CLOUDTEK TERMINAL v1.0 ▓▓▓                    ║{RESET}
{CYAN}║              Multi-Cloud Management System                        ║{RESET}
{GREEN}╚═════════════════════════════════════════════════════════════════╝{RESET}
"""

COMMAND_MAP = {
    "aws": "aws",
    "gcp": "gcloud",
    "azure": "az",
    "custodian": "c7n",
    "pulumi": "pulumi",
    "ansible": "ansible"
}

# Simplified command aliases
SIMPLIFIED_COMMANDS = {
    # AWS simplified commands
    "aws list instances": "aws ec2 describe-instances",
    "aws list buckets": "aws s3 ls",
    "aws list users": "aws iam list-users",
    "aws list roles": "aws iam list-roles",
    "aws list functions": "aws lambda list-functions",
    "aws list databases": "aws rds describe-db-instances",
    "aws start instance": "aws ec2 start-instances --instance-ids",
    "aws stop instance": "aws ec2 stop-instances --instance-ids",
    "aws create bucket": "aws s3 mb s3://",
    "aws delete bucket": "aws s3 rb s3://",
    
    # GCP simplified commands
    "gcp list instances": "gcloud compute instances list",
    "gcp list buckets": "gsutil ls",
    "gcp list functions": "gcloud functions list",
    "gcp list databases": "gcloud sql instances list",
    "gcp start instance": "gcloud compute instances start",
    "gcp stop instance": "gcloud compute instances stop",
    "gcp create bucket": "gsutil mb gs://",
    "gcp delete bucket": "gsutil rb gs://",
    
    # Azure simplified commands
    "azure list vms": "az vm list",
    "azure list storage": "az storage account list",
    "azure list functions": "az functionapp list",
    "azure list databases": "az sql server list",
    "azure start vm": "az vm start --name",
    "azure stop vm": "az vm stop --name",
    "azure create storage": "az storage account create --name",
    "azure delete storage": "az storage account delete --name",
}

def setup_credentials():
    APP_DIR.mkdir(parents=True, exist_ok=True)
    AWS_CREDS_DIR.mkdir(parents=True, exist_ok=True)
    GCP_CREDS_DIR.mkdir(parents=True, exist_ok=True)
    AZURE_CREDS_DIR.mkdir(parents=True, exist_ok=True)
    
    os.environ['AWS_SHARED_CREDENTIALS_FILE'] = str(AWS_CREDS_DIR / "credentials")
    os.environ['AWS_CONFIG_FILE'] = str(AWS_CREDS_DIR / "config")
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = str(GCP_CREDS_DIR / "application_default_credentials.json")

def first_run_setup():
    import shutil
    from getpass import getpass
    
    print(f"\n{CYAN}═══ FIRST RUN SETUP ═══{RESET}\n")
    print(f"{YELLOW}Credential storage: {APP_DIR}{RESET}\n")
    
    # AWS Setup
    print(f"{GREEN}AWS Credentials Setup:{RESET}")
    aws_key = input(f"{CYAN}AWS Access Key ID:{RESET} ").strip()
    print(f"{YELLOW}(Input hidden for security){RESET}")
    aws_secret = getpass(f"{CYAN}AWS Secret Access Key:{RESET} ").strip()
    aws_region = input(f"{CYAN}Default Region [us-east-1]:{RESET} ").strip() or "us-east-1"
    
    if aws_key and aws_secret:
        aws_creds_file = AWS_CREDS_DIR / "credentials"
        aws_config_file = AWS_CREDS_DIR / "config"
        
        with open(aws_creds_file, 'w') as f:
            f.write(f"[default]\n")
            f.write(f"aws_access_key_id = {aws_key}\n")
            f.write(f"aws_secret_access_key = {aws_secret}\n")
        
        with open(aws_config_file, 'w') as f:
            f.write(f"[default]\n")
            f.write(f"region = {aws_region}\n")
        
        print(f"{GREEN}✓ AWS credentials saved{RESET}")
    else:
        print(f"{YELLOW}⚠ Skipped AWS setup{RESET}")
    
    # GCP Setup
    print(f"\n{GREEN}GCP Credentials Setup:{RESET}")
    gcp_json_path = input(f"{CYAN}Path to GCP service account JSON (or press Enter to skip):{RESET} ").strip()
    
    if gcp_json_path and Path(gcp_json_path).exists():
        gcp_dest = GCP_CREDS_DIR / "application_default_credentials.json"
        shutil.copy(gcp_json_path, gcp_dest)
        print(f"{GREEN}✓ GCP credentials saved{RESET}")
    else:
        print(f"{YELLOW}⚠ Skipped GCP setup{RESET}")
    
    # Azure Setup
    print(f"\n{GREEN}Azure Credentials Setup:{RESET}")
    azure_setup = input(f"{CYAN}Run 'az login' now? (y/n):{RESET} ").strip().lower()
    
    if azure_setup == 'y':
        print(f"{YELLOW}Running: az login{RESET}")
        subprocess.run("az login", shell=True)
        print(f"{GREEN}✓ Azure login complete{RESET}")
    else:
        print(f"{YELLOW}⚠ Skipped Azure setup - run 'az login' manually later{RESET}")
    
    print(f"\n{GREEN}Setup complete!{RESET}\n")

def show_help():
    print(f"\n{CYAN}═══ CLOUDTEK SIMPLIFIED COMMANDS ═══{RESET}")
    print(f"\n{GREEN}AWS Commands:{RESET}")
    print(f"  aws list instances  - List EC2 instances")
    print(f"  aws list buckets    - List S3 buckets")
    print(f"  aws list users      - List IAM users")
    print(f"  aws list functions  - List Lambda functions")
    print(f"  aws list databases  - List RDS databases")
    print(f"\n{GREEN}GCP Commands:{RESET}")
    print(f"  gcp list instances  - List Compute instances")
    print(f"  gcp list buckets    - List Cloud Storage buckets")
    print(f"  gcp list functions  - List Cloud Functions")
    print(f"  gcp list databases  - List Cloud SQL databases")
    print(f"\n{GREEN}Azure Commands:{RESET}")
    print(f"  azure list vms      - List Virtual Machines")
    print(f"  azure list storage  - List Storage accounts")
    print(f"  azure list functions - List Function apps")
    print(f"  azure list databases - List SQL servers")
    print(f"\n{GREEN}Tools:{RESET}")
    print(f"  custodian <command> - Cloud Custodian")
    print(f"  pulumi <command>    - Pulumi IaC")
    print(f"  ansible <command>   - Ansible")
    print(f"\n{GREEN}System:{RESET}")
    print(f"  help  - Show this help")
    print(f"  exit  - Exit CloudTek")
    print(f"\n{YELLOW}All other commands pass through like a normal terminal{RESET}\n")

def execute_command(cmd):
    cmd_lower = cmd.lower().strip()
    
    # Intercept help commands
    if cmd_lower == "aws help":
        print(f"\n{CYAN}AWS SIMPLIFIED COMMANDS:{RESET}")
        print(f"  aws list instances/buckets/users/functions/databases")
        print(f"  aws start/stop instance <id>")
        print(f"  aws create/delete bucket <name>\n")
        return
    elif cmd_lower == "gcp help":
        print(f"\n{CYAN}GCP SIMPLIFIED COMMANDS:{RESET}")
        print(f"  gcp list instances/buckets/functions/databases")
        print(f"  gcp start/stop instance <name>")
        print(f"  gcp create/delete bucket <name>\n")
        return
    elif cmd_lower == "azure help":
        print(f"\n{CYAN}AZURE SIMPLIFIED COMMANDS:{RESET}")
        print(f"  azure list vms/storage/functions/databases")
        print(f"  azure start/stop vm <name>")
        print(f"  azure create/delete storage <name>\n")
        return
    
    # Check for simplified commands
    actual_cmd = None
    for simple_cmd, real_cmd in SIMPLIFIED_COMMANDS.items():
        if cmd_lower.startswith(simple_cmd):
            extra_args = cmd[len(simple_cmd):].strip()
            actual_cmd = f"{real_cmd} {extra_args}".strip()
            break
    
    # If no simplified command matched, check for base command aliases
    if not actual_cmd:
        parts = cmd.split(maxsplit=1)
        if not parts:
            return
        
        base_cmd = parts[0]
        args = parts[1] if len(parts) > 1 else ""
        
        if base_cmd in COMMAND_MAP:
            actual_cmd = f"{COMMAND_MAP[base_cmd]} {args}"
        else:
            # Pass through all other commands
            actual_cmd = cmd
    
    try:
        result = subprocess.run(actual_cmd, shell=True, capture_output=True, text=True, timeout=30)
        if result.stdout:
            # Try to format as YAML for cloud commands
            if any(cmd_lower.startswith(prefix) for prefix in ["aws", "gcp", "azure", "custodian"]):
                try:
                    data = json.loads(result.stdout)
                    print(f"{GREEN}{yaml.dump(data, default_flow_style=False, sort_keys=False)}{RESET}")
                except:
                    print(result.stdout)
            else:
                print(result.stdout)
        if result.stderr:
            print(f"{RED}{result.stderr}{RESET}")
    except subprocess.TimeoutExpired:
        print(f"{RED}Command timed out{RESET}")
    except Exception as e:
        print(f"{RED}Error: {e}{RESET}")

def main():
    setup_credentials()
    print(BANNER)
    
    if not (AWS_CREDS_DIR / "credentials").exists():
        first_run_setup()
    
    print(f"{GREEN}CloudTek initialized. Type 'help' for commands.{RESET}\n")
    
    while True:
        try:
            cmd = input(f"{CYAN}cloudtek>{RESET} ").strip()
            if not cmd:
                continue
            if cmd == "exit":
                print(f"{GREEN}Goodbye!{RESET}")
                break
            elif cmd == "help":
                show_help()
            else:
                execute_command(cmd)
        except KeyboardInterrupt:
            print(f"\n{GREEN}Goodbye!{RESET}")
            break
        except EOFError:
            break

if __name__ == "__main__":
    main()

