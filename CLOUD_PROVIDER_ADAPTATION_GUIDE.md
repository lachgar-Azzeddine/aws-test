# Cloud Provider Adaptation Guide

**Purpose:** Adapt the platform to use cloud providers (AWS, Azure, GCP, Oracle Cloud) instead of on-premise hypervisors (VMware vSphere, Nutanix AHV).

**Target Use Case:** Deploy the SRM-CS platform on cloud infrastructure for testing, development, or cloud-native production deployments.

---

## 🎯 What Stays the Same vs What Changes

### ✅ Components That Stay 100% Unchanged

These parts of the platform work identically regardless of where VMs run:

| Component | Reason |
|-----------|--------|
| **Ansible roles (post-provisioning)** | Work on any Linux VM with SSH |
| **prepare-vms** | SSH key setup works anywhere |
| **install-vault** | Installs Vault on any VM |
| **install-rke2-\*** | Kubernetes works on any VMs |
| **install-docker-registry** | Docker works anywhere |
| **install-gogs, argocd, etc.** | All application roles unchanged |
| **Backend API** | Business logic unchanged |
| **Frontend** | UI unchanged (except hypervisor config step) |
| **Database schema** | Core tables unchanged |

**Key insight:** Once VMs exist with SSH access, everything else is identical.

---

### 🔧 Components That Need Changes

| Component | Current (On-Premise) | Cloud Adaptation Needed |
|-----------|---------------------|------------------------|
| **VM Provisioning Roles** | VMware/Nutanix APIs | Cloud provider SDKs (boto3, azure-mgmt, etc.) |
| **Hypervisor Config Table** | `vmware_esxi`, `nutanix` | New table: `cloud_providers` |
| **Repository Functions** | `add_vmware_esxi_configuration()` | `add_cloud_provider_configuration()` |
| **Frontend Wizard** | VMware/Nutanix form | Cloud provider form (region, VPC, etc.) |
| **Network Model** | VLANs, port groups | VPCs, subnets, security groups |
| **IP Assignment** | Hypervisor DHCP/static | Cloud provider network interface |

---

## 🏗️ Architecture: On-Premise vs Cloud

### Current On-Premise Flow

```
1. User configures VMware/Nutanix in frontend
   ↓
2. Backend stores in vmware_esxi or nutanix table
   ↓
3. Ansible role: provisionnement-vms-*
   - Uses pyvmomi (VMware) or REST API (Nutanix)
   - Creates VMs on hypervisor
   - Assigns IPs from VLAN
   ↓
4. VMs exist with SSH access
   ↓
5. All other Ansible roles run normally
```

### Cloud Provider Flow (Target)

```
1. User configures Cloud Provider in frontend
   ↓
2. Backend stores in cloud_providers table
   ↓
3. Ansible role: provisionnement-vms-cloud-*
   - Uses boto3 (AWS) or azure-mgmt (Azure) or gcp SDK
   - Creates VMs on cloud provider
   - Assigns IPs from VPC subnet
   ↓
4. VMs exist with SSH access
   ↓
5. All other Ansible roles run normally (UNCHANGED)
```

**Key takeaway:** Only steps 1-3 need adaptation. Steps 4-5 are identical.

---

## 📊 Detailed Changes by Layer

---

## 1️⃣ Database Schema Changes

### Current Tables (On-Premise)

```sql
-- VMware hypervisor configuration
CREATE TABLE vmware_esxi (
    id SERIAL PRIMARY KEY,
    alias VARCHAR NOT NULL,
    login VARCHAR NOT NULL,
    password VARCHAR NOT NULL,
    api_url VARCHAR NOT NULL,
    datacenter_name VARCHAR,
    cluster_name VARCHAR,
    datastore_name VARCHAR,
    resource_pool_name VARCHAR,
    is_connected BOOLEAN
);

-- Nutanix hypervisor configuration
CREATE TABLE nutanix (
    id SERIAL PRIMARY KEY,
    alias VARCHAR NOT NULL,
    login VARCHAR NOT NULL,
    password VARCHAR NOT NULL,
    api_url VARCHAR NOT NULL,
    cluster_name VARCHAR,
    network_name VARCHAR,
    is_connected BOOLEAN
);
```

### New Table (Cloud Providers)

**Option A: Single Generic Table**

