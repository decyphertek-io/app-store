#!/usr/bin/env python3
"""
cloudtek — Multi-cloud VM lifecycle (AWS, GCP, Azure) via Apache libcloud.
No cloud CLIs required for API calls. Headless CLI for agents / PyInstaller.
Skills: libcloud (GCP/AWS/Azure), Ansible playbooks.
Credentials: Bitwarden (`bw`) and/or ~/.cloudtek/.bw-creds (fallback ~/.claw-vm/.bw-creds).
"""
import os
import sys
import json
import time
import yaml
import tempfile
import subprocess
import argparse
from pathlib import Path


def get_resource_path(relative_path):
    try:
        base_path = Path(sys._MEIPASS)
    except Exception:
        base_path = Path(__file__).parent
    return base_path / relative_path


class BitwardenManager:
    """Fetch credentials from Bitwarden vault via bw CLI."""

    def __init__(self):
        self._session = None
        self._cache = {}

    def _ensure_session(self):
        if self._session:
            return
        client_id = os.environ.get("BW_CLIENTID", "")
        client_secret = os.environ.get("BW_CLIENTSECRET", "")
        password = os.environ.get("BW_PASSWORD", "")

        if not client_id or not client_secret or not password:
            creds_file = os.path.expanduser("~/.cloudtek/.bw-creds")
            if not os.path.exists(creds_file):
                creds_file = os.path.expanduser("~/.claw-vm/.bw-creds")
            if os.path.exists(creds_file):
                with open(creds_file) as f:
                    creds = json.load(f)
                client_id = creds.get("client_id", "")
                client_secret = creds.get("client_secret", "")
                password = creds.get("password", "")

        if not client_id or not client_secret:
            print("[error] Bitwarden credentials not found.")
            print("  Set BW_CLIENTID, BW_CLIENTSECRET, BW_PASSWORD env vars")
            print("  Or create ~/.cloudtek/.bw-creds with {client_id, client_secret, password}")
            sys.exit(1)

        env = os.environ.copy()
        env["BW_CLIENTID"] = client_id
        env["BW_CLIENTSECRET"] = client_secret

        result = subprocess.run(
            ["bw", "login", "--apikey"],
            capture_output=True, text=True, env=env
        )
        if result.returncode != 0 and "already logged in" not in result.stderr.lower():
            subprocess.run(["bw", "logout"], capture_output=True, text=True)
            result = subprocess.run(
                ["bw", "login", "--apikey"],
                capture_output=True, text=True, env=env
            )
            if result.returncode != 0:
                print(f"[error] bw login failed: {result.stderr.strip()}")
                sys.exit(1)

        result = subprocess.run(
            ["bw", "unlock", "--passwordenv", "BW_PASSWORD"],
            capture_output=True, text=True,
            env={**env, "BW_PASSWORD": password}
        )
        if result.returncode != 0:
            print(f"[error] bw unlock failed: {result.stderr.strip()}")
            sys.exit(1)

        for line in result.stdout.splitlines():
            if 'BW_SESSION="' in line:
                self._session = line.split('BW_SESSION="')[1].rstrip('"')
                break
            elif "BW_SESSION=" in line:
                self._session = line.split("BW_SESSION=")[1].strip().strip('"')
                break

        if not self._session:
            print("[error] Could not extract BW_SESSION from unlock output.")
            print(result.stdout)
            sys.exit(1)

        subprocess.run(
            ["bw", "sync", "--session", self._session],
            capture_output=True, text=True
        )

    def get_cred(self, item_name):
        if item_name in self._cache:
            return self._cache[item_name]

        self._ensure_session()

        result = subprocess.run(
            ["bw", "get", "item", item_name, "--session", self._session],
            capture_output=True, text=True
        )
        if result.returncode != 0:
            result = subprocess.run(
                ["bw", "get", "notes", item_name, "--session", self._session],
                capture_output=True, text=True
            )
            if result.returncode != 0:
                print(f"[error] Item '{item_name}' not found in Bitwarden vault.")
                sys.exit(1)
            self._cache[item_name] = result.stdout.strip()
            return self._cache[item_name]

        try:
            item = json.loads(result.stdout)
            if item.get("notes"):
                self._cache[item_name] = item["notes"]
                return self._cache[item_name]
            if item.get("login", {}).get("password"):
                self._cache[item_name] = item["login"]["password"]
                return self._cache[item_name]
            for field in item.get("fields", []):
                if field.get("name") == "value" or field.get("name") == item_name:
                    self._cache[item_name] = field["value"]
                    return self._cache[item_name]
        except json.JSONDecodeError:
            self._cache[item_name] = result.stdout.strip()
            return self._cache[item_name]

        print(f"[error] Item '{item_name}' found but has no usable value.")
        sys.exit(1)

    def lock(self):
        if self._session:
            subprocess.run(
                ["bw", "lock"],
                capture_output=True, text=True
            )
            self._session = None
            self._cache.clear()


