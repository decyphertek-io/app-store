"""
GCP Provider - google-cloud wrapper with custom credential path
Uses ~/.decyphertek.ai/app-store/cloudtek-tui/gcp/ for credentials
"""
import os
import json
from pathlib import Path
from typing import Optional, Dict, List

HOME = Path.home()
GCP_CREDS_DIR = HOME / ".decyphertek.ai/app-store/cloudtek-tui/gcp"
GCP_CREDENTIALS_FILE = GCP_CREDS_DIR / "application_default_credentials.json"

class GCPProvider:
    """GCP provider using custom credential path"""
    
    def __init__(self, project_id: str = "", region: str = "us-central1"):
        self.project_id = project_id
        self.region = region
        self.zone = f"{region}-a"
        self._setup_credentials()
        self.compute_client = None
        self.storage_client = None
    
    def _setup_credentials(self):
        """Set environment variable to use custom credential path"""
        if GCP_CREDENTIALS_FILE.exists():
            os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = str(GCP_CREDENTIALS_FILE)
            if not self.project_id:
                try:
                    creds = json.loads(GCP_CREDENTIALS_FILE.read_text())
                    self.project_id = creds.get('project_id', '')
                except Exception:
                    pass
    
    def connect(self) -> bool:
        """Initialize GCP clients and test connection"""
        try:
            from google.cloud import compute_v1
            from google.cloud import storage
            
            self.compute_client = compute_v1.InstancesClient()
            self.storage_client = storage.Client(project=self.project_id)
            
            list(self.storage_client.list_buckets(max_results=1))
            return True
        except Exception:
            return False
    
    def list_compute_instances(self) -> List[Dict]:
        """List Compute Engine instances"""
        if not self.compute_client or not self.project_id:
            return []
        
        try:
            from google.cloud import compute_v1
            
            request = compute_v1.AggregatedListInstancesRequest(
                project=self.project_id
            )
            
            instances = []
            agg_list = self.compute_client.aggregated_list(request=request)
            
            for zone, response in agg_list:
                if response.instances:
                    for instance in response.instances:
                        instances.append({
                            'id': instance.id,
                            'name': instance.name,
                            'type': instance.machine_type.split('/')[-1],
                            'state': instance.status,
                            'zone': instance.zone.split('/')[-1]
                        })
            return instances
        except Exception:
            return []
    
    def list_storage_buckets(self) -> List[Dict]:
        """List Cloud Storage buckets"""
        if not self.storage_client:
            return []
        
        try:
            buckets = []
            for bucket in self.storage_client.list_buckets():
                buckets.append({
                    'name': bucket.name,
                    'location': bucket.location,
                    'created': bucket.time_created
                })
            return buckets
        except Exception:
            return []
    
    def start_instance(self, instance_name: str, zone: str) -> bool:
        """Start Compute Engine instance"""
        if not self.compute_client or not self.project_id:
            return False
        
        try:
            from google.cloud import compute_v1
            
            request = compute_v1.StartInstanceRequest(
                project=self.project_id,
                zone=zone,
                instance=instance_name
            )
            self.compute_client.start(request=request)
            return True
        except Exception:
            return False
    
    def stop_instance(self, instance_name: str, zone: str) -> bool:
        """Stop Compute Engine instance"""
        if not self.compute_client or not self.project_id:
            return False
        
        try:
            from google.cloud import compute_v1
            
            request = compute_v1.StopInstanceRequest(
                project=self.project_id,
                zone=zone,
                instance=instance_name
            )
            self.compute_client.stop(request=request)
            return True
        except Exception:
            return False

def setup_gcp_credentials(credentials_json: str) -> bool:
    """Setup GCP credentials in custom path"""
    try:
        GCP_CREDS_DIR.mkdir(parents=True, exist_ok=True)
        
        creds = json.loads(credentials_json)
        
        GCP_CREDENTIALS_FILE.write_text(json.dumps(creds, indent=2))
        GCP_CREDENTIALS_FILE.chmod(0o600)
        
        return True
    except Exception:
        return False
