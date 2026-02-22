"""
AWS Provider - boto3 wrapper with custom credential path
Uses ~/.decyphertek.ai/app-store/cloudtek-tui/aws/ for credentials
"""
import os
import boto3
from pathlib import Path
from typing import Optional, Dict, List

HOME = Path.home()
AWS_CREDS_DIR = HOME / ".decyphertek.ai/app-store/cloudtek-tui/aws"
AWS_CREDENTIALS_FILE = AWS_CREDS_DIR / "credentials"
AWS_CONFIG_FILE = AWS_CREDS_DIR / "config"

class AWSProvider:
    """AWS provider using custom credential path"""
    
    def __init__(self, profile: str = "default", region: str = "us-east-1"):
        self.profile = profile
        self.region = region
        self._setup_credentials()
        self.session = None
        
    def _setup_credentials(self):
        """Set environment variables to use custom credential path"""
        if AWS_CREDENTIALS_FILE.exists():
            os.environ['AWS_SHARED_CREDENTIALS_FILE'] = str(AWS_CREDENTIALS_FILE)
        if AWS_CONFIG_FILE.exists():
            os.environ['AWS_CONFIG_FILE'] = str(AWS_CONFIG_FILE)
    
    def connect(self) -> bool:
        """Initialize boto3 session and test connection"""
        try:
            self.session = boto3.Session(
                profile_name=self.profile,
                region_name=self.region
            )
            sts = self.session.client('sts')
            sts.get_caller_identity()
            return True
        except Exception as e:
            return False
    
    def list_ec2_instances(self) -> List[Dict]:
        """List EC2 instances"""
        if not self.session:
            return []
        
        try:
            ec2 = self.session.client('ec2', region_name=self.region)
            response = ec2.describe_instances()
            
            instances = []
            for reservation in response.get('Reservations', []):
                for instance in reservation.get('Instances', []):
                    instances.append({
                        'id': instance.get('InstanceId'),
                        'type': instance.get('InstanceType'),
                        'state': instance.get('State', {}).get('Name'),
                        'ip': instance.get('PublicIpAddress', 'N/A'),
                        'name': next((tag['Value'] for tag in instance.get('Tags', []) if tag['Key'] == 'Name'), 'N/A')
                    })
            return instances
        except Exception as e:
            return []
    
    def list_s3_buckets(self) -> List[Dict]:
        """List S3 buckets"""
        if not self.session:
            return []
        
        try:
            s3 = self.session.client('s3')
            response = s3.list_buckets()
            
            buckets = []
            for bucket in response.get('Buckets', []):
                buckets.append({
                    'name': bucket.get('Name'),
                    'created': bucket.get('CreationDate')
                })
            return buckets
        except Exception as e:
            return []
    
    def start_instance(self, instance_id: str) -> bool:
        """Start EC2 instance"""
        if not self.session:
            return False
        
        try:
            ec2 = self.session.client('ec2', region_name=self.region)
            ec2.start_instances(InstanceIds=[instance_id])
            return True
        except Exception:
            return False
    
    def stop_instance(self, instance_id: str) -> bool:
        """Stop EC2 instance"""
        if not self.session:
            return False
        
        try:
            ec2 = self.session.client('ec2', region_name=self.region)
            ec2.stop_instances(InstanceIds=[instance_id])
            return True
        except Exception:
            return False

def setup_aws_credentials(access_key: str, secret_key: str, region: str = "us-east-1") -> bool:
    """Setup AWS credentials in custom path"""
    try:
        AWS_CREDS_DIR.mkdir(parents=True, exist_ok=True)
        
        credentials_content = f"""[default]
aws_access_key_id = {access_key}
aws_secret_access_key = {secret_key}
"""
        
        config_content = f"""[default]
region = {region}
output = json
"""
        
        AWS_CREDENTIALS_FILE.write_text(credentials_content)
        AWS_CONFIG_FILE.write_text(config_content)
        
        AWS_CREDENTIALS_FILE.chmod(0o600)
        AWS_CONFIG_FILE.chmod(0o600)
        
        return True
    except Exception:
        return False