```sql
CREATE TABLE cloud_providers (
    id SERIAL PRIMARY KEY,
    alias VARCHAR NOT NULL,                  -- User-friendly name
    provider_type VARCHAR NOT NULL,          -- 'aws', 'azure', 'gcp', 'oracle'

    -- Authentication
    access_key_id VARCHAR,                   -- AWS: Access Key ID
    secret_access_key VARCHAR,               -- AWS: Secret Access Key (encrypted)
    subscription_id VARCHAR,                 -- Azure: Subscription ID
    tenant_id VARCHAR,                       -- Azure: Tenant ID
    client_id VARCHAR,                       -- Azure: Client ID
    client_secret VARCHAR,                   -- Azure: Client Secret (encrypted)
    project_id VARCHAR,                      -- GCP: Project ID
    service_account_json TEXT,               -- GCP: Service Account JSON (encrypted)

    -- Region and Network
    region VARCHAR NOT NULL,                 -- e.g., 'us-east-1', 'westeurope', 'us-ashburn-1'
    vpc_id VARCHAR,                          -- VPC ID or VNet ID
    vpc_name VARCHAR,                        -- VPC/VNet name

    -- Compute Defaults
    default_instance_type VARCHAR,           -- e.g., 't3.medium', 'Standard_D2s_v3'
    default_image_id VARCHAR,                -- AMI ID, Image ID, etc.
    default_key_pair_name VARCHAR,           -- SSH key pair name in cloud provider
    default_security_group_id VARCHAR,       -- Security group or Network Security Group

    -- Storage Defaults
    default_volume_type VARCHAR,             -- e.g., 'gp3', 'Premium_LRS'

    -- Metadata
    is_connected BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Option B: Provider-Specific Tables**

```sql
-- AWS Configuration
CREATE TABLE aws_providers (
    id SERIAL PRIMARY KEY,
    alias VARCHAR NOT NULL,
    access_key_id VARCHAR NOT NULL,
    secret_access_key VARCHAR NOT NULL,     -- Encrypted
    region VARCHAR NOT NULL,                 -- e.g., 'us-east-1'
    vpc_id VARCHAR,
    default_ami_id VARCHAR,                  -- Default Amazon Linux 2 or Rocky Linux AMI
    default_instance_type VARCHAR,           -- e.g., 't3.medium'
    default_key_pair_name VARCHAR,           -- SSH key pair name
    default_security_group_id VARCHAR,
    is_connected BOOLEAN DEFAULT FALSE
);

-- Azure Configuration
CREATE TABLE azure_providers (
    id SERIAL PRIMARY KEY,
    alias VARCHAR NOT NULL,
    subscription_id VARCHAR NOT NULL,
    tenant_id VARCHAR NOT NULL,
    client_id VARCHAR NOT NULL,
    client_secret VARCHAR NOT NULL,          -- Encrypted
    region VARCHAR NOT NULL,                 -- e.g., 'westeurope'
    resource_group_name VARCHAR NOT NULL,
    vnet_id VARCHAR,
    default_vm_size VARCHAR,                 -- e.g., 'Standard_D2s_v3'
    default_image_publisher VARCHAR,         -- e.g., 'RedHat'
    default_image_offer VARCHAR,             -- e.g., 'RHEL'
    default_image_sku VARCHAR,               -- e.g., '9-lvm-gen2'
    is_connected BOOLEAN DEFAULT FALSE
);

-- GCP Configuration
CREATE TABLE gcp_providers (
    id SERIAL PRIMARY KEY,
    alias VARCHAR NOT NULL,
    project_id VARCHAR NOT NULL,
    service_account_json TEXT NOT NULL,      -- Encrypted JSON key
    region VARCHAR NOT NULL,                 -- e.g., 'us-central1'
    zone VARCHAR NOT NULL,                   -- e.g., 'us-central1-a'
    vpc_name VARCHAR,
    default_machine_type VARCHAR,            -- e.g., 'n1-standard-2'
    default_image_family VARCHAR,            -- e.g., 'rocky-linux-9'
    default_image_project VARCHAR,           -- e.g., 'rocky-linux-cloud'
    is_connected BOOLEAN DEFAULT FALSE
);

-- Oracle Cloud Configuration
CREATE TABLE oracle_cloud_providers (
    id SERIAL PRIMARY KEY,
    alias VARCHAR NOT NULL,
    tenancy_ocid VARCHAR NOT NULL,
    user_ocid VARCHAR NOT NULL,
    fingerprint VARCHAR NOT NULL,
    private_key TEXT NOT NULL,               -- Encrypted PEM key
    region VARCHAR NOT NULL,                 -- e.g., 'us-ashburn-1'
    compartment_ocid VARCHAR NOT NULL,
    vcn_ocid VARCHAR,
    default_shape VARCHAR,                   -- e.g., 'VM.Standard.E3.Flex'
    default_image_ocid VARCHAR,              -- Oracle Linux or Rocky Linux image
    is_connected BOOLEAN DEFAULT FALSE
);
```

**Recommendation:** Use **Option B (provider-specific tables)** because:
- Each cloud provider has unique authentication mechanisms
- Cleaner schema (no nullable fields for irrelevant providers)
- Easier validation per provider

---

## 2️⃣ Repository Layer Changes

### New Functions to Add

**File:** `backend/repository.py`

```python
# ============================================================================
# AWS Provider Functions
# ============================================================================

