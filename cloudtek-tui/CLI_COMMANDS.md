# CLI Commands Mapping

This document maps common AWS, GCP, and Azure CLI commands to their Python SDK equivalents and TUI actions in cloudtek-tui.

## AWS Commands → boto3 SDK

### EC2 (Compute)

| CLI Command | boto3 Equivalent | TUI Action |
|-------------|------------------|------------|
| `aws ec2 describe-instances` | `ec2.describe_instances()` | List VMs |
| `aws ec2 start-instances --instance-ids i-xxx` | `ec2.start_instances(InstanceIds=['i-xxx'])` | Start VM |
| `aws ec2 stop-instances --instance-ids i-xxx` | `ec2.stop_instances(InstanceIds=['i-xxx'])` | Stop VM |
| `aws ec2 terminate-instances --instance-ids i-xxx` | `ec2.terminate_instances(InstanceIds=['i-xxx'])` | Delete VM |
| `aws ec2 run-instances --image-id ami-xxx` | `ec2.run_instances(ImageId='ami-xxx', ...)` | Create VM |
| `aws ec2 describe-images --owners self` | `ec2.describe_images(Owners=['self'])` | List AMIs |
| `aws ec2 describe-security-groups` | `ec2.describe_security_groups()` | List Security Groups |
| `aws ec2 describe-key-pairs` | `ec2.describe_key_pairs()` | List SSH Keys |
| `aws ec2 describe-vpcs` | `ec2.describe_vpcs()` | List VPCs |
| `aws ec2 describe-subnets` | `ec2.describe_subnets()` | List Subnets |

### S3 (Storage)

| CLI Command | boto3 Equivalent | TUI Action |
|-------------|------------------|------------|
| `aws s3 ls` | `s3.list_buckets()` | List Buckets |
| `aws s3 ls s3://bucket-name` | `s3.list_objects_v2(Bucket='bucket-name')` | List Objects |
| `aws s3 cp file.txt s3://bucket/` | `s3.upload_file('file.txt', 'bucket', 'file.txt')` | Upload File |
| `aws s3 cp s3://bucket/file.txt .` | `s3.download_file('bucket', 'file.txt', 'file.txt')` | Download File |
| `aws s3 mb s3://bucket-name` | `s3.create_bucket(Bucket='bucket-name')` | Create Bucket |
| `aws s3 rb s3://bucket-name` | `s3.delete_bucket(Bucket='bucket-name')` | Delete Bucket |

### IAM (Identity)

| CLI Command | boto3 Equivalent | TUI Action |
|-------------|------------------|------------|
| `aws iam list-users` | `iam.list_users()` | List Users |
| `aws iam list-roles` | `iam.list_roles()` | List Roles |
| `aws iam list-policies` | `iam.list_policies()` | List Policies |
| `aws iam get-user --user-name xxx` | `iam.get_user(UserName='xxx')` | View User |
| `aws iam create-user --user-name xxx` | `iam.create_user(UserName='xxx')` | Create User |
| `aws iam delete-user --user-name xxx` | `iam.delete_user(UserName='xxx')` | Delete User |

### Lambda (Functions)

| CLI Command | boto3 Equivalent | TUI Action |
|-------------|------------------|------------|
| `aws lambda list-functions` | `lambda_client.list_functions()` | List Functions |
| `aws lambda invoke --function-name xxx` | `lambda_client.invoke(FunctionName='xxx')` | Invoke Function |
| `aws lambda get-function --function-name xxx` | `lambda_client.get_function(FunctionName='xxx')` | View Function |

### RDS (Databases)

| CLI Command | boto3 Equivalent | TUI Action |
|-------------|------------------|------------|
| `aws rds describe-db-instances` | `rds.describe_db_instances()` | List DB Instances |
| `aws rds start-db-instance --db-instance-id xxx` | `rds.start_db_instance(DBInstanceIdentifier='xxx')` | Start Database |
| `aws rds stop-db-instance --db-instance-id xxx` | `rds.stop_db_instance(DBInstanceIdentifier='xxx')` | Stop Database |

---

## GCP Commands → google-cloud SDK

### Compute Engine (VMs)

