import os
from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker

from models import (
    Configuration,
    Monitoring,
    # Product removed - no longer using product-based system
    Security,
    User,
    Zone,
    create_tables,
)
from cryptography.fernet import Fernet

# Encryption key (same as in repository.py)
ENCRYPTION_KEY = "uOdT_oGBMvG8N7_rpBg1UVlwVK7BD6igm0l4IqJD8cA="
fernet = Fernet(ENCRYPTION_KEY)

def encrypt_password(plain_password: str):
    """Encrypt password using Fernet"""
    encoded_pwd = plain_password.encode()
    encrypted_pwd_bytes = fernet.encrypt(encoded_pwd)
    return encrypted_pwd_bytes.decode()
import logging

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def initialize_database():
    # create database and itialize tables
    db_uri = os.getenv("DATABASE_URL", "sqlite:///./sql_app.db")
    Engine = create_engine(db_uri)
    
    # Check if the 'configurations' table exists
    inspector = inspect(Engine)
    if not inspector.has_table("configurations"):
        logger.info("Database not initialized, creating tables and initial data")
        Session = sessionmaker(bind=Engine)
        session = Session()
        create_tables(Engine)

        # Product initialization removed - no longer using product-based system
        monitoring = Monitoring(
            id=1,
            deploy_embeded_monitoring_stack=True,
            logs_retention_period=1,
            logs_retention_disk_space=100,
            metrics_retention_period=1,
            metrics_retnetion_disk_space=100,
        )
        session.add(monitoring)
        security = Security(
            id=1,
            use_proxy=False,
            porxy_host="",
            proxy_port="",
            proxy_login="",
            proxy_password="",
            ssh_pulic_key="",
            ssh_private_key="",
            base_domain="",
            env_prefix="",
            pem_certificate="",
        )
        session.add(security)
        configuration = Configuration(
            id=1,
            number_concurrent_users=100,
            monitoring=monitoring,
            security=security,
        )
        # products relationship removed
        session.add(configuration)
        zone1 = Zone(
            id=1,
            name="apps",
            sub_network="",
            network_mask=0,
            dns="",
            hypervisor_type="vmware",
            gateway="",
            domain="",
            vlan_name="",
        )
        session.add(zone1)
        zone2 = Zone(
            id=2,
            name="infra",
            sub_network="",
            network_mask=0,
            dns="",
            hypervisor_type="vmware",
            gateway="",
            domain="",
            vlan_name="",
        )
        session.add(zone2)
        zone3 = Zone(
            id=3,
            name="dmz",
            sub_network="",
            network_mask=0,
            dns="",
            hypervisor_type="vmware",
            gateway="",
            domain="",
            vlan_name="",
        )
        session.add(zone3)

        # ================================================================
        # CREATE DEFAULT ADMIN USER FOR TESTING
        # ================================================================
        # Username: admin
        # Password: admin123
        # IMPORTANT: Change this password after first login!
        # ================================================================
        default_admin = User(
            id=1,
            username="admin",
            password=encrypt_password("admin123"),
            is_active=True,
            role="admin"
        )
        session.add(default_admin)
        logger.info("✅ Default admin user created (username: admin, password: admin123)")
        logger.warning("⚠️  CHANGE DEFAULT PASSWORD AFTER FIRST LOGIN!")

        session.commit()
        session.close()
    else:
        logger.info("Database already initialized")

    Session = sessionmaker(bind=Engine)
    return Engine, Session


if __name__ == "__main__":
    initialize_database()