def add_aws_provider(alias, access_key_id, secret_access_key, region, vpc_id,
                     default_ami_id, default_instance_type, default_key_pair_name,
                     default_security_group_id, Session):
    """Add AWS provider configuration."""
    if Session is None:
        print("Session is not initialized")
        return None

    session = Session()

    # Encrypt secret access key
    encrypted_secret = encrypt_password(secret_access_key)

    aws_provider = AWSProvider(
        alias=alias,
        access_key_id=access_key_id,
        secret_access_key=encrypted_secret,
        region=region,
        vpc_id=vpc_id,
        default_ami_id=default_ami_id,
        default_instance_type=default_instance_type,
        default_key_pair_name=default_key_pair_name,
        default_security_group_id=default_security_group_id,
        is_connected=False
    )

    session.add(aws_provider)
    session.commit()
    provider_id = aws_provider.id
    session.close()

    return provider_id

def get_aws_provider(Session):
    """Get AWS provider configuration."""
    if Session is None:
        print("Session is not initialized")
        return None

    session = Session()
    provider = session.query(AWSProvider).first()
    session.close()

    return provider

def update_aws_provider(provider_id, **kwargs):
    """Update AWS provider configuration."""
    # Similar to update_vmware_esxi_configuration
    pass

# ============================================================================
# Azure Provider Functions
# ============================================================================

def add_azure_provider(alias, subscription_id, tenant_id, client_id, client_secret,
                       region, resource_group_name, vnet_id, default_vm_size,
                       default_image_publisher, default_image_offer,
                       default_image_sku, Session):
    """Add Azure provider configuration."""
    if Session is None:
        print("Session is not initialized")
        return None

    session = Session()

    # Encrypt client secret
    encrypted_secret = encrypt_password(client_secret)

    azure_provider = AzureProvider(
        alias=alias,
        subscription_id=subscription_id,
        tenant_id=tenant_id,
        client_id=client_id,
        client_secret=encrypted_secret,
        region=region,
        resource_group_name=resource_group_name,
        vnet_id=vnet_id,
        default_vm_size=default_vm_size,
        default_image_publisher=default_image_publisher,
        default_image_offer=default_image_offer,
        default_image_sku=default_image_sku,
        is_connected=False
    )

    session.add(azure_provider)
    session.commit()
    provider_id = azure_provider.id
    session.close()

    return provider_id

def get_azure_provider(Session):
    """Get Azure provider configuration."""
    if Session is None:
        print("Session is not initialized")
        return None

    session = Session()
    provider = session.query(AzureProvider).first()
    session.close()

    return provider

# ============================================================================
# Generic Cloud Provider Detection
# ============================================================================

def get_active_cloud_provider(Session):
    """
    Get the active cloud provider configuration.
    Returns: (provider_type, provider_object)
    provider_type: 'aws', 'azure', 'gcp', 'oracle', 'vmware', 'nutanix'
    """
    if Session is None:
        print("Session is not initialized")
        return None, None

    session = Session()

    # Check AWS
    aws = session.query(AWSProvider).first()
    if aws:
        session.close()
        return 'aws', aws

    # Check Azure
    azure = session.query(AzureProvider).first()
    if azure:
        session.close()
        return 'azure', azure

    # Check GCP
    gcp = session.query(GCPProvider).first()
    if gcp:
        session.close()
        return 'gcp', gcp

    # Check Oracle
    oracle = session.query(OracleCloudProvider).first()
    if oracle:
        session.close()
        return 'oracle', oracle

    # Check VMware (existing)
    vmware = session.query(VMwareESXi).first()
    if vmware:
        session.close()
        return 'vmware', vmware

    # Check Nutanix (existing)
    nutanix = session.query(Nutanix).first()
    if nutanix:
        session.close()
        return 'nutanix', nutanix

    session.close()
    return None, None
```

---

## 3️⃣ Database Models (SQLAlchemy)

**File:** `backend/models.py`

Add new model classes:

```python
from sqlalchemy import Column, Integer, String, Boolean, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

# ============================================================================
# AWS Provider Model
# ============================================================================

class AWSProvider(Base):
    __tablename__ = "aws_providers"

    id = Column(Integer, primary_key=True, index=True)
    alias = Column(String, nullable=False)
    access_key_id = Column(String, nullable=False)
    secret_access_key = Column(String, nullable=False)  # Encrypted
    region = Column(String, nullable=False)
    vpc_id = Column(String)
    default_ami_id = Column(String)
    default_instance_type = Column(String, default='t3.medium')
    default_key_pair_name = Column(String)
    default_security_group_id = Column(String)
    is_connected = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# ============================================================================
# Azure Provider Model
# ============================================================================