| CLI Command | google-cloud Equivalent | TUI Action |
|-------------|------------------------|------------|
| `gcloud compute instances list` | `compute_v1.InstancesClient().list(project, zone)` | List VMs |
| `gcloud compute instances start vm-name` | `instances_client.start(project, zone, instance)` | Start VM |
| `gcloud compute instances stop vm-name` | `instances_client.stop(project, zone, instance)` | Stop VM |
| `gcloud compute instances delete vm-name` | `instances_client.delete(project, zone, instance)` | Delete VM |
| `gcloud compute instances create vm-name` | `instances_client.insert(project, zone, instance_resource)` | Create VM |
| `gcloud compute images list` | `images_client.list(project)` | List Images |
| `gcloud compute networks list` | `networks_client.list(project)` | List Networks |
| `gcloud compute firewall-rules list` | `firewalls_client.list(project)` | List Firewall Rules |

### Cloud Storage (Buckets)

| CLI Command | google-cloud Equivalent | TUI Action |
|-------------|------------------------|------------|
| `gsutil ls` | `storage.Client().list_buckets()` | List Buckets |
| `gsutil ls gs://bucket-name` | `bucket.list_blobs()` | List Objects |
| `gsutil cp file.txt gs://bucket/` | `bucket.blob('file.txt').upload_from_filename('file.txt')` | Upload File |
| `gsutil cp gs://bucket/file.txt .` | `blob.download_to_filename('file.txt')` | Download File |
| `gsutil mb gs://bucket-name` | `storage_client.create_bucket('bucket-name')` | Create Bucket |
| `gsutil rb gs://bucket-name` | `bucket.delete()` | Delete Bucket |

### IAM (Identity)

| CLI Command | google-cloud Equivalent | TUI Action |
|-------------|------------------------|------------|
| `gcloud iam service-accounts list` | `iam.ServiceAccountsClient().list_service_accounts(project)` | List Service Accounts |
| `gcloud iam roles list` | `iam.RolesClient().list_roles(parent)` | List Roles |
| `gcloud projects get-iam-policy PROJECT` | `resourcemanager.ProjectsClient().get_iam_policy(resource)` | View IAM Policy |

### Cloud Functions

| CLI Command | google-cloud Equivalent | TUI Action |
|-------------|------------------------|------------|
| `gcloud functions list` | `functions_v1.CloudFunctionsServiceClient().list_functions(parent)` | List Functions |
| `gcloud functions call function-name` | `functions_client.call_function(name)` | Invoke Function |
| `gcloud functions describe function-name` | `functions_client.get_function(name)` | View Function |

### Cloud SQL (Databases)

| CLI Command | google-cloud Equivalent | TUI Action |
|-------------|------------------------|------------|
| `gcloud sql instances list` | `sqladmin_v1.SqlInstancesServiceClient().list(project)` | List DB Instances |
| `gcloud sql instances patch instance-name` | `sql_client.patch(project, instance, body)` | Update Instance |

---

## Azure Commands → azure-mgmt SDK

### Virtual Machines (Compute)

| CLI Command | azure-mgmt Equivalent | TUI Action |
|-------------|----------------------|------------|
| `az vm list` | `compute_client.virtual_machines.list_all()` | List VMs |
| `az vm start --name vm-name --resource-group rg` | `compute_client.virtual_machines.begin_start(rg, vm_name)` | Start VM |
| `az vm stop --name vm-name --resource-group rg` | `compute_client.virtual_machines.begin_power_off(rg, vm_name)` | Stop VM |
| `az vm delete --name vm-name --resource-group rg` | `compute_client.virtual_machines.begin_delete(rg, vm_name)` | Delete VM |
| `az vm create --name vm-name --resource-group rg` | `compute_client.virtual_machines.begin_create_or_update(rg, vm_name, params)` | Create VM |
| `az vm image list` | `compute_client.virtual_machine_images.list(location, publisher, offer, sku)` | List Images |
| `az network vnet list` | `network_client.virtual_networks.list_all()` | List VNets |
| `az network nsg list` | `network_client.network_security_groups.list_all()` | List NSGs |

### Storage (Blobs)