class GCPProvider:
    def __init__(self, config, vault):
        self.config = config
        self.vault = vault
        self._driver = None

    def _get_driver(self):
        if self._driver:
            return self._driver
        from libcloud.compute.types import Provider
        from libcloud.compute.providers import get_driver
        creds_json = self.vault.get_cred("GCP_CREDENTIALS")
        if isinstance(creds_json, str):
            creds = json.loads(creds_json)
        else:
            creds = creds_json
        self._tmp_creds = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False)
        json.dump(creds, self._tmp_creds)
        self._tmp_creds.close()
        ComputeEngine = get_driver(Provider.GCE)
        self._driver = ComputeEngine(
            creds["client_email"],
            self._tmp_creds.name,
            project=self.config["project"],
            datacenter=self.config["zone"]
        )
        return self._driver

    def _cleanup_tmp(self):
        if hasattr(self, '_tmp_creds') and os.path.exists(self._tmp_creds.name):
            os.unlink(self._tmp_creds.name)

    def _get_ssh_user(self, name):
        for svc, prefix in self.config.get("image_prefixes", {}).items():
            if name.startswith(prefix) or name.startswith(svc):
                prof_name = self.config.get("service_profiles", {}).get(svc)
                if prof_name:
                    return self.config.get("profiles", {}).get(prof_name, {}).get("ssh_user", "core")
        return "core"

    def _get_tags(self, image_name):
        tags = ["test-vm"]
        for svc, prefix in self.config.get("image_prefixes", {}).items():
            if image_name.startswith(prefix) or image_name.startswith(svc):
                prof_name = self.config.get("service_profiles", {}).get(svc)
                if prof_name:
                    prof = self.config.get("profiles", {}).get(prof_name, {})
                    tags = prof.get("tags", tags)
                break
        return tags

    def list_images(self, filter_prefix=None):
        driver = self._get_driver()
        try:
            images = driver.list_images(ex_project=self.config["project"])
            if filter_prefix:
                images = [i for i in images if i.name.startswith(filter_prefix)]
            images.sort(key=lambda i: i.extra.get("creationTimestamp", ""), reverse=True)
            return images
        finally:
            self._cleanup_tmp()

    def list_vms(self):
        driver = self._get_driver()
        try:
            return driver.list_nodes(ex_zone=self.config["zone"])
        finally:
            self._cleanup_tmp()

    def launch(self, image_name, vm_name=None):
        driver = self._get_driver()
        try:
            if not vm_name:
                vm_name = f"{image_name}-test"
            from libcloud.compute.base import NodeSize
            size = NodeSize(
                id=self.config["machine_type"],
                name=self.config["machine_type"],
                ram=0, disk=0, bandwidth=0, price=0, driver=driver,
            )
            images = [i for i in driver.list_images(ex_project=self.config["project"])
                      if i.name == image_name]
            if not images:
                print(f"[error] Image '{image_name}' not found.")
                return None
            image = images[0]
            tags = self._get_tags(image_name)
            node = driver.create_node(
                name=vm_name,
                size=size,
                image=image,
                location=self.config["zone"],
                ex_network=self.config.get("network"),
                ex_subnetwork=self.config.get("subnetwork"),
                ex_disk_size=self.config.get("disk_size", 50),
                ex_tags=tags,
            )
            print(f"[ok] VM created: {node.name}")
            print("[info] Waiting 60s for VM to boot...")
            time.sleep(60)
            nodes = [n for n in driver.list_nodes(ex_zone=self.config["zone"]) if n.name == vm_name]
            if nodes and nodes[0].public_ips:
                print(f"[ok] Public IP: {nodes[0].public_ips[0]}")
            elif nodes and nodes[0].private_ips:
                print(f"[info] Private IP: {nodes[0].private_ips[0]} (no public IP)")
            return node
        finally:
            self._cleanup_tmp()

    def delete_vm(self, vm_name):
        driver = self._get_driver()
        try:
            nodes = [n for n in driver.list_nodes(ex_zone=self.config["zone"]) if n.name == vm_name]
            if not nodes:
                print(f"[error] VM '{vm_name}' not found.")
                return False
            driver.destroy_node(nodes[0])
            print(f"[ok] VM '{vm_name}' deleted.")
            return True
        finally:
            self._cleanup_tmp()

    def delete_image(self, image_name):
        driver = self._get_driver()
        try:
            images = [i for i in driver.list_images(ex_project=self.config["project"])
                      if i.name == image_name]
            if not images:
                print(f"[error] Image '{image_name}' not found.")
                return False
            driver.ex_delete_image(images[0])
            print(f"[ok] Image '{image_name}' deleted.")
            return True
        finally:
            self._cleanup_tmp()

    def get_vm_ip(self, vm_name):
        driver = self._get_driver()
        try:
            nodes = [n for n in driver.list_nodes(ex_zone=self.config["zone"]) if n.name == vm_name]
            if not nodes:
                return None
            return nodes[0].public_ips[0] if nodes[0].public_ips else None
        finally:
            self._cleanup_tmp()

    def ssh_cmd(self, vm_name, command=None):
        ip = self.get_vm_ip(vm_name)
        if not ip:
            print(f"[error] VM '{vm_name}' not found or has no public IP.")
            return None
        ssh_user = self._get_ssh_user(vm_name)
        ssh_key_content = self.vault.get_cred("GCP_SSH_PRIVATE_KEY")
        key_file = tempfile.NamedTemporaryFile(mode='w', suffix='.pem', delete=False)
        key_file.write(ssh_key_content)
        key_file.close()
        os.chmod(key_file.name, 0o600)
        try:
            ssh_base = f"ssh -i {key_file.name} -o StrictHostKeyChecking=no -o ConnectTimeout=10 {ssh_user}@{ip}"
            if command:
                result = subprocess.run(f"{ssh_base} '{command}'", shell=True, capture_output=True, text=True)
                print(result.stdout)
                if result.stderr:
                    print(result.stderr)
                return result.returncode
            else:
                return subprocess.call(ssh_base, shell=True)
        finally:
            os.unlink(key_file.name)