class AzureProvider(Base):
    __tablename__ = "azure_providers"

    id = Column(Integer, primary_key=True, index=True)
    alias = Column(String, nullable=False)
    subscription_id = Column(String, nullable=False)
    tenant_id = Column(String, nullable=False)
    client_id = Column(String, nullable=False)
    client_secret = Column(String, nullable=False)  # Encrypted
    region = Column(String, nullable=False)
    resource_group_name = Column(String, nullable=False)
    vnet_id = Column(String)
    default_vm_size = Column(String, default='Standard_D2s_v3')
    default_image_publisher = Column(String, default='RedHat')
    default_image_offer = Column(String, default='RHEL')
    default_image_sku = Column(String, default='9-lvm-gen2')
    is_connected = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# ============================================================================
# GCP Provider Model
# ============================================================================

class GCPProvider(Base):
    __tablename__ = "gcp_providers"

    id = Column(Integer, primary_key=True, index=True)
    alias = Column(String, nullable=False)
    project_id = Column(String, nullable=False)
    service_account_json = Column(Text, nullable=False)  # Encrypted
    region = Column(String, nullable=False)
    zone = Column(String, nullable=False)
    vpc_name = Column(String)
    default_machine_type = Column(String, default='n1-standard-2')
    default_image_family = Column(String, default='rocky-linux-9')
    default_image_project = Column(String, default='rocky-linux-cloud')
    is_connected = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# ============================================================================
# Oracle Cloud Provider Model
# ============================================================================

class OracleCloudProvider(Base):
    __tablename__ = "oracle_cloud_providers"

    id = Column(Integer, primary_key=True, index=True)
    alias = Column(String, nullable=False)
    tenancy_ocid = Column(String, nullable=False)
    user_ocid = Column(String, nullable=False)
    fingerprint = Column(String, nullable=False)
    private_key = Column(Text, nullable=False)  # Encrypted PEM
    region = Column(String, nullable=False)
    compartment_ocid = Column(String, nullable=False)
    vcn_ocid = Column(String)
    default_shape = Column(String, default='VM.Standard.E3.Flex')
    default_image_ocid = Column(String)
    is_connected = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
```

---

## 4️⃣ API Endpoints

**File:** `backend/api.py`

Add new endpoints for cloud provider management:

```python
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter()

# ============================================================================
# AWS Provider Endpoints
# ============================================================================

class AWSProviderCreate(BaseModel):
    alias: str
    access_key_id: str
    secret_access_key: str
    region: str
    vpc_id: str = None
    default_ami_id: str = None
    default_instance_type: str = "t3.medium"
    default_key_pair_name: str = None
    default_security_group_id: str = None

@router.post("/cloud/aws")
def create_aws_provider(provider: AWSProviderCreate):
    """Add AWS provider configuration."""
    provider_id = add_aws_provider(
        alias=provider.alias,
        access_key_id=provider.access_key_id,
        secret_access_key=provider.secret_access_key,
        region=provider.region,
        vpc_id=provider.vpc_id,
        default_ami_id=provider.default_ami_id,
        default_instance_type=provider.default_instance_type,
        default_key_pair_name=provider.default_key_pair_name,
        default_security_group_id=provider.default_security_group_id,
        Session=Session
    )
    return {"id": provider_id, "message": "AWS provider added successfully"}

@router.get("/cloud/aws")
def read_aws_provider():
    """Get AWS provider configuration."""
    provider = get_aws_provider(Session)
    if not provider:
        raise HTTPException(status_code=404, detail="AWS provider not configured")

    # Don't return encrypted secrets
    return {
        "id": provider.id,
        "alias": provider.alias,
        "region": provider.region,
        "vpc_id": provider.vpc_id,
        "is_connected": provider.is_connected
    }

# ============================================================================
# Azure Provider Endpoints
# ============================================================================

class AzureProviderCreate(BaseModel):
    alias: str
    subscription_id: str
    tenant_id: str
    client_id: str
    client_secret: str
    region: str
    resource_group_name: str
    vnet_id: str = None
    default_vm_size: str = "Standard_D2s_v3"
    default_image_publisher: str = "RedHat"
    default_image_offer: str = "RHEL"
    default_image_sku: str = "9-lvm-gen2"

@router.post("/cloud/azure")
def create_azure_provider(provider: AzureProviderCreate):
    """Add Azure provider configuration."""
    provider_id = add_azure_provider(
        alias=provider.alias,
        subscription_id=provider.subscription_id,
        tenant_id=provider.tenant_id,
        client_id=provider.client_id,
        client_secret=provider.client_secret,
        region=provider.region,
        resource_group_name=provider.resource_group_name,
        vnet_id=provider.vnet_id,
        default_vm_size=provider.default_vm_size,
        default_image_publisher=provider.default_image_publisher,
        default_image_offer=provider.default_image_offer,
        default_image_sku=provider.default_image_sku,
        Session=Session
    )
    return {"id": provider_id, "message": "Azure provider added successfully"}

@router.get("/cloud/azure")
def read_azure_provider():
    """Get Azure provider configuration."""
    provider = get_azure_provider(Session)
    if not provider:
        raise HTTPException(status_code=404, detail="Azure provider not configured")

    return {
        "id": provider.id,
        "alias": provider.alias,
        "region": provider.region,
        "resource_group_name": provider.resource_group_name,
        "is_connected": provider.is_connected
    }

