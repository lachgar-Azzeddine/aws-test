from sqlalchemy import (
    Column,
    String,
    Text,
    # BigInteger,
    Boolean,
    Integer,
    ForeignKey,
    DateTime,
)
from datetime import datetime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from pydantic import BaseModel
from typing import List, Optional


Base = declarative_base()


def create_tables(engine):
    Base.metadata.create_all(engine)


class User(Base):
    __tablename__ = "user"
    id = Column(Integer, primary_key=True)
    username = Column(String, nullable=False)
    password = Column(String, nullable=False)
    is_active = Column(Boolean, nullable=False, default=True)
    role = Column(String, nullable=False)


class UserModel(BaseModel):
    id: int
    username: str
    password: str
    is_active: bool
    role: str


class UserStatusModel(BaseModel):
    id: int
    is_active: bool


class Token(BaseModel):
    access_token: str
    token_type: str


class GlobalRecap(BaseModel):
    zone: str
    total_cpu: int
    total_memory: int
    total_disk: int


class HypervisorModel(BaseModel):
    id: int
    alias: str
    type: str
    is_connected: bool
    # class Config:
    #    from_attributes = True


class certificatModel(BaseModel):
    domain: str
    certificate: str


class sshKeyModel(BaseModel):
    public_key_str: str
    private_key_str: str
    private_key_pwd: Optional[str] = None


class ConnectionDetailsModel(BaseModel):
    source_host: str
    destination_host: str
    destination_port: str
    pkey_str: Optional[str] = None
    passphrase: Optional[str] = None
    isUDP: Optional[bool] = False


class ServiceModel(BaseModel):
    destination: str
    port: Optional[str] = None


class Security(Base):
    __tablename__ = "security"
    id = Column(Integer, primary_key=True)
    use_proxy = Column(Boolean, nullable=False, default=False)
    porxy_host = Column(String, nullable=True)
    proxy_port = Column(String, nullable=True)
    proxy_login = Column(String, nullable=True, default="")
    proxy_password = Column(String, nullable=True, default="")
    ssh_pulic_key = Column(String, nullable=False)
    ssh_private_key = Column(String, nullable=False)
    ssh_private_key_pwd = Column(String, nullable=True, default="")
    base_domain = Column(String, nullable=False)
    env_prefix = Column(String, nullable=False)
    pem_certificate = Column(Text, nullable=False)
    configuration_id = Column(Integer, ForeignKey("configurations.id"))
    configuration = relationship("Configuration", back_populates="security")


# Pydantic model for the update request body
class SecurityUpdateModel(BaseModel):
    use_proxy: bool
    porxy_host: str
    proxy_port: str
    proxy_login: str
    proxy_password: str
    ssh_pulic_key: str
    ssh_private_key: str
    ssh_private_key_pwd: str
    base_domain: str
    env_prefix: str
    pem_certificate: str


class SecurityModel(BaseModel):
    id: int
    use_proxy: bool
    porxy_host: Optional[str]
    proxy_port: Optional[str]
    proxy_login: Optional[str]
    proxy_password: Optional[str]
    ssh_pulic_key: str
    ssh_private_key: str
    ssh_private_key_pwd: str
    base_domain: str
    env_prefix: str
    pem_certificate: str

    class Config:
        from_attributes = True


class Database(Base):
    __tablename__ = "database"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    type = Column(String, nullable=False)
    alias = Column(String, nullable=False)
    host = Column(String, nullable=False)
    servername = Column(String, nullable=True)
    port = Column(Integer, nullable=False)
    login = Column(String, nullable=False)
    password = Column(String, nullable=False)
    is_connected = Column(Boolean, nullable=False, default=False)
    configuration_id = Column(Integer, ForeignKey("configurations.id"), nullable=False)
    configuration = relationship("Configuration", back_populates="databases")


class DatabaseModel(BaseModel):
    id: int
    name: str
    type: str
    host: str
    servername: str
    port: int
    login: str
    password: str
    is_connected: bool
    alias: str

    class Config:
        from_attributes = True


class Monitoring(Base):
    __tablename__ = "monitoring"
    id = Column(Integer, primary_key=True)
    deploy_embeded_monitoring_stack = Column(Boolean, nullable=False, default=True)
    logs_retention_period = Column(Integer, nullable=True, default=1)
    logs_retention_disk_space = Column(Integer, nullable=True, default=100)
    metrics_retention_period = Column(Integer, nullable=True, default=1)
    metrics_retnetion_disk_space = Column(Integer, nullable=True, default=100)
    configuration_id = Column(Integer, ForeignKey("configurations.id"))
    configuration = relationship("Configuration", back_populates="monitoring")