class AWSProvider:
    def __init__(self, config, vault):
        self.config = config
        self.vault = vault
        self._driver = None

    def _get_driver(self):
        if self._driver:
            return self._driver
        from libcloud.compute.types import Provider
        from libcloud.compute.providers import get_driver
        access_key = self.vault.get_cred("AWS_ACCESS_KEY_ID")
        secret_key = (
            self.vault.get_cred("AWS_SECRET_KEY_ID")
            or self.vault.get_cred("AWS_SECRET_ACCESS_KEY")
        )
        EC2 = get_driver(Provider.EC2)
        self._driver = EC2(access_key, secret_key, region=self.config["region"])
        return self._driver

    def _get_ssh_user(self, name):
        for svc, prefix in self.config.get("image_prefixes", {}).items():
            if name.startswith(prefix) or name.startswith(svc):
                prof_name = self.config.get("service_profiles", {}).get(svc)
                if prof_name:
                    return self.config.get("profiles", {}).get(prof_name, {}).get("ssh_user", "core")
        return "core"

    def list_images(self, filter_prefix=None):
        driver = self._get_driver()
        images = driver.list_images(ex_owner="self")
        if filter_prefix:
            images = [i for i in images if i.name and i.name.startswith(filter_prefix)]
        images.sort(key=lambda i: i.extra.get("creation_date", ""), reverse=True)
        return images

    def list_vms(self):
        driver = self._get_driver()
        return driver.list_nodes()

    def launch(self, image_name, vm_name=None):
        driver = self._get_driver()
        if not vm_name:
            vm_name = f"{image_name}-test"
        images = [i for i in driver.list_images(ex_owner="self") if i.name == image_name]
        if not images:
            print(f"[error] AMI '{image_name}' not found.")
            return None
        image = images[0]
        from libcloud.compute.base import NodeSize
        size = NodeSize(
            id=self.config["instance_type"],
            name=self.config["instance_type"],
            ram=0, disk=0, bandwidth=0, price=0, driver=driver,
        )
        sg_id = self.config.get("security_group_id", "")
        ex_security_group_ids = [sg_id] if sg_id else None
        subnet_id = self.config.get("subnet_id", "")
        create_kwargs = dict(
            name=vm_name,
            size=size,
            image=image,
            ex_blockdevicemappings=[{
                "DeviceName": "/dev/xvda",
                "Ebs": {"VolumeSize": self.config.get("disk_size", 50)}
            }],
        )
        if ex_security_group_ids:
            create_kwargs["ex_security_group_ids"] = ex_security_group_ids
            from libcloud.compute.drivers.ec2 import EC2NetworkSubnet
            if subnet_id and subnet_id.startswith("subnet-"):
                create_kwargs["ex_subnet"] = EC2NetworkSubnet(
                    id=subnet_id, name="", state="available", extra={},
                )
            else:
                vpc_id = self.config.get("vpc_id", "")
                subnets = driver.ex_list_subnets()
                if vpc_id:
                    subnets = [s for s in subnets if s.extra.get("vpc_id") == vpc_id]
                preferred = [s for s in subnets if not s.extra.get("zone", "").endswith("e")]
                chosen = preferred[0] if preferred else (subnets[0] if subnets else None)
                if chosen:
                    create_kwargs["ex_subnet"] = chosen
                    print(f"[info] Using subnet: {chosen.id} ({chosen.extra.get('zone', '?')})")
                else:
                    print("[warn] No subnet found — launching without security group IDs")
                    del create_kwargs["ex_security_group_ids"]
        node = driver.create_node(**create_kwargs)
        print(f"[ok] VM created: {node.name} ({node.id})")
        print("[info] Waiting 60s for VM to boot...")
        time.sleep(60)
        nodes = [n for n in driver.list_nodes() if n.id == node.id]
        if nodes and nodes[0].public_ips:
            print(f"[ok] Public IP: {nodes[0].public_ips[0]}")
        return node

    def delete_vm(self, vm_name):
        driver = self._get_driver()
        nodes = [n for n in driver.list_nodes() if n.name == vm_name or n.id == vm_name]
        if not nodes:
            print(f"[error] VM '{vm_name}' not found.")
            return False
        driver.destroy_node(nodes[0])
        print(f"[ok] VM '{vm_name}' deleted.")
        return True

    def delete_image(self, image_name):
        driver = self._get_driver()
        images = [i for i in driver.list_images(ex_owner="self") if i.name == image_name or i.id == image_name]
        if not images:
            print(f"[error] Image '{image_name}' not found.")
            return False
        driver.delete_image(images[0])
        print(f"[ok] Image '{image_name}' deleted.")
        return True

    def get_vm_ip(self, vm_name):
        driver = self._get_driver()
        nodes = [n for n in driver.list_nodes() if n.name == vm_name or n.id == vm_name]
        if not nodes:
            return None
        return nodes[0].public_ips[0] if nodes[0].public_ips else None

    def ssh_cmd(self, vm_name, command=None):
        ip = self.get_vm_ip(vm_name)
        if not ip:
            print(f"[error] VM '{vm_name}' not found or has no public IP.")
            return None
        ssh_user = self._get_ssh_user(vm_name)
        ssh_key_content = self.vault.get_cred("AWS_SSH_PRIVATE_KEY")
        key_file = tempfile.NamedTemporaryFile(mode='w', suffix='.pem', delete=False)
        key_file.write(ssh_key_content)
        key_file.close()
        os.chmod(key_file.name, 0o600)
        try:
            ssh_base = f"ssh -i {key_file.name} -o StrictHostKeyChecking=no -o ConnectTimeout=10 {ssh_user}@{ip}"
            if command:
                result = subprocess.run(f"{ssh_base} '{command}'", shell=True, capture_output=True, text=True)
                print(result.stdout)
                if result.stderr:
                    print(result.stderr)
                return result.returncode
            else:
                return subprocess.call(ssh_base, shell=True)
        finally:
            os.unlink(key_file.name)