# ============================================================================
# Generic Cloud Provider Endpoint
# ============================================================================

@router.get("/cloud/active")
def get_active_provider():
    """Get the currently configured cloud/hypervisor provider."""
    provider_type, provider = get_active_cloud_provider(Session)

    if not provider:
        raise HTTPException(status_code=404, detail="No provider configured")

    return {
        "provider_type": provider_type,
        "alias": provider.alias,
        "is_connected": provider.is_connected
    }
```

---

## 5️⃣ Ansible Roles - VM Provisioning

### Current Roles (On-Premise)

```
backend/project/roles/
├── provisionnement-vms-infra/     # VMware/Nutanix API
├── provisionnement-vms-apps/      # VMware/Nutanix API
└── provisionnement-vms-dmz/       # VMware/Nutanix API
```

### New Roles (Cloud)

Create cloud-specific provisioning roles:

```
backend/project/roles/
├── provisionnement-vms-cloud-aws/
├── provisionnement-vms-cloud-azure/
├── provisionnement-vms-cloud-gcp/
└── provisionnement-vms-cloud-oracle/
```

---

### Example: AWS Provisioning Role

**Directory structure:**

```
backend/project/roles/provisionnement-vms-cloud-aws/
├── prepare_inputs.py
├── tasks/
│   └── main.yml
└── requirements.txt
```

**File:** `prepare_inputs.py`

```python
from repository import (
    get_session,
    get_aws_provider,
    get_virtual_machines,
    get_security,
    decrypt_password
)
import base64

def get_inputs(Session):
    """
    Prepare variables for AWS VM provisioning.
    """

    # Get AWS provider config
    aws = get_aws_provider(Session)
    if not aws:
        raise Exception("AWS provider not configured")

    # Get VMs to provision
    vms = get_virtual_machines(Session)
    if not vms:
        raise Exception("No VMs to provision")

    # Get security settings (for SSH keys, cloud-init)
    security = get_security(Session)

    # Decrypt AWS secret access key
    secret_key = decrypt_password(aws.secret_access_key)

    # Prepare extra variables
    extra_vars = {
        # AWS credentials
        "aws_access_key_id": aws.access_key_id,
        "aws_secret_access_key": secret_key,
        "aws_region": aws.region,

        # Default settings
        "vpc_id": aws.vpc_id,
        "default_ami_id": aws.default_ami_id,
        "default_instance_type": aws.default_instance_type,
        "default_key_pair_name": aws.default_key_pair_name,
        "default_security_group_id": aws.default_security_group_id,

        # SSH public key (for cloud-init)
        "ssh_public_key": security.ssh_pulic_key,

        # VMs to create
        "vms_to_create": [
            {
                "hostname": vm.hostname,
                "ip": vm.ip,
                "zone_id": vm.zone_id,
                "cpu": vm.nb_cpu,
                "ram": vm.ram,
                "os_disk_size": vm.os_disk_size,
                "data_disk_size": vm.data_disk_size,
                "roles": vm.roles,

                # Map CPU/RAM to AWS instance type
                "instance_type": map_to_aws_instance_type(vm.nb_cpu, vm.ram),
            }
            for vm in vms
        ]
    }

    # Inventory (local execution)
    inventory = {
        "all": {
            "hosts": {
                "localhost": {
                    "ansible_host": "127.0.0.1",
                    "ansible_connection": "local"
                }
            }
        }
    }

    return extra_vars, inventory


def map_to_aws_instance_type(cpu, ram_mb):
    """
    Map CPU/RAM requirements to AWS instance types.
    ram_mb: RAM in MB
    """
    ram_gb = ram_mb / 1024

    # Mapping table: (cpu, ram_gb) -> instance_type
    if cpu == 2 and ram_gb <= 4:
        return "t3.medium"      # 2 vCPU, 4 GB
    elif cpu == 2 and ram_gb <= 8:
        return "t3.large"       # 2 vCPU, 8 GB
    elif cpu == 4 and ram_gb <= 8:
        return "t3.xlarge"      # 4 vCPU, 16 GB (closest match)
    elif cpu == 4 and ram_gb <= 16:
        return "m5.xlarge"      # 4 vCPU, 16 GB
    elif cpu == 8 and ram_gb <= 32:
        return "m5.2xlarge"     # 8 vCPU, 32 GB
    else:
        # Default to reasonable size
        return "t3.xlarge"
