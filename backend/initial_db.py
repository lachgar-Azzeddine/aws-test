import os
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
    Initialize database with default configuration and VMs.
    MES-OMNI STYLE - Creates zones, security config, and VMs directly.
    """
    db_uri = db_path if db_path else DATABASE_URL
    if not db_uri.startswith("sqlite:///") and not db_uri.startswith("postgresql://"):
        db_uri = f"sqlite:///{db_uri}"

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
        # SECURITY CONFIGURATION - FILL IN YOUR VALUES
        # ==========================================================================
        security = Security(
            id=1,
            use_proxy=False,
            porxy_host="",
            proxy_port="",
            proxy_login="",
            proxy_password="",
            # FILL: Your SSH public key for connecting to VMs
            ssh_pulic_key="",
            # FILL: Your SSH private key for connecting to VMs
            ssh_private_key="",
            ssh_private_key_pwd="",
            # FILL: Your base domain, e.g., "example.com"
            base_domain="",
            # FILL: Environment prefix, e.g., "test" or "prod" (optional)
            env_prefix="",
            # FILL: Your PEM certificate for HTTPS (optional)
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
        # ZONE CONFIGURATION - FILL IN YOUR NETWORK DETAILS
        # ==========================================================================
        # Zone 1: LAN/Apps zone - main zone for all VMs
        zone1 = Zone(
            id=1,
            name="lan",
            sub_network="",        # FILL: e.g., "192.168.1.0"
            network_mask="",       # FILL: e.g., "24"
            dns="",                # FILL: e.g., "8.8.8.8"
            hypervisor_type="none",  # No hypervisor - VMs pre-exist
            gateway="",            # FILL: e.g., "192.168.1.1"
            domain="",             # FILL: e.g., "local"
            vlan_name="",          # FILL: e.g., "VLAN_100"
        )
        session.add(zone1)
        session.commit()  # Commit zone first so we can reference it

        # ==========================================================================
        # VIRTUAL MACHINES - FILL IN YOUR 6 VMs
        # ==========================================================================
        # REQUIRED GROUPS:
        #   - "vault"   : HashiCorp Vault (needed by other roles for secrets)
        #   - "gitops"  : Gogs + Docker Registry
        #   - "RKEAPPS" : RKE2 Kubernetes cluster nodes
        # ==========================================================================

        # VM 1: Vault - HashiCorp Vault (MUST BE FIRST - other roles depend on it)
        vm1 = VirtualMachine(
            hostname="",           # FILL: e.g., "vault"
            roles="vault",
            group="vault",         # REQUIRED: install-vault, install-gogs need this
            ip="",                 # FILL: e.g., "192.168.1.10"
            nb_cpu=0,              # FILL: e.g., 4
            ram=0,                 # FILL: e.g., 8192 (MB)
            os_disk_size=0,        # FILL: e.g., 50 (GB)
            data_disk_size=0,      # FILL: e.g., 50 (GB)
            zone_id=zone1.id,
            status="created",
        )
        session.add(vm1)

        # VM 2: GitOps - Gogs + Docker Registry
        vm2 = VirtualMachine(
            hostname="",           # FILL: e.g., "gitops"
            roles="git,docker-registry",
            group="gitops",        # REQUIRED: install-gogs, install-docker-registry need this
            ip="",                 # FILL: e.g., "192.168.1.11"
            nb_cpu=0,              # FILL: e.g., 4
            ram=0,                 # FILL: e.g., 8192 (MB)
            os_disk_size=0,        # FILL: e.g., 50 (GB)
            data_disk_size=0,      # FILL: e.g., 200 (GB) - for Docker images
            zone_id=zone1.id,
            status="created",
        )
        session.add(vm2)

        # VM 3: RKE2 Node 1 - Kubernetes master/worker
        vm3 = VirtualMachine(
            hostname="",           # FILL: e.g., "rkeapp1"
            roles="master,worker,cns",
            group="RKEAPPS",       # REQUIRED: install-rke2-apps needs this
            ip="",                 # FILL: e.g., "192.168.1.12"
            nb_cpu=0,              # FILL: e.g., 4
            ram=0,                 # FILL: e.g., 16384 (MB)
            os_disk_size=0,        # FILL: e.g., 80 (GB)
            data_disk_size=0,      # FILL: e.g., 100 (GB) - for Longhorn storage
            zone_id=zone1.id,
            status="created",
        )
        session.add(vm3)

        # VM 4: RKE2 Node 2 - Kubernetes master/worker
        vm4 = VirtualMachine(
            hostname="",           # FILL: e.g., "rkeapp2"
            roles="master,worker,cns",
            group="RKEAPPS",
            ip="",                 # FILL: e.g., "192.168.1.13"
            nb_cpu=0,
            ram=0,
            os_disk_size=0,
            data_disk_size=0,
            zone_id=zone1.id,
            status="created",
        )
        session.add(vm4)

        # VM 5: RKE2 Node 3 - Kubernetes master/worker
        vm5 = VirtualMachine(
            hostname="",           # FILL: e.g., "rkeapp3"
            roles="master,worker,cns",
            group="RKEAPPS",
            ip="",                 # FILL: e.g., "192.168.1.14"
            nb_cpu=0,
            ram=0,
            os_disk_size=0,
            data_disk_size=0,
            zone_id=zone1.id,
            status="created",
        )
        session.add(vm5)

        # VM 6: (OPTIONAL) Middleware - Keycloak, Seald
        # Uncomment if you need Keycloak/Seald
        # vm6 = VirtualMachine(
        #     hostname="",           # FILL: e.g., "middleware"
        #     roles="keycloak,seald",
        #     group="RKEMIDDLEWARE",
        #     ip="",                 # FILL: e.g., "192.168.1.15"
        #     nb_cpu=0,
        #     ram=0,
        #     os_disk_size=0,
        #     data_disk_size=0,
        #     zone_id=zone1.id,
        #     status="created",
        # )
        # session.add(vm6)

        session.commit()
        logger.info("Database initialized with zones and VMs")
        session.close()
    else:
        logger.info("Database already initialized")

    Session = sessionmaker(bind=Engine)
    return Engine, Session


if __name__ == "__main__":
    initialize_database()