class AzureProvider:
    def __init__(self, config, vault):
        self.config = config
        self.vault = vault
        self._driver = None

    def _get_driver(self):
        if self._driver:
            return self._driver
        from libcloud.compute.types import Provider
        from libcloud.compute.providers import get_driver
        tenant_id = self.vault.get_cred("AZURE_TENANT_ID")
        subscription_id = self.vault.get_cred("AZURE_SUBSCRIPTION_ID")
        client_id = self.vault.get_cred("AZURE_CLIENT_ID")
        client_secret = self.vault.get_cred("AZURE_CLIENT_SECRET")
        AzureNodeDriver = get_driver(Provider.AZURE_ARM)
        self._driver = AzureNodeDriver(
            tenant_id=tenant_id,
            subscription_id=subscription_id,
            key=client_id,
            secret=client_secret,
        )
        return self._driver

    def list_images(self, filter_prefix=None):
        driver = self._get_driver()
        rg = self.config.get("resource_group", "vm-builder-rg")
        location = self.config.get("location", "eastus")
        images = driver.list_images(location=location, ex_resource_group=rg)
        if filter_prefix:
            images = [i for i in images if i.name and i.name.startswith(filter_prefix)]
        return images

    def list_vms(self):
        driver = self._get_driver()
        return driver.list_nodes()

    def launch(self, image_name, vm_name=None):
        print("[warn] Azure launch not yet fully implemented — needs creds configured first.")
        return None

    def delete_vm(self, vm_name):
        driver = self._get_driver()
        nodes = [n for n in driver.list_nodes() if n.name == vm_name]
        if not nodes:
            print(f"[error] VM '{vm_name}' not found.")
            return False
        driver.destroy_node(nodes[0])
        print(f"[ok] VM '{vm_name}' deleted.")
        return True

    def delete_image(self, image_name):
        print("[warn] Azure image deletion not yet implemented.")
        return False

    def get_vm_ip(self, vm_name):
        return None

    def ssh_cmd(self, vm_name, command=None):
        print("[warn] Azure SSH not yet implemented.")
        return None