```

**File:** `tasks/main.yml`

```yaml
---
- name: Provision VMs on AWS
  hosts: localhost
  gather_facts: no
  vars:
    ansible_python_interpreter: /usr/bin/python3

  tasks:
    - name: Install boto3 and botocore
      pip:
        name:
          - boto3
          - botocore
        state: present

    - name: Create cloud-init user data
      set_fact:
        cloud_init_user_data: |
          #cloud-config
          users:
            - name: devops
              sudo: ALL=(ALL) NOPASSWD:ALL
              shell: /bin/bash
              ssh_authorized_keys:
                - {{ ssh_public_key }}

          # Enable password authentication temporarily
          ssh_pwauth: true

          # Set initial password
          chpasswd:
            list: |
              devops:devops
            expire: false

          # System updates
          package_update: true
          package_upgrade: false

          packages:
            - python3
            - python3-pip

    - name: Create EC2 instances
      amazon.aws.ec2_instance:
        aws_access_key: "{{ aws_access_key_id }}"
        aws_secret_key: "{{ aws_secret_access_key }}"
        region: "{{ aws_region }}"

        name: "{{ item.hostname }}"
        instance_type: "{{ item.instance_type }}"
        image_id: "{{ default_ami_id }}"
        key_name: "{{ default_key_pair_name }}"
        vpc_subnet_id: "{{ vpc_id }}"
        security_group: "{{ default_security_group_id }}"

        # Network configuration
        network:
          assign_public_ip: true
          private_ip_address: "{{ item.ip }}"

        # Volumes
        volumes:
          - device_name: /dev/sda1
            ebs:
              volume_size: "{{ item.os_disk_size }}"
              volume_type: gp3
              delete_on_termination: true

          - device_name: /dev/sdb
            ebs:
              volume_size: "{{ item.data_disk_size }}"
              volume_type: gp3
              delete_on_termination: true

        # User data (cloud-init)
        user_data: "{{ cloud_init_user_data }}"

        # Tags
        tags:
          Name: "{{ item.hostname }}"
          Environment: "{{ env_prefix | default('dev') }}"
          Roles: "{{ item.roles }}"
          Zone: "{{ item.zone_id }}"

        state: running
        wait: yes
        wait_timeout: 600
      loop: "{{ vms_to_create }}"
      register: ec2_instances

    - name: Wait for SSH to become available
      wait_for:
        host: "{{ item.public_ip_address }}"
        port: 22
        delay: 30
        timeout: 300
        state: started
      loop: "{{ ec2_instances.results }}"
      when: item.public_ip_address is defined

    - name: Display created instances
      debug:
        msg: "Created {{ item.tags.Name }} with IP {{ item.public_ip_address }}"
      loop: "{{ ec2_instances.results }}"
```

**File:** `requirements.txt`

```
boto3>=1.26.0
botocore>=1.29.0
ansible>=2.14.0
```

---

## 6️⃣ Network Zones - Cloud Adaptation

### Current Network Model (On-Premise)

```python
# Zone table
class Zone:
    id = Column(Integer, primary_key=True)
    name = Column(String)           # LAN_INFRA, LAN_APPS, DMZ
    sub_network = Column(String)    # 10.1.10.0
    network_mask = Column(String)   # 24
    gateway = Column(String)        # 10.1.10.1
    dns = Column(String)            # 8.8.8.8
    vlan = Column(String)           # VLAN10
    ip_range_start = Column(String) # 10.1.10.10
    ip_range_end = Column(String)   # 10.1.10.50
    hypervisor_id = Column(Integer) # FK to vmware_esxi or nutanix
```

**Usage:** Zones represent VLANs on on-premise network

### Cloud Network Model (Adaptation)

**Option 1: Extend Zone Table (Recommended)**

Add cloud-specific fields:

```python
class Zone:
    # ... existing fields ...

    # Cloud-specific fields
    cloud_provider_id = Column(Integer)      # FK to cloud provider
    cloud_vpc_id = Column(String)            # AWS VPC, Azure VNet, GCP VPC
    cloud_subnet_id = Column(String)         # Subnet ID in cloud provider
    cloud_security_group_id = Column(String) # Security group ID
    cloud_route_table_id = Column(String)    # Route table ID (if needed)
```

**Why this works:**
- `sub_network`, `network_mask` still define IP range
- `cloud_subnet_id` maps to actual subnet in cloud
- Same zone logic applies (INFRA, APPS, DMZ)

**Example:**

```python
# On-premise zone
Zone(
    name="LAN_INFRA",
    sub_network="10.1.10.0",
    network_mask="24",
    vlan="VLAN10",
    hypervisor_id=1  # VMware
)