class MonitoringModel(BaseModel):
    id: int
    deploy_embeded_monitoring_stack: bool
    logs_retention_period: Optional[int]
    logs_retention_disk_space: Optional[int]
    metrics_retention_period: Optional[int]
    metrics_retnetion_disk_space: Optional[int]

    class Config:
        from_attributes = True


class VaultCredentials(Base):
    __tablename__ = "vault_credentials"
    id = Column(Integer, primary_key=True)
    type = Column(String, nullable=False)
    value = Column(String, nullable=False)


class VaultCredentialsModel(BaseModel):
    id: int
    type: str
    value: str


# Product model removed - no longer using product-based system


class Application(Base):
    __tablename__ = "applications_harmo"
    id = Column(Integer, primary_key=True, autoincrement=True)
    url = Column(String, nullable=False)
    category = Column(String, nullable=False)
    name = Column(String, nullable=False)
    # product_id removed - no longer using product-based system
    configuration_id = Column(Integer, ForeignKey("configurations.id"), nullable=False)
    configuration = relationship("Configuration", back_populates="applications")


class ApplicationModel(BaseModel):
    id: int
    url: str
    category: str
    name: str
    # product_id removed - no longer using product-based system
    configuration_id: int

    class Config:
        from_attributes = True


class VMwareEsxi(Base):
    __tablename__ = "vmware_esxi"
    id = Column(Integer, primary_key=True, autoincrement=True)
    alias = Column(String, nullable=False)
    login = Column(String, nullable=False)
    password = Column(String, nullable=False)
    api_url = Column(String, nullable=False)
    api_timeout = Column(Integer, nullable=False)
    allow_unverified_ssl = Column(Boolean, nullable=False)
    datacenter_name = Column(String, nullable=False)
    datacenter_id = Column(String, nullable=False)
    target_name = Column(String, nullable=False)
    target_id = Column(String, nullable=False)
    target_type = Column(String, nullable=False)
    datastore_name = Column(String, nullable=False)
    datastore_id = Column(String, nullable=False)
    pool_ressource_name = Column(String, nullable=False)
    pool_ressource_id = Column(String, nullable=False)
    is_connected = Column(Boolean, nullable=False, default=False)
    configuration_id = Column(Integer, ForeignKey("configurations.id"), nullable=False)
    configuration = relationship("Configuration", back_populates="vmwares")
    zones = relationship("Zone", back_populates="vmware")


class VMwareEsxiModel(BaseModel):
    id: int
    alias: str
    login: str
    password: str
    api_url: str
    api_timeout: int
    allow_unverified_ssl: bool
    datacenter_name: str
    datacenter_id: str
    target_name: str
    target_id: str
    target_type: str
    datastore_name: str
    datastore_id: str
    pool_ressource_name: str
    pool_ressource_id: str
    is_connected: bool
    type: str = "vmware"

    class Config:
        from_attributes = True


class NutanixAHV(Base):
    __tablename__ = "nutanix_ahv"
    id = Column(Integer, primary_key=True, autoincrement=True)
    alias = Column(String, nullable=False)
    login = Column(String, nullable=False)
    password = Column(String, nullable=False)
    host = Column(String, nullable=False)
    port = Column(Integer, nullable=False)
    allow_unverified_ssl = Column(Boolean, nullable=False)
    is_connected = Column(Boolean, nullable=False, default=False)
    configuration_id = Column(Integer, ForeignKey("configurations.id"), nullable=False)
    configuration = relationship("Configuration", back_populates="nutanixs")
    zones = relationship("Zone", back_populates="nutanix")


class NutanixAHVModel(BaseModel):
    id: int
    alias: str
    login: str
    password: str
    host: str
    port: int
    allow_unverified_ssl: bool
    is_connected: bool
    type: str = "nutanix"

    class Config:
        from_attributes = True


class Ldap(Base):
    __tablename__ = "ldaps"
    id = Column(Integer, primary_key=True, autoincrement=True)
    ldap_type = Column(String, nullable=False)
    ldap_url = Column(String, nullable=False)
    ldap_port = Column(String, nullable=False)
    bind_dn = Column(String, nullable=True)
    bind_credentials = Column(String, nullable=False)
    user_dn = Column(String, nullable=True)
    user_ldap_attributes = Column(String, nullable=True)
    search_scope = Column(String, nullable=True)
    configuration_id = Column(Integer, ForeignKey("configurations.id"), nullable=False)
    configuration = relationship("Configuration", back_populates="ldaps")


class LdapModel(BaseModel):
    id: int
    ldap_type: str  # can be either internal_users or external_users
    ldap_url: str
    ldap_port: str
    bind_dn: Optional[str]
    bind_credentials: Optional[str]
    user_dn: Optional[str]
    user_ldap_attributes: Optional[str]
    search_scope: Optional[str]

    class Config:
        from_attributes = True