def run_playbook(provider, vm_name, playbook_path, extra_vars=None):
    ip = provider.get_vm_ip(vm_name)
    if not ip:
        print(f"[error] VM '{vm_name}' not found or has no public IP.")
        return 1

    ssh_user = provider._get_ssh_user(vm_name)

    cloud_key_name = "GCP_SSH_PRIVATE_KEY"
    if isinstance(provider, AWSProvider):
        cloud_key_name = "AWS_SSH_PRIVATE_KEY"
    elif isinstance(provider, AzureProvider):
        cloud_key_name = "AZURE_SSH_PRIVATE_KEY"

    ssh_key_content = provider.vault.get_cred(cloud_key_name)
    key_file = tempfile.NamedTemporaryFile(mode='w', suffix='.pem', delete=False)
    key_file.write(ssh_key_content)
    key_file.close()
    os.chmod(key_file.name, 0o600)

    try:
        cmd = [
            "ansible-playbook", playbook_path,
            "-i", f"{ip},",
            "-e", f"target_host={ip}",
            "-u", ssh_user,
            "--private-key", key_file.name,
            "--ssh-extra-args=-o StrictHostKeyChecking=no",
        ]
        if extra_vars:
            for k, v in extra_vars.items():
                cmd.extend(["-e", f"{k}={v}"])

        print(f"[info] Running playbook: {playbook_path}")
        result = subprocess.run(cmd, text=True)
        return result.returncode
    finally:
        os.unlink(key_file.name)


PROVIDERS = {
    "gcp": (GCPProvider, "gcp.yaml"),
    "aws": (AWSProvider, "aws.yaml"),
    "azure": (AzureProvider, "azure.yaml"),
}


def get_provider(cloud, vault):
    if cloud not in PROVIDERS:
        print(f"[error] Unknown cloud: {cloud}. Options: gcp, aws, azure")
        sys.exit(1)
    cls, config_file = PROVIDERS[cloud]
    config_path = get_resource_path("configs") / config_file
    if not config_path.exists():
        print(f"[error] Config not found: {config_path}")
        sys.exit(1)
    with open(config_path) as f:
        config = yaml.safe_load(f)
    return cls(config, vault)