# AWS zone
Zone(
    name="LAN_INFRA",
    sub_network="10.1.10.0",
    network_mask="24",
    cloud_provider_id=1,         # AWS provider
    cloud_vpc_id="vpc-abc123",
    cloud_subnet_id="subnet-def456",
    cloud_security_group_id="sg-ghi789"
)
```

---

## 7️⃣ Frontend Changes

### Current Frontend (On-Premise)

**Wizard Step 1:** Hypervisor Configuration

```
┌─────────────────────────────────────┐
│ Select Hypervisor Type              │
│ ○ VMware vSphere                    │
│ ○ Nutanix AHV                       │
│                                     │
│ [VMware Form]                       │
│ - vCenter URL                       │
│ - Username                          │
│ - Password                          │
│ - Datacenter                        │
│ - Cluster                           │
│ - Datastore                         │
└─────────────────────────────────────┘
```

### Cloud Frontend (Adaptation)

**Wizard Step 1:** Infrastructure Provider

```
┌─────────────────────────────────────┐
│ Select Infrastructure Provider      │
│ ○ VMware vSphere                    │
│ ○ Nutanix AHV                       │
│ ○ Amazon Web Services (AWS)         │
│ ○ Microsoft Azure                   │
│ ○ Google Cloud Platform (GCP)       │
│ ○ Oracle Cloud Infrastructure (OCI) │
│                                     │
│ [AWS Form]                          │
│ - Alias: ___________________        │
│ - Access Key ID: ___________        │
│ - Secret Access Key: ________       │
│ - Region: [us-east-1 ▼]            │
│ - VPC ID: vpc-____________          │
│ - AMI ID (optional): ________       │
│ - Instance Type: [t3.medium ▼]     │
│ - Key Pair Name: ___________        │
│ - Security Group: ___________       │
│                                     │
│ [Test Connection] [Next]            │
└─────────────────────────────────────┘
```

**Implementation:** `frontend/src/app/components/hypervisor-config/`

Add new component: `cloud-provider-config.component.ts`

```typescript
export interface CloudProvider {
  providerType: 'aws' | 'azure' | 'gcp' | 'oracle';
  alias: string;
  // Provider-specific fields...
}

// AWS Form
export interface AWSConfig {
  alias: string;
  accessKeyId: string;
  secretAccessKey: string;
  region: string;
  vpcId?: string;
  defaultAmiId?: string;
  defaultInstanceType: string;
  defaultKeyPairName?: string;
  defaultSecurityGroupId?: string;
}
```

---

## 8️⃣ Migration Strategy

### Strategy A: Parallel Support (Recommended)

**Support both on-premise and cloud simultaneously**

```
backend/project/roles/
├── provisionnement-vms-infra/          # VMware/Nutanix (existing)
├── provisionnement-vms-apps/           # VMware/Nutanix (existing)
├── provisionnement-vms-dmz/            # VMware/Nutanix (existing)
├── provisionnement-vms-cloud-aws/      # AWS (new)
├── provisionnement-vms-cloud-azure/    # Azure (new)
└── provisionnement-vms-cloud-gcp/      # GCP (new)
```

**Deployment logic** (`install.py`):

```python
def get_provisioning_roles(Session):
    """Determine which provisioning roles to use based on configured provider."""
    provider_type, provider = get_active_cloud_provider(Session)

    if provider_type == 'aws':
        return [
            "provisionnement-vms-cloud-aws",  # Creates ALL VMs in one role
        ]
    elif provider_type == 'azure':
        return [
            "provisionnement-vms-cloud-azure",
        ]
    elif provider_type == 'gcp':
        return [
            "provisionnement-vms-cloud-gcp",
        ]
    elif provider_type == 'vmware':
        return [
            "provisionnement-vms-infra",
            "provisionnement-vms-apps",
            "provisionnement-vms-dmz",
        ]
    elif provider_type == 'nutanix':
        return [
            "provisionnement-vms-infra",
            "provisionnement-vms-apps",
            "provisionnement-vms-dmz",
        ]
    else:
        raise Exception("No infrastructure provider configured")

# Main role execution
async def install_all_roles(Session):
    # Get provisioning roles based on provider
    provisioning_roles = get_provisioning_roles(Session)

    # Post-provisioning roles (unchanged)
    common_roles = [
        "prepare-vms",
        "install-vault",
        "install-docker-registry",
        "install-gogs",
        "install-rke2-apps",
        "install-argocd",
        # ... etc
    ]

    all_roles = provisioning_roles + common_roles

    # Execute roles
    for role in all_roles:
        await async_call_role(role, Session)
