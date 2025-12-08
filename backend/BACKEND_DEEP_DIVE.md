# Backend Deep Dive - Complete Understanding Guide

This document provides a comprehensive explanation of the backend architecture, data flow, and how all components work together. By the end, you'll understand exactly how to customize and modify any part of the system.

---

## Table of Contents

1. [High-Level Architecture](#high-level-architecture)
2. [The Three-Layer Pattern](#the-three-layer-pattern)
3. [Database Layer - models.py](#database-layer---modelspy)
4. [Repository Layer - repository.py](#repository-layer---repositorypy)
5. [API Layer - api.py](#api-layer---apipy)
6. [Ansible Integration - install.py](#ansible-integration---installpy)
7. [Complete Request Flow Examples](#complete-request-flow-examples)
8. [How to Add New Features](#how-to-add-new-features)
9. [Security and Encryption](#security-and-encryption)
10. [Testing and Validation](#testing-and-validation)

---

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         Angular Frontend                         │
│                     (HTTP Requests via API)                      │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    API Layer (api.py)                            │
│  - FastAPI Endpoints (REST)                                      │
│  - Request Validation (Pydantic)                                 │
│  - Response Serialization                                        │
│  - CORS Middleware                                               │
│  - Background Task Management                                    │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│              Repository Layer (repository.py)                    │
│  - Business Logic                                                │
│  - Database Operations (CRUD)                                    │
│  - Password Encryption/Decryption                                │
│  - Data Validation                                               │
│  - External Service Testing (VMware, LDAP, DB)                   │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│               Database Layer (models.py)                         │
│  - SQLAlchemy ORM Models (Tables)                                │
│  - Pydantic Models (API Validation)                              │
│  - Table Relationships                                           │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
                    PostgreSQL Database
                    (Tables, Data Storage)
```

### Separate Orchestration Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                  Ansible Orchestration (install.py)              │
│  - Role Execution Engine                                         │
│  - Dynamic Variable Loading                                      │
│  - Status Tracking                                               │
│  - Log Capture                                                   │
└─────────────────────────────────────────────────────────────────┘
        │                                    ▲
        │ (Executes)                         │ (Queries DB for vars)
        ▼                                    │
┌────────────────────┐            ┌──────────────────────┐
│  Ansible Roles     │            │  prepare_inputs.py   │
│  (34 roles in      │            │  (Per role, queries  │
│   backend/project  │            │   repository.py)     │
│   /roles/)         │            └──────────────────────┘
└────────────────────┘
```

---

## The Three-Layer Pattern

This backend follows a **strict separation of concerns** with three distinct layers. **Never skip layers** - always go through them in order.

### Why Three Layers?

1. **Maintainability**: Changes to database schema don't affect API endpoints
2. **Testability**: Each layer can be tested independently
3. **Security**: Business logic and validation centralized
4. **Reusability**: Repository functions used by both API and Ansible

### Layer Responsibilities

| Layer | File | Purpose | What It Does | What It Never Does |
|-------|------|---------|--------------|-------------------|
| **API** | `api.py` | HTTP Interface | - Define FastAPI endpoints<br>- Validate incoming requests<br>- Call repository functions<br>- Format HTTP responses | - Direct database queries<br>- Business logic<br>- Password encryption |
| **Repository** | `repository.py` | Business Logic & Data Access | - Database CRUD operations<br>- Password encryption/decryption<br>- Complex queries<br>- External service testing | - Define HTTP endpoints<br>- Handle HTTP requests |
| **Database** | `models.py` | Data Structure | - Define SQLAlchemy models (tables)<br>- Define Pydantic models (validation)<br>- Table relationships | - Contain business logic<br>- Handle HTTP |

---

## Database Layer - models.py

### What's in This File?

This file contains **two types of models** for each entity:

1. **SQLAlchemy Models** (Database Tables) - Inherits from `Base`
2. **Pydantic Models** (API Validation & Serialization) - Inherits from `BaseModel`

### Example: VMware Hypervisor

```python
# 1. SQLAlchemy Model (Database Table)
class VMwareEsxi(Base):
    __tablename__ = "vmware_esxi"

    # Primary key
    id = Column(Integer, primary_key=True, autoincrement=True)

    # Data fields
    alias = Column(String, nullable=False)
    login = Column(String, nullable=False)
    password = Column(String, nullable=False)  # Stored encrypted
    api_url = Column(String, nullable=False)

    # Relationships
    configuration_id = Column(Integer, ForeignKey("configurations.id"), nullable=False)
    configuration = relationship("Configuration", back_populates="vmwares")
    zones = relationship("Zone", back_populates="vmware")

# 2. Pydantic Model (API Validation)
class VMwareEsxiModel(BaseModel):
    id: int
    alias: str
    login: str
    password: str
    api_url: str
    type: str = "vmware"

    class Config:
        from_attributes = True  # Allows loading from SQLAlchemy objects
```

### Key Database Tables

| Table | Purpose | Key Relationships |
|-------|---------|------------------|
| **Configuration** | Root configuration (1 per system) | Has many: VMwares, Nutanixs, Databases, Zones |
| **VMwareEsxi** | VMware vCenter configuration | Belongs to: Configuration<br>Has many: Zones |
| **NutanixAHV** | Nutanix hypervisor configuration | Belongs to: Configuration<br>Has many: Zones |
| **Zone** | Network zones (LAN_INFRA, LAN_APPS, DMZ) | Belongs to: VMware or Nutanix<br>Has many: VirtualMachines |
| **VirtualMachine** | VM inventory | Belongs to: Zone |
| **Database** | External database connections | Belongs to: Configuration |
| **Ldap** | LDAP/AD servers | Belongs to: Configuration |
| **Security** | SSH keys, SSL certs, proxy config | Belongs to: Configuration (1-to-1) |
| **AnsibleRole** | Ansible role execution tracking | Has many: TaskLogs |
| **TaskLog** | Ansible task output logs | Belongs to: AnsibleRole |

### Understanding Relationships

```python
# One-to-Many: Configuration → VMwareEsxi
configuration.vmwares  # List of all VMware configs
vmware.configuration   # Parent configuration

# One-to-Many: Zone → VirtualMachine
zone.virtual_machines  # All VMs in this zone
vm.zone                # Parent zone

# One-to-Many: AnsibleRole → TaskLog
ansible_role.task_logs  # All logs for this role execution
task_log.ansible_role   # Parent role execution
```

---

## Repository Layer - repository.py

This is the **heart of the backend** - 3,635 lines of business logic and database operations.

### Key Responsibilities

1. **Database Session Management**
2. **CRUD Operations** (Create, Read, Update, Delete)
3. **Password Encryption/Decryption**
4. **External Service Testing** (VMware, Nutanix, LDAP, Databases)
5. **Complex Queries** (Joins, Filters, Aggregations)
6. **VM Architecture Scaffolding**

### Session Management Pattern

Every function follows this pattern:

```python
def add_vmware_esxi_configuration(
    alias, login, password, api_url, ..., Session
):
    # 1. Create session from Session factory
    session = Session()

    try:
        # 2. Get parent configuration (always ID 1)
        configuration = session.query(Configuration).get(1)
        if configuration is None:
            print("Configuration not found")
            session.close()
            return

        # 3. Create new object
        vmware = VMwareEsxi(
            alias=alias,
            login=login,
            password=encrypt_password(password),  # Encrypt passwords!
            api_url=api_url,
            configuration=configuration,
        )

        # 4. Add to parent relationship
        configuration.vmwares.append(vmware)

        # 5. Commit transaction
        session.commit()

        # 6. Refresh object to get DB-generated values
        session.refresh(vmware)

        # 7. Close session
        session.close()

        # 8. Return object
        return vmware
    except Exception as e:
        session.rollback()
        session.close()
        raise e
```

### Password Encryption

All passwords are encrypted using **Fernet symmetric encryption**:

```python
# Encryption key (⚠️ Should be in environment variable!)
ENCRYPTION_KEY = "uOdT_oGBMvG8N7_rpBg1UVlwVK7BD6igm0l4IqJD8cA="
fernet = Fernet(ENCRYPTION_KEY)

def encrypt_password(plain_password: str):
    encoded_pwd = plain_password.encode()
    encrypted_pwd_bytes = fernet.encrypt(encoded_pwd)
    return encrypted_pwd_bytes.decode()

def decrypt_password(encrypted_password: str):
    encrypted_pwd_bytes = encrypted_password.encode()
    decrypted_pwd_bytes = fernet.decrypt(encrypted_pwd_bytes)
    return decrypted_pwd_bytes.decode()
```

**Usage:**
- **Always encrypt** before storing: `password=encrypt_password(password)`
- **Always decrypt** before using: `plain_pwd = decrypt_password(db_object.password)`

### External Service Testing

Repository provides test functions for external services:

```python
# Test VMware vCenter connectivity
def test_vmware_esxi_configuration(login, password, api_url, ...):
    # 1. Resolve hostname
    # 2. Authenticate to vCenter REST API
    # 3. Verify datacenter exists
    # 4. Verify cluster/host exists
    # 5. Verify datastore exists
    # 6. Verify resource pool exists
    # Returns: list of errors (empty if success)

# Test LDAP/AD connectivity
def test_ldap(ldap_url, ldap_port, bind_dn, bind_credentials):
    # 1. Connect to LDAP server
    # 2. Attempt bind with credentials
    # Returns: {"is_valid": True/False, "error": "..."}

# Test database connectivity
def test_database(type, host, port, name, login, password, servername=None):
    # 1. Build connection string
    # 2. Attempt connection
    # 3. Execute simple query
    # Returns: {"is_valid": True/False, "error": "..."}
```

### Key Repository Functions by Category

#### Configuration
- `getConfiguration(Session)` - Get the single Configuration record (ID=1)
- `update_number_concurent_users(number, Session)` - Update concurrent users
- `update_current_step(number, Session)` - Update wizard step

#### Hypervisors
- `add_vmware_esxi_configuration(...)` - Add VMware config
- `update_vmware_esxi_configuration(id, ...)` - Update VMware config
- `delete_vmware_esxi_configuration(id, Session)` - Delete VMware config
- `add_nutanix_ahv_configuration(...)` - Add Nutanix config
- `get_hypervisor(id, type, Session)` - Get hypervisor by ID and type
- `get_hypervisor_list(Session)` - Get all hypervisors (both types)

#### Zones
- `add_zone(name, sub_network, ..., hypervisor_id, Session)` - Add network zone
- `get_zones(Session)` - Get all zones
- `update_zone(id, ..., hypervisor_id, Session)` - Update zone

#### Virtual Machines
- `scaffold_architecture(Session)` - Generate VM architecture based on config
- `get_virtual_machines(Session)` - Get all VMs
- `get_vms_by_group(group, Session)` - Get VMs by group (e.g., "gitops", "vault")
- `update_virtual_machine(id, ..., Session)` - Update VM

#### Ansible
- `add_ansible_role(role_name, order, Session)` - Track role execution
- `update_ansible_role(role_name, runner_ident, status, Session)` - Update role status
- `get_ansible_roles(Session)` - Get all roles
- `get_ansible_role_status(role_name, Session)` - Get status of specific role
- `add_task_logs(event, task, stdout, runner_ident, Session)` - Log task output
- `delete_all_ansible_roles(Session)` - Clear role tracking (before new run)

#### Services
- `add_database(name, type, host, port, ...)` - Add database connection
- `add_ldap(ldap_type, ldap_url, ...)` - Add LDAP server
- `add_sms_provider(url, login, ...)` - Add SMS provider
- `add_smtp_server(host, port, ...)` - Add SMTP server

---

## API Layer - api.py

This file defines **all REST API endpoints** using FastAPI.

### FastAPI Basics

```python
from fastapi import FastAPI, HTTPException, BackgroundTasks, Depends

app = FastAPI()

# GET endpoint
@app.get("/zones", response_model=List[ZoneModel])
def read_zones():
    return get_zones(Session)

# POST endpoint
@app.post("/vmware", response_model=VMwareEsxiModel)
def add_vmware(vmware: VMwareEsxiModel):
    vmware_dict = vmware.dict(exclude={"id", "type"})
    return add_vmware_esxi_configuration(**vmware_dict, Session=Session)

# PUT endpoint
@app.put("/vmware/{id}", response_model=VMwareEsxiModel)
def update_vmware(id: int, vmware: VMwareEsxiModel):
    return update_vmware_esxi_configuration(
        id=id,
        **vmware.model_dump(exclude={"id", "is_connected", "type"}),
        Session=Session
    )

# DELETE endpoint
@app.delete("/vmware/{id}")
def delete_vmware(id: int):
    delete_vmware_esxi_configuration(id, Session)
    return {"message": "VMware Esxi configuration deleted"}
```

### CORS Configuration

```python
origins = ["*"]  # Allow all origins

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Background Tasks

For long-running operations like Ansible deployments:

```python
@app.post("/start", response_model=bool)
async def start_install(background_tasks: BackgroundTasks):
    # Clear previous run
    delete_all_ansible_roles(Session)

    # Run in background (non-blocking)
    background_tasks.add_task(install_all_roles, Session)

    # Return immediately
    return True
```

### API Endpoints by Category

#### Deployment
- `POST /start` - Start Ansible deployment (background task)
- `GET /ansible_roles` - Get all role execution statuses
- `GET /task-logs/{runner_ident}` - Get logs for specific role run

#### Configuration
- `GET /configuration` - Get full system configuration
- `PUT /configuration/concurrent-users` - Update user count
- `PUT /configuration/current_step` - Update wizard step

#### Hypervisors
- `GET /hypervisors` - List all hypervisors
- `GET /hypervisor/{id}?type=vmware` - Get specific hypervisor
- `POST /vmware` - Add VMware configuration
- `PUT /vmware/{id}` - Update VMware configuration
- `DELETE /vmware/{id}` - Delete VMware configuration
- `POST /nutanix` - Add Nutanix configuration
- `PUT /nutanix/{id}` - Update Nutanix configuration
- `DELETE /nutanix/{id}` - Delete Nutanix configuration

#### Zones & VMs
- `GET /zones` - List all network zones
- `GET /zones/{id}` - Get specific zone
- `PUT /zone/{id}/{hypervisor_id}` - Update zone
- `GET /virtual-machines` - List all VMs (triggers scaffold)
- `GET /virtual-machines/group/{group}` - Get VMs by group
- `PUT /virtual-machine/{id}` - Update VM

#### Services
- `GET /databases` - List databases
- `POST /database` - Add database
- `PUT /database/{id}` - Update database
- `DELETE /database/{id}` - Delete database
- `POST /database-test` - Test database connection
- `GET /ldaps` - List LDAP servers
- `POST /ldap` - Add LDAP server
- `POST /ldap-test` - Test LDAP connection
- `GET /sms-providers` - List SMS providers
- `GET /smtp-servers` - List SMTP servers

#### Security
- `GET /security` - Get security config
- `PUT /security` - Update security config
- `POST /tester-certificat` - Test SSL certificate
- `POST /ssh-keys-test` - Test SSH key pair

#### Testing
- `POST /vmware-test` - Test VMware connectivity
- `POST /service-test` - Test service connectivity
- `GET /test-flows` - Test network flows

---

## Ansible Integration - install.py

This is where **infrastructure orchestration** happens.

### How It Works

```python
async def install_all_roles(Session):
    """Execute all 34 Ansible roles in sequence"""

    # 1. Define role execution order
    noinf_roles = [
        "provisionnement-vms-infra",
        "provisionnement-vms-apps",
        "provisionnement-vms-dmz",
        "prepare-vms",
        "install-docker-registry",
        # ... 29 more roles
    ]

    # 2. Create tracking records in database
    order = 1
    for role in noinf_roles:
        add_ansible_role(role, order, Session)
        order += 1

    # 3. Execute each role
    for role in noinf_roles:
        await async_call_role(role, Session)

        # 4. Check status - stop if failed
        status = get_ansible_role_status(role, Session)
        if status != "successful":
            break
```

### Role Execution Flow

```python
def call_role(role_name, Session):
    """Execute a single Ansible role"""

    # 1. Load role-specific variables from database
    extra_vars, inventory = load_and_call_get_inputs(role_name, Session)

    # 2. Set up Ansible Runner
    private_data_dir = ANSIBLE_ROOT  # /home/devops or /backend
    status_handler = create_status_handler(role_name, Session)
    event_handler = create_event_handler(role_name, Session)

    # 3. Execute role
    ansible_runner.run(
        private_data_dir=private_data_dir,
        role=role_name,
        status_handler=status_handler,    # Updates DB on status change
        event_handler=event_handler,      # Logs task output to DB
        extravars=extra_vars,             # Variables from DB
        inventory=inventory,              # Dynamic inventory
    )

    # 4. Run post-install hook (if exists)
    call_post_install(role_name, Session)
```

### Dynamic Variable Loading

Each role has a `prepare_inputs.py` file:

```python
# backend/project/roles/install-argocd/prepare_inputs.py

def get_inputs(Session):
    """Query database and return Ansible variables"""

    # 1. Get security config
    security = get_security(Session)
    prefix = "" if security.env_prefix == "" else security.env_prefix + "-"

    # 2. Build domain names
    argocd_domain_apps = f"{prefix}argocd-apps.{security.base_domain}"

    # 3. Get VM IPs
    vault_vm = get_vms_by_group("vault", Session)[0]
    gogs_vm = get_vms_by_group("gitops", Session)[0]

    # 4. Build variables dictionary
    extra_vars = {
        "vault_ip": vault_vm.ip,
        "gogs_ip": gogs_vm.ip,
        "argocd_domain_apps": argocd_domain_apps,
        "prefix": prefix,
    }

    # 5. Build dynamic inventory
    inventory = {
        "all": {
            "hosts": {
                "localhost": {
                    "ansible_host": "127.0.0.1",
                    "ansible_connection": "local",
                },
                "vault_vm": {
                    "ansible_host": vault_vm.ip,
                    "ansible_user": "devops"
                }
            }
        }
    }

    # 6. Return tuple: (variables, inventory)
    return extra_vars, inventory
```

### Status and Event Handlers

```python
def create_status_handler(role_name, Session):
    """Update role status in database"""
    def my_status_handler(data, runner_config):
        update_ansible_role(
            role_name,
            data["runner_ident"],  # Unique run ID
            data["status"],        # running, successful, failed
            Session
        )
    return my_status_handler

def create_event_handler(role_name, Session):
    """Log task output to database"""
    def my_event_handler(data):
        if "event_data" in data and "task" in data["event_data"]:
            add_task_logs(
                data["event"],            # task_started, task_ok, task_failed
                data["event_data"]["task"],  # Task name
                data["stdout"],           # Task output
                data["runner_ident"],     # Unique run ID
                Session
            )
    return my_event_handler
```

---

## Complete Request Flow Examples

### Example 1: Adding a VMware Hypervisor

```
User (Frontend)
    │
    │ POST /vmware
    │ {
    │   "alias": "vcenter-prod",
    │   "login": "admin",
    │   "password": "secret123",
    │   "api_url": "vcenter.local",
    │   ...
    │ }
    ▼
API Layer (api.py)
    │
    │ @app.post("/vmware", response_model=VMwareEsxiModel)
    │ def add_vmware(vmware: VMwareEsxiModel):
    │     vmware_dict = vmware.dict(exclude={"id", "type"})
    │     return add_vmware_esxi_configuration(**vmware_dict, Session=Session)
    │
    ▼
Repository Layer (repository.py)
    │
    │ def add_vmware_esxi_configuration(..., Session):
    │     session = Session()
    │     configuration = session.query(Configuration).get(1)
    │
    │     vmware = VMwareEsxi(
    │         alias=alias,
    │         password=encrypt_password(password),  ← Encrypt!
    │         ...
    │     )
    │
    │     configuration.vmwares.append(vmware)
    │     session.commit()
    │     return vmware
    │
    ▼
Database Layer (models.py)
    │
    │ class VMwareEsxi(Base):
    │     __tablename__ = "vmware_esxi"
    │     id = Column(Integer, primary_key=True)
    │     password = Column(String, nullable=False)
    │     ...
    │
    ▼
PostgreSQL
    │
    │ INSERT INTO vmware_esxi (alias, login, password, ...)
    │ VALUES ('vcenter-prod', 'admin', 'gAAAAA...encrypted', ...)
    │ RETURNING id, alias, ...;
    │
    ▼
Response flows back up
    │
    │ PostgreSQL → SQLAlchemy Object → Repository → API → JSON
    │
    ▼
User (Frontend)
    │
    │ Receives:
    │ {
    │   "id": 1,
    │   "alias": "vcenter-prod",
    │   "is_connected": false,
    │   ...
    │ }
```

### Example 2: Starting Ansible Deployment

```
User (Frontend)
    │
    │ POST /start
    ▼
API Layer (api.py)
    │
    │ @app.post("/start")
    │ async def start_install(background_tasks: BackgroundTasks):
    │     delete_all_ansible_roles(Session)          ← Clear previous run
    │     background_tasks.add_task(install_all_roles, Session)  ← Start background
    │     return True                                 ← Return immediately
    │
    │ (API returns, user sees "Deployment started")
    │
    ▼
Background Task Executes
    │
    │ install.py: install_all_roles(Session)
    │     │
    │     ├─ For each role in sequence:
    │     │     │
    │     │     ├─ 1. Add to DB: add_ansible_role(role, order, Session)
    │     │     │
    │     │     ├─ 2. Load variables: load_and_call_get_inputs(role, Session)
    │     │     │         │
    │     │     │         ▼
    │     │     │    role/prepare_inputs.py: get_inputs(Session)
    │     │     │         │
    │     │     │         ├─ Query DB: get_security(Session)
    │     │     │         ├─ Query DB: get_vms_by_group("vault", Session)
    │     │     │         └─ Return: (extra_vars, inventory)
    │     │     │
    │     │     ├─ 3. Execute: ansible_runner.run(...)
    │     │     │         │
    │     │     │         ├─ On status change → update_ansible_role(...)
    │     │     │         └─ On task output → add_task_logs(...)
    │     │     │
    │     │     └─ 4. Check status → if failed, stop
    │     │
    │     └─ All roles complete or one failed
    │
    ▼
Frontend polls /ansible_roles
    │
    │ GET /ansible_roles → Returns status of all roles
    │ [
    │   {"role_name": "install-vault", "status": "successful", ...},
    │   {"role_name": "install-argocd", "status": "running", ...},
    │   ...
    │ ]
```

---

## How to Add New Features

### Adding a New Database Table

**1. Define SQLAlchemy Model in `models.py`:**

```python
class NewService(Base):
    __tablename__ = "new_services"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    url = Column(String, nullable=False)
    api_key = Column(String, nullable=False)
    configuration_id = Column(Integer, ForeignKey("configurations.id"))
    configuration = relationship("Configuration", back_populates="new_services")
```

**2. Add relationship to Configuration:**

```python
class Configuration(Base):
    # ... existing fields
    new_services = relationship("NewService", back_populates="configuration")
```

**3. Define Pydantic Model:**

```python
class NewServiceModel(BaseModel):
    id: int
    name: str
    url: str
    api_key: str

    class Config:
        from_attributes = True
```

**4. Add to ConfigurationModel:**

```python
class ConfigurationModel(BaseModel):
    # ... existing fields
    new_services: List[NewServiceModel]
```

### Adding Repository Functions

**In `repository.py`:**

```python
def add_new_service(name, url, api_key, Session):
    """Add a new service"""
    session = Session()
    configuration = session.query(Configuration).get(1)
    if configuration is None:
        print("Configuration not found")
        session.close()
        return

    new_service = NewService(
        name=name,
        url=url,
        api_key=encrypt_password(api_key),  # Encrypt sensitive data!
        configuration=configuration,
    )

    configuration.new_services.append(new_service)
    session.commit()
    session.refresh(new_service)
    session.close()
    return new_service

def get_new_services(Session):
    """Get all new services"""
    session = Session()
    services = session.query(NewService).all()
    session.close()
    return services

def update_new_service(id, name, url, api_key, Session):
    """Update a new service"""
    session = Session()
    service = session.query(NewService).get(id)
    if service is None:
        print("Service not found")
        session.close()
        return

    service.name = name
    service.url = url
    if api_key:  # Only update if provided
        service.api_key = encrypt_password(api_key)

    session.commit()
    session.refresh(service)
    session.close()
    return service

def delete_new_service(id, Session):
    """Delete a new service"""
    session = Session()
    service = session.query(NewService).get(id)
    if service is None:
        print("Service not found")
        session.close()
        return
    session.delete(service)
    session.commit()
    session.close()
```

### Adding API Endpoints

**In `api.py`:**

```python
from models import NewServiceModel
from repository import (
    add_new_service,
    get_new_services,
    update_new_service,
    delete_new_service,
)

# GET all services
@app.get("/new-services", response_model=List[NewServiceModel])
def read_new_services():
    return get_new_services(Session)

# POST new service
@app.post("/new-service", response_model=NewServiceModel)
def create_new_service(service: NewServiceModel):
    service_dict = service.dict(exclude={"id"})
    return add_new_service(**service_dict, Session=Session)

# PUT update service
@app.put("/new-service/{id}", response_model=NewServiceModel)
def modify_new_service(id: int, service: NewServiceModel):
    return update_new_service(
        id,
        **service.model_dump(exclude={"id"}),
        Session=Session
    )

# DELETE service
@app.delete("/new-service/{id}")
def remove_new_service(id: int):
    delete_new_service(id, Session)
    return {"message": "Service deleted successfully"}
```

### Adding a New Ansible Role

**1. Create role directory:**

```bash
mkdir -p backend/project/roles/install-my-service/{tasks,templates,files,defaults}
```

**2. Create `prepare_inputs.py`:**

```python
# backend/project/roles/install-my-service/prepare_inputs.py

from repository import get_security, get_new_services, get_vms_by_group

def get_inputs(Session):
    """Load variables from database"""

    # Get configuration
    security = get_security(Session)
    my_services = get_new_services(Session)
    target_vms = get_vms_by_group("my-service-group", Session)

    # Build variables
    extra_vars = {
        "base_domain": security.base_domain,
        "services": [
            {"name": s.name, "url": s.url, "api_key": decrypt_password(s.api_key)}
            for s in my_services
        ],
        "target_ips": [vm.ip for vm in target_vms],
    }

    # Build inventory
    inventory = {
        "all": {
            "hosts": {
                vm.hostname: {
                    "ansible_host": vm.ip,
                    "ansible_user": "devops"
                }
                for vm in target_vms
            }
        }
    }

    return extra_vars, inventory
```

**3. Create Ansible tasks:**

```yaml
# backend/project/roles/install-my-service/tasks/main.yml

---
- name: Install my service
  debug:
    msg: "Installing on {{ ansible_host }}"

- name: Deploy configuration
  template:
    src: config.yml.j2
    dest: /etc/my-service/config.yml
```

**4. Add to role sequence in `install.py`:**

```python
wkube_roles = [
    "install-argocd",
    "install-cert-manager",
    "install-my-service",  # ← Add here
    # ... other roles
]
```

---

## Security and Encryption

### Password Encryption

**Always encrypt before storing:**

```python
# WRONG ❌
vmware = VMwareEsxi(password=password)

# CORRECT ✅
vmware = VMwareEsxi(password=encrypt_password(password))
```

**Always decrypt before using:**

```python
# Get from DB
vmware = session.query(VMwareEsxi).get(1)

# Decrypt before using
plain_password = decrypt_password(vmware.password)

# Use in API call
response = requests.post(api_url, auth=(vmware.login, plain_password))
```

### Moving Encryption Key to Environment

**Current (not secure):**
```python
ENCRYPTION_KEY = "uOdT_oGBMvG8N7_rpBg1UVlwVK7BD6igm0l4IqJD8cA="
```

**Better:**
```python
ENCRYPTION_KEY = os.getenv("FERNET_KEY", "default-key-for-dev")
fernet = Fernet(ENCRYPTION_KEY)
```

Then set in docker-compose.yml:
```yaml
backend:
  environment:
    FERNET_KEY: "uOdT_oGBMvG8N7_rpBg1UVlwVK7BD6igm0l4IqJD8cA="
```

---

## Testing and Validation

### Testing Database Connectivity

```python
def test_database(type, host, port, name, login, password, servername=None):
    """Test database connection"""
    errors = []

    if type == "postgresql":
        try:
            conn = psycopg2.connect(
                host=host,
                port=port,
                database=name,
                user=login,
                password=password,
                connect_timeout=10
            )
            conn.close()
            return {"is_valid": True}
        except Exception as e:
            return {"is_valid": False, "error": str(e)}

    elif type == "informix":
        # Informix connection logic
        # ...
```

### Testing VMware Connectivity

```python
def test_vmware_esxi_configuration(...):
    """Validate VMware vCenter configuration"""
    errors = []

    # 1. Test authentication
    response = requests.post(
        f"https://{api_url}/rest/com/vmware/cis/session",
        auth=(login, password),
        verify=False
    )

    if response.status_code == 401:
        errors.append("Invalid credentials")

    # 2. Test datacenter exists
    # 3. Test cluster/host exists
    # 4. Test datastore exists
    # 5. Test resource pool exists

    return errors  # Empty list = success
```

### Manual Testing

```bash
# Start backend in development mode
cd backend
uvicorn api:app --host 0.0.0.0 --port 8008 --reload

# Test API endpoints
curl http://localhost:8008/configuration
curl -X POST http://localhost:8008/vmware -H "Content-Type: application/json" -d '{...}'

# Test Ansible role manually
python install.py --role install-argocd

# Access PostgreSQL
docker exec -it postgres psql -U harmonisation

# Check tables
\dt
SELECT * FROM vmware_esxi;
SELECT * FROM ansible_roles;
```

---

## Summary - Key Takeaways

1. **Three-Layer Architecture**: API → Repository → Database. Never skip layers.

2. **Always Use Repository Functions**: Never write direct SQL queries in `api.py`.

3. **Encrypt Sensitive Data**: Use `encrypt_password()` before storing, `decrypt_password()` before using.

4. **Session Pattern**: Always close database sessions in `repository.py`.

5. **Ansible Integration**: Each role has `prepare_inputs.py` that queries the database.

6. **Background Tasks**: Long-running operations use FastAPI's `BackgroundTasks`.

7. **Dynamic Variables**: Ansible gets all variables from the database at runtime.

8. **Status Tracking**: Ansible role execution tracked in `ansible_roles` and `task_logs` tables.

---

## Next Steps

Now that you understand the backend architecture:

1. **Explore the Code**: Read through actual functions in `repository.py`
2. **Trace a Request**: Pick an endpoint and follow it through all layers
3. **Examine Ansible Roles**: Look at different `prepare_inputs.py` files
4. **Make a Change**: Add a small feature following the patterns above
5. **Test**: Use curl or Postman to test your changes

**You now have the knowledge to confidently modify and extend this backend!**