class LdapPartialModel(BaseModel):
    ldap_url: str
    ldap_port: str
    bind_dn: str
    bind_credentials: str


class VirtualMachine(Base):
    __tablename__ = "virtual_machines"
    id = Column(Integer, primary_key=True, autoincrement=True)
    hostname = Column(String, nullable=False)
    roles = Column(String, nullable=False)
    group = Column(String, nullable=False)
    ip = Column(String, nullable=False)
    nb_cpu = Column(Integer, nullable=False)
    ram = Column(Integer, nullable=False)
    os_disk_size = Column(Integer, nullable=False)
    data_disk_size = Column(Integer, nullable=True, default=0)
    zone_id = Column(Integer, ForeignKey("zones.id"), nullable=False)
    zone = relationship("Zone", back_populates="virtual_machines")
    status = Column(String, nullable=False, default="to_create")


class VirtualMachineModel(BaseModel):
    id: int
    hostname: str
    roles: str
    group: str
    ip: str
    nb_cpu: int
    ram: int
    os_disk_size: int
    data_disk_size: Optional[int]
    status: str
    zone_id: int

    class Config:
        from_attributes = True


class Dns(Base):
    __tablename__ = "dns"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    hostname = Column(String, nullable=False)
    ip = Column(String, nullable=False)


class DnsModel(BaseModel):
    id: int
    name: str
    hostname: str
    ip: str

    class Config:
        from_attributes = True


class FlowMatrix(Base):
    __tablename__ = "flow_matrix"
    id = Column(Integer, primary_key=True, autoincrement=True)
    source = Column(String, nullable=False)
    destination = Column(String, nullable=False)
    port = Column(Integer, nullable=False)
    protocol = Column(String, nullable=False)
    is_open = Column(Boolean, nullable=False, default=False)
    description = Column(Text, nullable=True)


class FlowMatrixModel(BaseModel):
    id: int
    source: str
    destination: str
    port: int
    protocol: str
    is_open: bool
    description: Optional[str] = None

    class Config:
        from_attributes = True


class SMTPServer(Base):
    __tablename__ = "smtp_servers"
    id = Column(Integer, primary_key=True, autoincrement=True)
    host = Column(String, nullable=False)
    port = Column(Integer, nullable=False)
    login = Column(String, nullable=True)
    password = Column(String, nullable=True)
    mail_from = Column(String, nullable=False)
    use_tls_ssl = Column(Boolean, nullable=False)
    configuration_id = Column(Integer, ForeignKey("configurations.id"))
    configuration = relationship("Configuration", back_populates="smtp_servers")


class SMTPServerModel(BaseModel):
    id: int
    host: str
    port: int
    login: Optional[str] = None
    password: Optional[str] = None
    mail_from: str
    use_tls_ssl: bool

    class Config:
        from_attributes = True


# Client-specific service models removed - ArcgisServer, PaymentProvider, PublishingProvider
# These were specific to a particular client implementation


class SMSProvider(Base):
    __tablename__ = "sms_providers"
    id = Column(Integer, primary_key=True, autoincrement=True)
    url = Column(String, nullable=False)
    login = Column(String, nullable=False)
    password = Column(String, nullable=False)
    binder = Column(String, nullable=False)
    configuration_id = Column(Integer, ForeignKey("configurations.id"))
    configuration = relationship("Configuration", back_populates="sms_providers")


class SMSProviderModel(BaseModel):
    id: int
    url: str
    login: str
    password: str
    binder: str

    class Config:
        from_attributes = True


# Client-specific service models removed:
# - FirebaseDb, Fcm (Firebase/FCM push notifications - client-specific)
# - Google (Google ReCaptcha, OAuth - client-specific)
# - Facebook (Facebook OAuth - client-specific)
# - SignatureService (E-signature service - client-specific)


# Client-specific service models removed:
# - AlfrescoServer (Document management - client-specific)
# - AuthServer (Custom auth service - client-specific)
# - GCBOServer (Client-specific business application)
# - GMAOServer (Client-specific maintenance application)


class Zone(Base):
    __tablename__ = "zones"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    sub_network = Column(String, nullable=False)
    network_mask = Column(Integer, nullable=False)
    dns = Column(String, nullable=False)
    hypervisor_type = Column(String, nullable=False)  # can be vmware or nutanix
    gateway = Column(String, nullable=False)
    domain = Column(String, nullable=False, default="local")
    vlan_name = Column(String, nullable=False)
    ip_pool_start = Column(String, nullable=False)
    ip_pool_end = Column(String, nullable=False)

    vmware_id = Column(Integer, ForeignKey("vmware_esxi.id"), nullable=True)
    vmware = relationship("VMwareEsxi", back_populates="zones")
    nutanix_id = Column(Integer, ForeignKey("nutanix_ahv.id"), nullable=True)
    nutanix = relationship("NutanixAHV", back_populates="zones")

    virtual_machines = relationship("VirtualMachine", back_populates="zone")