```

---

### Strategy B: Cloud-Only (Simpler)

**Remove on-premise support entirely, focus on cloud**

- Delete VMware/Nutanix roles
- Only support AWS/Azure/GCP
- Simpler codebase
- Good for cloud-native startups

---

## 9️⃣ Testing Cloud Providers

### AWS Free Tier Testing

**What you get free:**
- 750 hours/month of t2.micro or t3.micro (12 months)
- 30 GB EBS storage
- Good for testing 1-2 VMs

**Setup:**
1. Create AWS account
2. Create IAM user with EC2 permissions
3. Create VPC and subnet
4. Create security group (allow SSH port 22)
5. Create key pair
6. Configure in platform frontend

### Oracle Cloud Free Tier (Best for Testing)

**What you get free (ALWAYS):**
- 4 Ampere A1 Compute instances (ARM):
  - Up to 24 GB RAM total
  - Up to 4 OCPUs total
- 200 GB block storage
- Permanent free tier!

**Perfect for your 5-VM setup:**
```
vault1:        1 OCPU, 6 GB RAM
gitops1:       1 OCPU, 6 GB RAM
rkeapp-master: 1 OCPU, 6 GB RAM
rkeapp-worker1: 0.5 OCPU, 3 GB RAM
rkeapp-worker2: 0.5 OCPU, 3 GB RAM
---
Total: 4 OCPUs, 24 GB RAM ✅ (within free tier!)
```

---

## 🔟 Summary - What to Change

### Minimal Changes (MVP)

**To support ONE cloud provider (e.g., AWS):**

| Component | What to Do | Effort |
|-----------|-----------|--------|
| **Database** | Add `aws_providers` table | 30 min |
| **Models** | Add `AWSProvider` class | 15 min |
| **Repository** | Add `add_aws_provider()`, `get_aws_provider()` | 30 min |
| **API** | Add `/cloud/aws` endpoints | 30 min |
| **Ansible Role** | Create `provisionnement-vms-cloud-aws/` | 4 hours |
| **install.py** | Add provider detection logic | 1 hour |
| **Frontend** | Add AWS form to hypervisor wizard step | 2 hours |
| **Total** | | **~9 hours** |

---

### Full Multi-Cloud Support

**To support AWS + Azure + GCP + Oracle + VMware + Nutanix:**

| Component | Effort |
|-----------|--------|
| **Database** | 4 tables | 2 hours |
| **Models** | 4 classes | 1 hour |
| **Repository** | 4 × 3 functions | 3 hours |
| **API** | 4 × 3 endpoints | 3 hours |
| **Ansible Roles** | 4 × 1 role | 16 hours |
| **Provider detection** | 1 logic | 2 hours |
| **Frontend** | 4 forms | 8 hours |
| **Testing** | All providers | 8 hours |
| **Total** | | **~43 hours** |

---

## 📝 Quick Start - AWS Support (Step-by-Step)

### Step 1: Add Database Table

```bash
docker exec -it postgres psql -U harmonisation

CREATE TABLE aws_providers (
    id SERIAL PRIMARY KEY,
    alias VARCHAR NOT NULL,
    access_key_id VARCHAR NOT NULL,
    secret_access_key VARCHAR NOT NULL,
    region VARCHAR NOT NULL,
    vpc_id VARCHAR,
    default_ami_id VARCHAR,
    default_instance_type VARCHAR DEFAULT 't3.medium',
    default_key_pair_name VARCHAR,
    default_security_group_id VARCHAR,
    is_connected BOOLEAN DEFAULT FALSE
);

\q
```

### Step 2: Add Model (models.py)

```python
class AWSProvider(Base):
    __tablename__ = "aws_providers"
    # ... (copy from section 3)
```

### Step 3: Add Repository Functions (repository.py)

```python
def add_aws_provider(...):
    # ... (copy from section 2)

def get_aws_provider(Session):
    # ... (copy from section 2)
```

### Step 4: Add API Endpoints (api.py)

```python
@router.post("/cloud/aws")
def create_aws_provider(...):
    # ... (copy from section 4)
```

### Step 5: Create Ansible Role

```bash
mkdir -p backend/project/roles/provisionnement-vms-cloud-aws/{tasks,templates}
# Create files from section 5
```

### Step 6: Update install.py

```python
def get_provisioning_roles(Session):
    # ... (copy from section 8)
```

### Step 7: Test

```bash
# Configure AWS via API
curl -X POST http://localhost/runner/api/cloud/aws \
  -H "Content-Type: application/json" \
  -d '{
    "alias": "aws-test",
    "access_key_id": "AKIA...",
    "secret_access_key": "...",
    "region": "us-east-1",
    "vpc_id": "vpc-...",
    "default_ami_id": "ami-0c55b159cbfafe1f0"
  }'

# Generate VMs
curl http://localhost/runner/api/virtual-machines

# Start deployment
curl -X POST http://localhost/runner/api/start
```

---

## ✅ Conclusion

**Bottom Line:**

1. **Most of the platform needs NO changes** (80%)
   - All application installation roles
   - Backend business logic
   - Database core tables
   - Frontend (except hypervisor step)

2. **Only VM provisioning layer needs adaptation** (20%)
   - New database tables for cloud providers
   - New Ansible roles for cloud APIs
   - Provider detection logic
   - Frontend hypervisor configuration form

3. **Recommended approach:** Start with **ONE cloud provider** (AWS or Oracle Cloud free tier) to validate the architecture, then expand to others.

4. **Timeline:**
   - MVP (AWS only): **1-2 days**
   - Full multi-cloud: **1-2 weeks**

Your platform's architecture makes this adaptation straightforward because the provisioning layer is cleanly separated from the rest of the deployment workflow! 🎉