| CLI Command | azure-mgmt Equivalent | TUI Action |
|-------------|----------------------|------------|
| `az storage account list` | `storage_client.storage_accounts.list()` | List Storage Accounts |
| `az storage container list` | `blob_service_client.list_containers()` | List Containers |
| `az storage blob list --container-name xxx` | `container_client.list_blobs()` | List Blobs |
| `az storage blob upload --file file.txt` | `blob_client.upload_blob(data)` | Upload File |
| `az storage blob download --name file.txt` | `blob_client.download_blob()` | Download File |
| `az storage account create` | `storage_client.storage_accounts.begin_create(rg, account_name, params)` | Create Storage Account |

### Azure AD (Identity)

| CLI Command | azure-mgmt Equivalent | TUI Action |
|-------------|----------------------|------------|
| `az ad user list` | `graph_client.users.list()` | List Users |
| `az ad sp list` | `graph_client.service_principals.list()` | List Service Principals |
| `az role assignment list` | `authorization_client.role_assignments.list()` | List Role Assignments |
| `az ad user show --id xxx` | `graph_client.users.get(user_id)` | View User |

### Azure Functions

| CLI Command | azure-mgmt Equivalent | TUI Action |
|-------------|----------------------|------------|
| `az functionapp list` | `web_client.web_apps.list()` | List Function Apps |
| `az functionapp show --name xxx` | `web_client.web_apps.get(rg, name)` | View Function App |

### Azure SQL (Databases)

| CLI Command | azure-mgmt Equivalent | TUI Action |
|-------------|----------------------|------------|
| `az sql server list` | `sql_client.servers.list()` | List SQL Servers |
| `az sql db list --server xxx` | `sql_client.databases.list_by_server(rg, server)` | List Databases |

---

## Common TUI Actions Summary

### Core Operations Across All Providers

| Action | AWS | GCP | Azure |
|--------|-----|-----|-------|
| **List VMs** | EC2 describe_instances | Compute instances.list | VM list |
| **Start VM** | EC2 start_instances | Compute instances.start | VM begin_start |
| **Stop VM** | EC2 stop_instances | Compute instances.stop | VM begin_power_off |
| **Create VM** | EC2 run_instances | Compute instances.insert | VM begin_create_or_update |
| **Delete VM** | EC2 terminate_instances | Compute instances.delete | VM begin_delete |
| **List Storage** | S3 list_buckets | Storage list_buckets | Storage accounts.list |
| **Upload File** | S3 upload_file | Blob upload_from_filename | Blob upload_blob |
| **Download File** | S3 download_file | Blob download_to_filename | Blob download_blob |
| **List Users** | IAM list_users | IAM list_service_accounts | AD users.list |
| **List Networks** | EC2 describe_vpcs | Compute networks.list | Network vnets.list_all |

---

## TUI Implementation Priority

### Phase 1: Core VM Management
- List all VMs across providers
- Start/Stop VMs
- View VM details (IP, status, size)
- SSH connection info

### Phase 2: Storage Operations
- List buckets/containers
- Browse objects/blobs
- Upload/download files
- Create/delete buckets

### Phase 3: Network & Security
- List VPCs/VNets/Networks
- View security groups/NSGs/firewall rules
- Display network topology

### Phase 4: Identity & Access
- List users/service accounts
- View roles and permissions
- Manage access policies

### Phase 5: Advanced Services
- Serverless functions (Lambda/Cloud Functions/Azure Functions)
- Databases (RDS/Cloud SQL/Azure SQL)
- Load balancers
- Monitoring & logs

---

## Python SDK Dependencies

### Required Packages for build.sh

```bash
# AWS
boto3

# GCP
google-cloud-compute
google-cloud-storage
google-cloud-iam
google-cloud-resource-manager

# Azure
azure-identity
azure-mgmt-compute
azure-mgmt-storage
azure-mgmt-network
azure-mgmt-resource

# TUI
textual

# Build
pyinstaller
```

### Hidden Imports for PyInstaller

```bash
--hidden-import boto3
--hidden-import botocore
--hidden-import google.cloud.compute_v1
--hidden-import google.cloud.storage
--hidden-import azure.mgmt.compute
--hidden-import azure.mgmt.storage
--hidden-import azure.identity
```