class ZoneModel(BaseModel):
    id: int
    name: str
    sub_network: str
    network_mask: int
    dns: str
    hypervisor_type: str
    gateway: str
    domain: str
    vlan_name: str
    ip_pool_start: str
    ip_pool_end: Optional[str] = None

    class Config:
        from_attributes = True


class Vault(Base):
    __tablename__ = "vault"
    id = Column(Integer, primary_key=True, autoincrement=True)
    unseal_keys = Column(String, nullable=False)
    token = Column(String, nullable=False)


class VaultModel(BaseModel):
    id: int
    unseal_keys: str
    token: str


class AnsibleRole(Base):
    __tablename__ = "ansible_roles"
    id = Column(Integer, primary_key=True, autoincrement=True)
    role_name = Column(String, nullable=False)
    order = Column(Integer, nullable=False)
    runner_ident = Column(String, nullable=True, unique=True)
    status = Column(String, nullable=False)
    # start_time = Column(DateTime, default=datetime.now())
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime)

    task_logs = relationship("TaskLog", back_populates="ansible_role")


class VMConfiguration(Base):
    __tablename__ = "vm_configurations"
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_count = Column(Integer, nullable=False)
    vm_type = Column(String, nullable=False)
    node_count = Column(Integer, nullable=False)
    cpu_per_node = Column(Integer, nullable=False)
    ram_per_node = Column(Integer, nullable=False)
    os_disk_size = Column(Integer, nullable=False)
    data_disk_size = Column(Integer, nullable=True, default=0)
    roles = Column(String, nullable=False)


class AnsibleRoleModel(BaseModel):
    id: int
    role_name: str
    order: int
    runner_ident: Optional[str]
    status: str
    start_time: datetime
    end_time: Optional[datetime]

    class Config:
        from_attributes = True


class VMConfigurationModel(BaseModel):
    id: int
    user_count: int
    vm_type: str
    node_count: int
    cpu_per_node: int
    ram_per_node: int
    os_disk_size: int
    data_disk_size: int
    roles: str

    class Config:
        from_attributes = True


class TaskLog(Base):
    __tablename__ = "task_logs"
    id = Column(Integer, primary_key=True, autoincrement=True)
    event = Column(String, nullable=False)
    task = Column(String, nullable=False)
    # runner_ident = Column(String, nullable=False)
    stdout = Column(Text)
    runner_ident = Column(String, ForeignKey("ansible_roles.runner_ident"))
    ansible_role = relationship("AnsibleRole", back_populates="task_logs")


class TaskLogModel(BaseModel):
    id: int
    event: str
    task: str
    runner_ident: str
    stdout: str

    class Config:
        from_attributes = True


class Configuration(Base):
    __tablename__ = "configurations"
    id = Column(Integer, primary_key=True)
    number_concurrent_users = Column(Integer, nullable=False)
    monitoring = relationship(
        "Monitoring", uselist=False, back_populates="configuration"
    )
    security = relationship("Security", uselist=False, back_populates="configuration")
    # products relationship removed - no longer using product-based system
    applications = relationship(
        "Application",
        back_populates="configuration",
    )
    vmwares = relationship(
        "VMwareEsxi",
        back_populates="configuration",
    )
    nutanixs = relationship(
        "NutanixAHV",
        back_populates="configuration",
    )
    databases = relationship(
        "Database",
        back_populates="configuration",
    )
    ldaps = relationship(
        "Ldap",
        back_populates="configuration",
    )
    sms_providers = relationship(
        "SMSProvider",
        back_populates="configuration",
    )
    # Client-specific service relationships removed:
    # google, facebook, arcgis_servers, publishing_providers, payment_providers
    # alfresco_server, firebase_db, fcm, signature, auth_server, gcbo_server, gmao_server
    smtp_servers = relationship(
        "SMTPServer",
        back_populates="configuration",
    )

    current_step = Column(Integer, nullable=False, default=0)


class ConfigurationModel(BaseModel):
    id: int
    number_concurrent_users: int
    monitoring: Optional[MonitoringModel]
    security: Optional[SecurityModel]
    # products removed - no longer using product-based system
    vmwares: List[VMwareEsxiModel]
    nutanixs: List[NutanixAHVModel]
    databases: List[DatabaseModel]
    ldaps: List[LdapModel]
    sms_providers: List[SMSProviderModel]
    # Client-specific services removed from ConfigurationModel:
    # google, facebook, firebase_db, fcm, signature, arcgis_servers
    # publishing_providers, payment_providers, alfresco_server
    # auth_server, gcbo_server, gmao_server
    smtp_servers: List[SMTPServerModel]
    current_step: int

    class Config:
        from_attributes = True