def main():
    parser = argparse.ArgumentParser(
        prog="cloudtek",
        description="VM lifecycle via libcloud + Bitwarden (app-store / headless)",
    )

    sub = parser.add_subparsers(dest="command")

    p_launch = sub.add_parser("launch", help="Launch a test VM from a built image")
    p_launch.add_argument("--cloud", required=True, choices=["gcp", "aws", "azure"])
    p_launch.add_argument("--image", required=True, help="Image name to launch from")
    p_launch.add_argument("--name", help="VM name (default: <image>-test)")

    p_list_vms = sub.add_parser("list-vms", help="List running VMs")
    p_list_vms.add_argument("--cloud", required=True, choices=["gcp", "aws", "azure"])

    p_list_images = sub.add_parser("list-images", help="List available images")
    p_list_images.add_argument("--cloud", required=True, choices=["gcp", "aws", "azure"])
    p_list_images.add_argument("--filter", help="Filter by prefix")

    p_del_vm = sub.add_parser("delete-vm", help="Delete a VM")
    p_del_vm.add_argument("--cloud", required=True, choices=["gcp", "aws", "azure"])
    p_del_vm.add_argument("--name", required=True, help="VM name to delete")

    p_del_img = sub.add_parser("delete-image", help="Delete an image")
    p_del_img.add_argument("--cloud", required=True, choices=["gcp", "aws", "azure"])
    p_del_img.add_argument("--name", required=True, help="Image name to delete")

    p_ssh = sub.add_parser("ssh", help="SSH into a VM or run a command")
    p_ssh.add_argument("--cloud", required=True, choices=["gcp", "aws", "azure"])
    p_ssh.add_argument("--name", required=True, help="VM name")
    p_ssh.add_argument("--cmd", help="Command to run (omit for interactive SSH)")

    p_smoke = sub.add_parser("smoke-test", help="Run smoke tests on a VM via SSH")
    p_smoke.add_argument("--cloud", required=True, choices=["gcp", "aws", "azure"])
    p_smoke.add_argument("--name", required=True, help="VM name")

    p_play = sub.add_parser("playbook", help="Run an Ansible playbook against a VM")
    p_play.add_argument("--cloud", required=True, choices=["gcp", "aws", "azure"])
    p_play.add_argument("--name", required=True, help="VM name")
    p_play.add_argument("--playbook", required=True, help="Path to playbook YAML")

    p_ip = sub.add_parser("get-ip", help="Get public IP of a VM")
    p_ip.add_argument("--cloud", required=True, choices=["gcp", "aws", "azure"])
    p_ip.add_argument("--name", required=True, help="VM name")

    sub.add_parser("version", help="Show version")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(0)

    if args.command == "version":
        print("cloudtek 0.1.0")
        sys.exit(0)

    vault = BitwardenManager()
    provider = get_provider(args.cloud, vault)

    try:
        if args.command == "launch":
            provider.launch(args.image, args.name)
        elif args.command == "list-vms":
            nodes = provider.list_vms()
            if not nodes:
                print("[info] No VMs found.")
            else:
                for n in nodes:
                    status = n.state
                    ips = ", ".join(n.public_ips) if n.public_ips else "no public IP"
                    print(f"  {n.name}  ({status})  {ips}")
        elif args.command == "list-images":
            images = provider.list_images(filter_prefix=args.filter)
            if not images:
                print("[info] No images found.")
            else:
                for img in images:
                    print(f"  {img.name}")
        elif args.command == "delete-vm":
            provider.delete_vm(args.name)
        elif args.command == "delete-image":
            provider.delete_image(args.name)
        elif args.command == "ssh":
            provider.ssh_cmd(args.name, args.cmd)
        elif args.command == "get-ip":
            ip = provider.get_vm_ip(args.name)
            if ip:
                print(ip)
            else:
                print("[error] No public IP found.")
        elif args.command == "playbook":
            rc = run_playbook(provider, args.name, args.playbook)
            sys.exit(rc)
        elif args.command == "smoke-test":
            print(f"[info] Running smoke tests on {args.name}...")
            tests = [
                ("docker daemon", "systemctl is-active docker"),
                ("containers running", "docker ps --format '{{.Names}}: {{.Status}}'"),
                ("disk space", "df -h /"),
                ("memory", "free -h"),
                ("https 443", "curl -k -s -o /dev/null -w '%{http_code}' https://localhost:443"),
            ]
            passed = 0
            total = len(tests)
            for tname, cmd in tests:
                rc = provider.ssh_cmd(args.name, cmd)
                if rc == 0:
                    passed += 1
                    print(f"  [PASS] {tname}")
                else:
                    print(f"  [FAIL] {tname}")
            print(f"\nResults: {passed}/{total} passed")
    finally:
        vault.lock()


if __name__ == "__main__":
    main()

