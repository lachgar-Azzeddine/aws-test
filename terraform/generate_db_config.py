#!/usr/bin/env python3
"""
Generate initial_db.py configuration from Terraform output.

Usage:
    cd terraform
    terraform output -json > tf_output.json
    python generate_db_config.py tf_output.json

Or directly:
    terraform output -json | python generate_db_config.py -
"""

import json
import sys
import os


def generate_initial_db_content(tf_output: dict, ssh_public_key: str, ssh_private_key: str, base_domain: str) -> str:
    """Generate the initial_db.py content from Terraform output."""

    vm_details = tf_output.get("vm_details", {}).get("value", {})

    # Get subnet info for zone configuration
    all_private_ips = tf_output.get("all_private_ips", {}).get("value", {})

    # Determine network from first IP
    first_ip = list(all_private_ips.values())[0] if all_private_ips else "10.0.0.0"
    network_parts = first_ip.rsplit(".", 1)
    sub_network = f"{network_parts[0]}.0" if len(network_parts) == 2 else "10.0.0.0"
    gateway = f"{network_parts[0]}.1" if len(network_parts) == 2 else "10.0.0.1"

    content = f'''import os
from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker

from models import (
    Configuration,
    Monitoring,
    Security,
    VirtualMachine,
    Zone,
    create_tables,
)
import logging

# ==========================================================================
# DATABASE PATH - Adjust as needed
# ==========================================================================
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./sql_app.db")

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def initialize_database(db_path=None):
    """
    Initialize database with configuration from Terraform.
    AUTO-GENERATED - Do not edit manually!
    """
    db_uri = db_path if db_path else DATABASE_URL
    if not db_uri.startswith("sqlite:///") and not db_uri.startswith("postgresql://"):
        db_uri = f"sqlite:///{{db_uri}}"

    Engine = create_engine(db_uri)

    # Check if database already exists
    inspector = inspect(Engine)
    if not inspector.has_table("configurations"):
        logger.info("Database not initialized, creating tables and initial data")
        Session = sessionmaker(bind=Engine)
        session = Session()
        create_tables(Engine)

        # ==========================================================================
        # MONITORING CONFIGURATION
        # ==========================================================================
        monitoring = Monitoring(
            id=1,
            deploy_embeded_monitoring_stack=True,
            logs_retention_period=1,
            logs_retention_disk_space=100,
            metrics_retention_period=1,
            metrics_retnetion_disk_space=100,
        )
        session.add(monitoring)

        # ==========================================================================
        # SECURITY CONFIGURATION - FROM TERRAFORM
        # ==========================================================================
        security = Security(
            id=1,
            use_proxy=False,
            porxy_host="",
            proxy_port="",
            proxy_login="",
            proxy_password="",
            ssh_pulic_key="""{ssh_public_key}""",
            ssh_private_key="""{ssh_private_key}""",
            ssh_private_key_pwd="",
            base_domain="{base_domain}",
            env_prefix="",
            pem_certificate="",
        )
        session.add(security)

        # ==========================================================================
        # MAIN CONFIGURATION
        # ==========================================================================
        configuration = Configuration(
            id=1,
            number_concurrent_users=100,
            monitoring=monitoring,
            security=security,
        )
        session.add(configuration)

        # ==========================================================================
        # ZONE CONFIGURATION - FROM TERRAFORM
        # ==========================================================================
        zone1 = Zone(
            id=1,
            name="lan",
            sub_network="{sub_network}",
            network_mask="24",
            dns="8.8.8.8",
            hypervisor_type="aws",
            gateway="{gateway}",
            domain="{base_domain}",
            vlan_name="",
        )
        session.add(zone1)
        session.commit()

        # ==========================================================================
        # VIRTUAL MACHINES - FROM TERRAFORM OUTPUT
        # ==========================================================================
'''

    # Add VMs
    vm_index = 1
    for vm_name, vm_info in vm_details.items():
        hostname = vm_info.get("hostname", vm_name)
        private_ip = vm_info.get("private_ip", "")
        group = vm_info.get("group", "")
        roles = vm_info.get("roles", "")

        # Determine CPU/RAM based on t3.medium
        nb_cpu = 2
        ram = 4096
        os_disk_size = 50
        data_disk_size = 100 if group == "RKEAPPS" else 0

        content += f'''
        # VM {vm_index}: {hostname} ({group})
        vm{vm_index} = VirtualMachine(
            hostname="{hostname}",
            roles="{roles}",
            group="{group}",
            ip="{private_ip}",
            nb_cpu={nb_cpu},
            ram={ram},
            os_disk_size={os_disk_size},
            data_disk_size={data_disk_size},
            zone_id=zone1.id,
            status="created",
        )
        session.add(vm{vm_index})
'''
        vm_index += 1

    content += '''
        session.commit()
        logger.info("Database initialized with Terraform VMs")
        session.close()
    else:
        logger.info("Database already initialized")

    Session = sessionmaker(bind=Engine)
    return Engine, Session


if __name__ == "__main__":
    initialize_database()
'''

    return content


def main():
    if len(sys.argv) < 2:
        print("Usage: python generate_db_config.py <terraform_output.json>")
        print("       terraform output -json | python generate_db_config.py -")
        sys.exit(1)

    input_file = sys.argv[1]

    # Read Terraform output
    if input_file == "-":
        tf_output = json.load(sys.stdin)
    else:
        with open(input_file, "r") as f:
            tf_output = json.load(f)

    # Read SSH keys from files or environment
    ssh_public_key = os.environ.get("SSH_PUBLIC_KEY", "")
    ssh_private_key = os.environ.get("SSH_PRIVATE_KEY", "")
    base_domain = os.environ.get("BASE_DOMAIN", "local")

    # Try to read from default locations if not in env
    if not ssh_public_key:
        try:
            with open(os.path.expanduser("~/.ssh/id_rsa.pub"), "r") as f:
                ssh_public_key = f.read().strip()
        except FileNotFoundError:
            print("Warning: SSH public key not found. Set SSH_PUBLIC_KEY env var.")

    if not ssh_private_key:
        try:
            with open(os.path.expanduser("~/.ssh/id_rsa"), "r") as f:
                ssh_private_key = f.read().strip()
        except FileNotFoundError:
            print("Warning: SSH private key not found. Set SSH_PRIVATE_KEY env var.")

    # Generate content
    content = generate_initial_db_content(tf_output, ssh_public_key, ssh_private_key, base_domain)

    # Output to file
    output_file = os.path.join(os.path.dirname(__file__), "..", "backend", "initial_db.py")
    with open(output_file, "w") as f:
        f.write(content)

    print(f"Generated: {output_file}")
    print("\nVM Configuration:")
    for vm_name, vm_info in tf_output.get("vm_details", {}).get("value", {}).items():
        print(f"  {vm_name}: {vm_info.get('private_ip')} ({vm_info.get('group')})")


if __name__ == "__main__":
    main()
