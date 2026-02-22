"""
Azure Provider - azure-mgmt wrapper with custom credential path
Uses ~/.decyphertek.ai/app-store/cloudtek-tui/azure/ for credentials
"""
import json
from pathlib import Path
from typing import Optional, Dict, List

HOME = Path.home()
AZURE_CREDS_DIR = HOME / ".decyphertek.ai/app-store/cloudtek-tui/azure"
AZURE_CREDENTIALS_FILE = AZURE_CREDS_DIR / "credentials.json"

class AzureProvider:
    """Azure provider using custom credential path"""
    
    def __init__(self, subscription_id: str = "", region: str = "eastus"):
        self.subscription_id = subscription_id
        self.region = region
        self.credentials = None
        self.credential = None
        self._load_credentials()
        self.compute_client = None
        self.storage_client = None
    
    def _load_credentials(self):
        """Load credentials from custom path"""
        if AZURE_CREDENTIALS_FILE.exists():
            try:
                self.credentials = json.loads(AZURE_CREDENTIALS_FILE.read_text())
                if not self.subscription_id:
                    self.subscription_id = self.credentials.get('subscription_id', '')
            except Exception:
                pass
    
    def connect(self) -> bool:
        """Initialize Azure clients and test connection"""
        if not self.credentials:
            return False
        
        try:
            from azure.identity import ClientSecretCredential
            from azure.mgmt.compute import ComputeManagementClient
            from azure.mgmt.storage import StorageManagementClient
            
            self.credential = ClientSecretCredential(
                tenant_id=self.credentials['tenant_id'],
                client_id=self.credentials['client_id'],
                client_secret=self.credentials['client_secret']
            )
            
            self.compute_client = ComputeManagementClient(
                self.credential,
                self.subscription_id
            )
            
            self.storage_client = StorageManagementClient(
                self.credential,
                self.subscription_id
            )
            
            list(self.compute_client.virtual_machines.list_all())
            return True
        except Exception:
            return False
    
    def list_virtual_machines(self) -> List[Dict]:
        """List Azure Virtual Machines"""
        if not self.compute_client:
            return []
        
        try:
            vms = []
            for vm in self.compute_client.virtual_machines.list_all():
                vms.append({
                    'id': vm.id,
                    'name': vm.name,
                    'type': vm.hardware_profile.vm_size,
                    'location': vm.location,
                    'state': 'running'
                })
            return vms
        except Exception:
            return []
    
    def list_storage_accounts(self) -> List[Dict]:
        """List Azure Storage Accounts"""
        if not self.storage_client:
            return []
        
        try:
            accounts = []
            for account in self.storage_client.storage_accounts.list():
                accounts.append({
                    'name': account.name,
                    'location': account.location,
                    'kind': account.kind
                })
            return accounts
        except Exception:
            return []
    
    def start_vm(self, resource_group: str, vm_name: str) -> bool:
        """Start Azure VM"""
        if not self.compute_client:
            return False
        
        try:
            self.compute_client.virtual_machines.begin_start(
                resource_group,
                vm_name
            )
            return True
        except Exception:
            return False
    
    def stop_vm(self, resource_group: str, vm_name: str) -> bool:
        """Stop Azure VM"""
        if not self.compute_client:
            return False
        
        try:
            self.compute_client.virtual_machines.begin_power_off(
                resource_group,
                vm_name
            )
            return True
        except Exception:
            return False

def setup_azure_credentials(tenant_id: str, client_id: str, client_secret: str, subscription_id: str) -> bool:
    """Setup Azure credentials in custom path"""
    try:
        AZURE_CREDS_DIR.mkdir(parents=True, exist_ok=True)
        
        credentials = {
            "tenant_id": tenant_id,
            "client_id": client_id,
            "client_secret": client_secret,
            "subscription_id": subscription_id
        }
        
        AZURE_CREDENTIALS_FILE.write_text(json.dumps(credentials, indent=2))
        AZURE_CREDENTIALS_FILE.chmod(0o600)
        
        return True
    except Exception:
        return False
