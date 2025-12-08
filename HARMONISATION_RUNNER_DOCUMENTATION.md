# **Harmonisation Runner - Complete Documentation**

**Version:** 1.0  
**Last Updated:** 2025-11-25

## **Executive Summary**

The **Harmonisation Runner** (SRM-CS Automation Platform) is a comprehensive Infrastructure-as-Code (IaC) automation platform designed to deploy, provision, and manage enterprise-grade microservices applications including **EServices** and **GCO** modules. The platform provides a full-stack, GitOps-driven deployment solution built on Kubernetes (RKE2), featuring an intuitive web interface and a powerful backend orchestration engine.

---

## **Table of Contents**

1. [Architecture Overview](#architecture-overview)
2. [Core Components](#core-components)
3. [Technology Stack](#technology-stack)
4. [Deployment Architecture](#deployment-architecture)
5. [Installation & Setup](#installation--setup)
6. [Backend System](#backend-system)
7. [Frontend System](#frontend-system)
8. [Ansible Automation](#ansible-automation)
9. [Database Schema](#database-schema)
10. [API Reference](#api-reference)
11. [Security & Authentication](#security--authentication)
12. [Network Architecture](#network-architecture)
13. [Monitoring & Observability](#monitoring--observability)
14. [Troubleshooting](#troubleshooting)
15. [Development Guide](#development-guide)
16. [Appendices](#appendices)

---

## **1. Architecture Overview**

### **High-Level Architecture**

```
┌─────────────────────────────────────────────────────────────────┐
│                         NGINX Reverse Proxy                     │
│                    (Port 80 - Entry Point)                      │
└─────────────────────────────────────────────────────────────────┘
         │                    │                    │
         ▼                    ▼                    ▼
┌─────────────────┐  ┌─────────────────┐  ┌─────────────────────┐
│    Corteza      │  │   Frontend      │  │      Backend        │
│   (Low-Code)    │  │   (Angular)     │  │  (FastAPI/Ansible)  │
│   Port: 80      │  │   Port: 80      │  │    Port: 8008       │
└─────────────────┘  └─────────────────┘  └─────────────────────┘
                                                    │
                                                    ▼
                                          ┌─────────────────────┐
                                          │   PostgreSQL DB     │
                                          │   Port: 5432        │
                                          └─────────────────────┘
```

### **Routing Configuration**

- **/** → Corteza (Low-code platform & admin interface)
- **/runner/** → Angular Frontend (User interface)
- **/runner/api/** → FastAPI Backend (REST API)

---

## **2. Core Components**

### **2.1 Backend - Orchestration Engine**

**Location:** `/backend`

The backend is the heart of the automation platform, built with:

- **Framework:** FastAPI (Python)
- **Architecture:** Three-layer (API → Repository → Database)
- **Core Function:** Ansible Runner orchestration
- **Database:** PostgreSQL (via SQLAlchemy ORM)
- **Authentication:** OAuth2 with JWT tokens
- **Containerization:** Docker with custom base image

**Key Responsibilities:**
- Execute Ansible playbooks via Ansible Runner
- Manage infrastructure provisioning workflows
- Store deployment configurations and state
- Provide REST API for frontend interaction
- Handle authentication and authorization
- Manage secrets encryption (Fernet)

**Key Files:**
- `api.py` - FastAPI application and endpoint definitions
- `repository.py` - Data access layer with business logic
- `models.py` - SQLAlchemy ORM and Pydantic models
- `install.py` - Ansible Runner integration and workflow engine
- `Dockerfile` - Container build with Informix CSDK

### **2.2 Frontend - User Interface**

**Location:** `/frontend`

Modern Angular-based single-page application (SPA):

- **Framework:** Angular 16+
- **Build:** Server-side rendering (SSR) capable
- **Styling:** CSS with modern responsive design
- **API Communication:** HTTP client with interceptors

**Features:**
- Visual deployment workflow management
- Real-time deployment status monitoring
- Configuration management interface
- Resource allocation visualization
- Deployment history tracking

### **2.3 Corteza - Low-Code Platform**

**Location:** `/corteza`

Integrated 100% open-source low-code platform:

- **Purpose:** Business process management and custom app development
- **Database:** Shared PostgreSQL instance
- **Localization:** Multi-language support (FR, EN)
- **Integration:** ODBC connectivity for Informix databases

### **2.4 Packer - Image Builder**

**Location:** `/packer`

Builds standardized VM templates:

- **Target Platforms:** VMware vSphere, Nutanix AHV
- **Base OS:** RHEL 9 variants
- **Variants:**
  - `rhel9-agents` - RKE2 Kubernetes agents
  - `rhel9-docker` - Docker runtime
  - `harmo-docker-agents` - Harmonisation-specific

### **2.5 Database Layer**

**PostgreSQL Container:**
- Version: PostgreSQL 15
- User: `harmonisation`
- Database: `harmonisation`
- Health checks: Automatic with pg_isready
- Initialization: SQL scripts in `/db_init`

---

## **3. Technology Stack**

### **Backend Technologies**

| Component | Technology | Version | Purpose |
|-----------|-----------|---------|---------|
| **Web Framework** | FastAPI | 0.115.3 | REST API server |
| **Automation Engine** | Ansible Runner | 2.4.0 | Playbook execution |
| **ORM** | SQLAlchemy | 2.0.35 | Database abstraction |
| **Validation** | Pydantic | 2.9.2 | Data validation |
| **WSGI Server** | Gunicorn | 23.0.0 | Production server |
| **Auth** | python-jose | 3.3.0 | JWT tokens |
| **Secrets** | Cryptography (Fernet) | - | Password encryption |
| **SSH** | Paramiko | 3.5.0 | Remote connections |
| **Database Driver** | psycopg2-binary | 2.9.10 | PostgreSQL |
| **Container Management** | Docker SDK | - | Docker operations |
| **Secrets Management** | hvac | - | Vault integration |
| **LDAP** | ldap3 | 2.9.1 | Directory services |
| **Kubernetes** | kubernetes | 31.0.0 | K8s API client |

### **Frontend Technologies**

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **Framework** | Angular 16+ | SPA framework |
| **Language** | TypeScript | Type-safe JavaScript |
| **Build Tool** | Angular CLI | Build & dev tools |
| **HTTP Client** | Angular HttpClient | API communication |
| **Routing** | Angular Router | Navigation |
| **SSR** | Angular Universal | Server-side rendering |

### **Infrastructure Technologies**

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **Hypervisors** | VMware vSphere, Nutanix AHV | VM hosting |
| **Orchestration** | Rancher Kubernetes Engine 2 (RKE2) | K8s distribution |
| **Container Runtime** | Docker | Containerization |
| **Image Builder** | Packer | VM template creation |
| **Load Balancer** | HAProxy | Traffic distribution |
| **Reverse Proxy** | NGINX | Ingress routing |

---

## **4. Deployment Architecture**

### **4.1 Network Zones**

The platform deploys across three isolated network zones:

1. **LAN Infrastructure Zone**
   - Core services: Vault, Docker Registry, Gogs
   - Load balancers: HAProxy
   - Management: Rancher

2. **LAN Applications Zone**
   - Kubernetes cluster: RKE2-APPS
   - Business applications: EServices, GCO
   - API Gateway: Gravitee LAN

3. **DMZ Zone**
   - Kubernetes cluster: RKE2-DMZ
   - API Gateway: Gravitee DMZ
   - External-facing services

### **4.2 Kubernetes Clusters**

Three separate RKE2 clusters are deployed:

| Cluster | Purpose | Components |
|---------|---------|-----------|
| **RKE2-APPS** | Business applications | EServices, GCO, Gravitee LAN |
| **RKE2-MIDDLEWARE** | Supporting services | MinIO, Kafka, Keycloak, n8n, Flowable |
| **RKE2-DMZ** | External access | Gravitee DMZ Gateway |

All clusters managed by a central **Rancher** instance.

### **4.3 Deployment Sequence**

The automated deployment follows this sequence (34 roles):

```
1. Infrastructure Provisioning
   ├── provisionnement-vms-infra
   ├── provisionnement-vms-apps
   └── provisionnement-vms-dmz

2. VM Preparation
   └── prepare-vms

3. Core Services (No Kubernetes)
   ├── install-docker-registry
   ├── install-vault
   ├── install-load-balancer
   └── install-gogs

4. Kubernetes Installation
   ├── install-rke2-apps
   ├── install-rke2-middleware
   ├── install-rke2-dmz
   └── install-rancher-server

5. K8s Foundation
   ├── install-argocd
   ├── install-cert-manager
   ├── install-longhorn
   └── setup-vault-injector

6. Middleware Services
   ├── install-minio
   ├── install-minio-backup
   ├── install-keycloak
   ├── install-kafka
   ├── install-n8n
   └── install-flowable (if EServices)

7. API Management
   ├── install-gravitee-lan
   └── install-gravitee-dmz

8. Security & Monitoring
   ├── install-neuvector
   └── install-monitoring (Coroot)

9. Applications
   ├── install-eservices
   └── install-gco
```

---

## **5. Installation & Setup**

### **5.1 Prerequisites**

- **Docker** and **Docker Compose** installed
- **Linux environment** (tested on RHEL 9)
- **Network access** to hypervisor APIs
- **SSH keys** configured
- **Sufficient resources:**
  - CPU: 8+ cores
  - RAM: 16GB+ available
  - Disk: 100GB+ free space

### **5.2 Quick Start**

```bash
# Clone the repository
cd runner-srm-cs

# Load Docker images (if provided)
bash setup.sh

# Or build from scratch
docker compose build

# Start the platform
docker compose up -d

# Access the interfaces
# Corteza: http://localhost/
# Runner Frontend: http://localhost/runner/
# Backend API: http://localhost/runner/api/docs
```

### **5.3 Directory Structure**

```
runner-srm-cs/
├── backend/               # FastAPI backend
│   ├── api.py            # Main API application
│   ├── repository.py     # Data access layer
│   ├── models.py         # Database models
│   ├── install.py        # Ansible orchestration
│   ├── project/          # Ansible roles
│   │   └── roles/        # 34 deployment roles
│   ├── inventory/        # Ansible inventories
│   └── requirements.txt  # Python dependencies
│
├── frontend/             # Angular frontend
│   ├── src/app/         # Application code
│   ├── angular.json     # Angular config
│   └── package.json     # Node dependencies
│
├── corteza/             # Corteza low-code platform
│   └── Dockerfile       # Custom Corteza build
│
├── packer/              # VM image builders
│   ├── rhel9/           # RHEL 9 base
│   └── scripts/         # Provisioning scripts
│
├── nginx/               # Reverse proxy config
│   └── custom.conf      # Routing rules
│
├── data/                # Persistent data (created by setup)
│   ├── db/              # SQLite (dev) / migrations
│   ├── postgres/        # PostgreSQL data
│   ├── .ssh/            # SSH keys
│   ├── .kube/           # Kubernetes configs
│   ├── inventory/       # Dynamic inventories
│   ├── env/             # Environment configs
│   └── terraform/       # Infrastructure state
│
├── docker-compose.yml   # Container orchestration
└── setup.sh            # Initial setup script
```

---

## **6. Backend System**

### **6.1 API Architecture**

**Three-Layer Design:**

```
┌─────────────────────────────────────┐
│     API Layer (api.py)              │
│  - FastAPI endpoints                │
│  - Request validation               │
│  - Response formatting              │
│  - Authentication/Authorization     │
└─────────────────────────────────────┘
              ▼
┌─────────────────────────────────────┐
│  Repository Layer (repository.py)   │
│  - Business logic                   │
│  - Database operations              │
│  - Password encryption              │
│  - Session management               │
└─────────────────────────────────────┘
              ▼
┌─────────────────────────────────────┐
│   Database Layer (models.py)        │
│  - SQLAlchemy ORM models            │
│  - Pydantic validation models       │
│  - Schema definitions               │
└─────────────────────────────────────┘
```

### **6.2 Key API Endpoints**

**Authentication:**
- `POST /token` - Login and get JWT token
- `POST /users/` - Create new user
- `PUT /users/{id}/status` - Activate/deactivate user

**Configuration:**
- `GET /zones/` - List network zones
- `GET /dns/` - Get DNS records
- `POST /hypervisor/vmware-esxi` - Add VMware hypervisor
- `POST /hypervisor/nutanix-ahv` - Add Nutanix hypervisor
- `POST /database/` - Configure database connection
- `POST /ldap/` - Configure LDAP authentication

**Deployment:**
- `POST /start-install` - Trigger installation workflow
- `GET /products/` - List available products
- `GET /ansible-roles/` - Get role execution status
- `GET /task-logs/` - Retrieve deployment logs
- `GET /virtual-machines/` - List provisioned VMs

**Infrastructure:**
- `POST /smtp-server/` - Configure email server
- `POST /monitoring/` - Set up monitoring
- `POST /security/` - Configure security settings
- `GET /recap-by-zone` - Resource summary by zone

### **6.3 Ansible Integration**

The `install.py` module manages Ansible execution:

**Key Features:**
- **Dynamic Role Loading:** Imports role-specific Python modules
- **Variable Injection:** Retrieves configuration from database
- **Sequential Execution:** Manages role dependencies
- **Status Tracking:** Updates database with role status
- **Logging:** Captures Ansible output to database

**Execution Flow:**
```python
1. delete_all_ansible_roles()  # Clear previous state
2. for each role in sequence:
   a. load_and_call_get_inputs(role)  # Get vars from DB
   b. call_role(role, vars)           # Execute via ansible_runner
   c. update_ansible_role(status)     # Update DB
   d. add_task_logs(output)           # Store logs
```

### **6.4 Database Models**

**Core Tables:**

| Table | Purpose | Key Fields |
|-------|---------|-----------|
| `user` | Authentication | username, password, role |
| `product` | Software to deploy | name, status, version |
| `ansible_role` | Role execution tracking | name, status, output |
| `zone` | Network zones | name, vlan, subnet |
| `virtual_machine` | VM inventory | hostname, ip, cpu, ram |
| `vmware_esxi` / `nutanix_ahv` | Hypervisor config | host, credentials |
| `database` | Database connections | host, port, name |
| `ldap` | Directory services | url, base_dn |
| `security` | Security settings | proxy, SSL config |

**Full Schema:** See [Database Schema](#9-database-schema) section.

---

## **7. Frontend System**

### **7.1 Application Structure**

```
src/app/
├── components/           # UI components
│   ├── home/            # Dashboard
│   ├── configuration/   # Config forms
│   ├── deployment/      # Install wizard
│   └── monitoring/      # Status views
│
├── Models/              # TypeScript interfaces
│   ├── Zone.ts
│   ├── VirtualMachine.ts
│   └── Product.ts
│
├── Services/            # API services
│   ├── api.service.ts   # HTTP client wrapper
│   └── auth.service.ts  # Authentication
│
└── app.routes.ts        # Route definitions
```

### **7.2 Key Features**

- **Deployment Wizard:** Step-by-step guided installation
- **Resource Visualization:** Charts for CPU/RAM/Disk allocation
- **Real-time Status:** WebSocket updates (planned)
- **Configuration Management:** CRUD operations for all entities
- **Role-based Access:** Admin/User interface differentiation
- **Deployment History:** Audit trail with logs
- **Error Handling:** User-friendly error messages

### **7.3 Routing**

| Route | Component | Description |
|-------|-----------|-------------|
| `/runner/` | Home | Dashboard with summary |
| `/runner/config` | Configuration | System setup |
| `/runner/deploy` | Deployment | Installation wizard |
| `/runner/status` | Monitoring | Real-time status |
| `/runner/history` | History | Past deployments |

---

## **8. Ansible Automation**

### **8.1 Role Structure**

Each role follows Ansible best practices:

```
roles/role-name/
├── tasks/
│   └── main.yml         # Task definitions
├── defaults/
│   └── main.yml         # Default variables
├── templates/
│   └── *.j2             # Jinja2 templates
├── files/
│   └── *                # Static files
├── prepare_inputs.py    # Python module for DB integration
└── README.md            # Role documentation
```

### **8.2 Dynamic Variable Loading**

Each role's `prepare_inputs.py` provides a `get_inputs(Session)` function:

```python
def get_inputs(Session):
    """
    Query database and return dict of Ansible variables
    """
    session = Session()
    # Query database
    zones = session.query(Zone).all()
    hypervisor = session.query(VMwareEsxi).first()
    
    # Build variables dict
    return {
        'zones': [zone.to_dict() for zone in zones],
        'vcenter_host': hypervisor.host,
        'vcenter_username': hypervisor.username,
        # ... more variables
    }
```

### **8.3 Role Categories**

**VM Provisioning Roles:**
- `provisionnement-vms-infra` - Infrastructure VMs
- `provisionnement-vms-apps` - Application VMs
- `provisionnement-vms-dmz` - DMZ VMs
- `prepare-vms` - Base VM configuration

**Infrastructure Roles:**
- `install-docker-registry` - Private registry
- `install-vault` - HashiCorp Vault
- `install-load-balancer` - HAProxy setup
- `install-gogs` - Git server

**Kubernetes Roles:**
- `install-rke2-*` - Three K8s clusters
- `install-rancher-server` - Cluster management
- `install-argocd` - GitOps CD
- `install-cert-manager` - TLS automation
- `install-longhorn` - Storage

**Middleware Roles:**
- `install-minio` - Object storage
- `install-keycloak` - IAM
- `install-kafka` - Message streaming
- `install-n8n` - Workflow automation
- `install-flowable` - BPM engine

**Application Roles:**
- `install-eservices` - Citizen services
- `install-gco` - Operations management

---

## **9. Database Schema**

### **9.1 Complete Entity Relationship Diagram**

```
┌─────────────┐
│    User     │
├─────────────┤
│ id (PK)     │
│ username    │
│ password    │
│ role        │
│ is_active   │
└─────────────┘

┌─────────────────┐      ┌──────────────────┐
│   Zone          │      │ VirtualMachine   │
├─────────────────┤      ├──────────────────┤
│ id (PK)         │◄─────┤ id (PK)          │
│ name            │  1:N │ zone_id (FK)     │
│ alias           │      │ hostname         │
│ vlan            │      │ ip_address       │
│ subnet          │      │ cpu              │
│ gateway         │      │ memory           │
│ dns_servers     │      │ disk             │
└─────────────────┘      │ product          │
                         │ role             │
                         └──────────────────┘

┌─────────────────┐
│  Product        │
├─────────────────┤
│ id (PK)         │
│ name            │
│ status          │
│ version         │
│ description     │
└─────────────────┘

┌─────────────────┐
│ AnsibleRole     │
├─────────────────┤
│ id (PK)         │
│ name            │
│ status          │
│ output          │
│ created_at      │
│ updated_at      │
└─────────────────┘

┌─────────────────┐
│  VMwareEsxi     │
├─────────────────┤
│ id (PK)         │
│ alias           │
│ host            │
│ username        │
│ password        │
│ datacenter      │
│ cluster         │
│ datastore       │
│ network         │
│ port            │
└─────────────────┘

┌─────────────────┐
│  NutanixAHV     │
├─────────────────┤
│ id (PK)         │
│ alias           │
│ host            │
│ username        │
│ password        │
│ cluster         │
│ network         │
│ port            │
└─────────────────┘

┌─────────────────┐
│  Database       │
├─────────────────┤
│ id (PK)         │
│ type            │
│ alias           │
│ host            │
│ port            │
│ database_name   │
│ username        │
│ password        │
└─────────────────┘

┌─────────────────┐
│   Ldap          │
├─────────────────┤
│ id (PK)         │
│ url             │
│ base_dn         │
│ user_dn         │
│ password        │
│ user_filter     │
│ group_filter    │
└─────────────────┘

┌─────────────────┐
│  Security       │
├─────────────────┤
│ id (PK)         │
│ use_proxy       │
│ proxy_host      │
│ proxy_port      │
│ prefix_hostname │
│ base_domain     │
│ ssl_enabled     │
└─────────────────┘

┌─────────────────┐
│  Monitoring     │
├─────────────────┤
│ id (PK)         │
│ tool            │
│ endpoint        │
│ username        │
│ password        │
└─────────────────┘

┌─────────────────┐
│  SMTPServer     │
├─────────────────┤
│ id (PK)         │
│ host            │
│ port            │
│ username        │
│ password        │
│ use_tls         │
│ from_address    │
└─────────────────┘

┌─────────────────┐
│  FlowMatrix     │
├─────────────────┤
│ id (PK)         │
│ source_zone     │
│ source_vm       │
│ dest_zone       │
│ dest_vm         │
│ protocol        │
│ port            │
└─────────────────┘
```

### **9.2 Important Notes**

- **Password Encryption:** All passwords encrypted with Fernet (symmetric encryption)
- **Cascading Deletes:** Foreign keys configured for proper cleanup
- **Timestamps:** `created_at` and `updated_at` tracked automatically
- **Status Values:** `to_install`, `installed`, `failed`, `skipped`

---

## **10. API Reference**

### **10.1 Authentication Endpoints**

#### **POST /token**
Login and receive JWT access token.

**Request:**
```json
{
  "username": "admin",
  "password": "password"
}
```

**Response:**
```json
{
  "access_token": "eyJhbGc...",
  "token_type": "bearer"
}
```

#### **POST /users/**
Create new user (admin only).

**Request:**
```json
{
  "username": "newuser",
  "password": "securepass",
  "role": "user",
  "is_active": true
}
```

### **10.2 Configuration Endpoints**

#### **POST /hypervisor/vmware-esxi**
Add VMware hypervisor configuration.

**Request:**
```json
{
  "alias": "vcenter-prod",
  "host": "vcenter.example.com",
  "username": "administrator@vsphere.local",
  "password": "password",
  "datacenter": "DC1",
  "cluster": "Cluster1",
  "datastore": "datastore1",
  "network": "VM Network",
  "port": "443"
}
```

#### **POST /zone/**
Create network zone.

**Request:**
```json
{
  "name": "lan_apps",
  "alias": "LAN Applications",
  "vlan": "100",
  "subnet": "10.1.100.0/24",
  "gateway": "10.1.100.1",
  "dns_servers": "8.8.8.8,8.8.4.4"
}
```

### **10.3 Deployment Endpoints**

#### **POST /start-install**
Trigger automated deployment workflow.

**Request:**
```json
{
  "products": ["eservices", "gco"]
}
```

**Response:**
```json
{
  "status": "started",
  "message": "Deployment initiated successfully"
}
```

#### **GET /ansible-roles/**
Get status of all Ansible roles.

**Response:**
```json
[
  {
    "id": 1,
    "name": "provisionnement-vms-infra",
    "status": "success",
    "output": "PLAY RECAP...",
    "created_at": "2025-11-25T09:00:00",
    "updated_at": "2025-11-25T09:05:00"
  }
]
```

---

## **11. Security & Authentication**

### **11.1 Authentication Flow**

```
1. User submits credentials → POST /token
2. Backend validates against database
3. JWT token generated (expires in 30 minutes)
4. Token stored in frontend (localStorage/memory)
5. All API requests include: Authorization: Bearer {token}
6. Backend validates token on each request
```

### **11.2 Password Security**

- **Storage:** Passwords encrypted with Fernet (symmetric encryption)
- **Key:** Stored in `repository.py` (should be in env variable)
- **Algorithm:** AES-128-CBC with HMAC
- **Encryption Key:** `uOdT_oGBMvG8N7_rpBg1UVlwVK7BD6igm0l4IqJD8cA=`

⚠️ **Security Recommendation:** Move encryption key to environment variable.

### **11.3 Network Security**

- **Proxy Support:** Configurable HTTP/HTTPS proxy
- **No-proxy List:** Bypass for internal networks
- **SSL/TLS:** Cert-manager for automated certificate management
- **Network Segmentation:** VLAN isolation between zones
- **Vault Integration:** Secrets stored in HashiCorp Vault

---

## **12. Network Architecture**

### **12.1 Zone Configuration**

Three primary network zones:

| Zone | VLAN | Subnet Example | Purpose |
|------|------|----------------|---------|
| **LAN_INFRA** | 10 | 10.1.10.0/24 | Core infrastructure services |
| **LAN_APPS** | 100 | 10.1.100.0/24 | Application workloads |
| **DMZ** | 200 | 10.1.200.0/24 | External-facing services |

### **12.2 Flow Matrix**

The platform manages firewall rules via Flow Matrix entries:

```python
FlowMatrix(
    source_zone="lan_apps",
    source_vm="app-server-01",
    dest_zone="lan_infra",
    dest_vm="postgres-01",
    protocol="tcp",
    port="5432"
)
```

### **12.3 Load Balancer Configuration**

HAProxy instances in each zone:
- **LB-LAN:** Routes traffic to RKE2-APPS and RKE2-MIDDLEWARE
- **LB-DMZ:** Routes external traffic to RKE2-DMZ
- **LB-INTEGRATION:** Connects DMZ to LAN services

---

## **13. Monitoring & Observability**

### **13.1 Coroot Monitoring**

Deployed monitoring stack includes:

- **Coroot Agents:** On all K8s clusters and LB VMs
- **Metrics Collection:** CPU, RAM, disk, network
- **Log Aggregation:** Container and system logs
- **Alerting:** Configured thresholds for critical services
- **Dashboards:** Pre-built visualizations

### **13.2 Deployment Monitoring**

- **Task Logs:** Stored in `task_log` table
- **Role Status:** Tracked in `ansible_role` table
- **Real-time Updates:** Via API polling (WebSocket planned)
- **Error Tracking:** Failed roles highlighted in UI

---

## **14. Troubleshooting**

### **14.1 Common Issues**

**Backend won't start:**
```bash
# Check PostgreSQL health
docker exec postgres pg_isready -U harmonisation

# View backend logs
docker logs backend

# Verify environment variables
docker exec backend env | grep DATABASE_URL
```

**Ansible role fails:**
```bash
# Check role logs in database
curl http://localhost/runner/api/ansible-roles/

# Manually test Ansible
docker exec -it backend bash
cd /home/devops/data/project
ansible-playbook -i inventory/hosts.yml roles/role-name/tasks/main.yml
```

**Network connectivity issues:**
```bash
# Test from backend container
docker exec backend ping -c 3 {hypervisor_ip}
docker exec backend curl -k https://{vcenter_host}
```

### **14.2 Database Issues**

**Reset database:**
```bash
# Stop services
docker compose down

# Remove PostgreSQL data
sudo rm -rf data/postgres/*

# Restart
docker compose up -d
```

**Manual database access:**
```bash
docker exec -it postgres psql -U harmonisation
```

### **14.3 Informix Integration**

See dedicated documentation: `INFORMIX_INTEGRATION.md` and `INFORMIX_TROUBLESHOOTING.md`

---

## **15. Development Guide**

### **15.1 Backend Development**

```bash
cd backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run development server
uvicorn api:app --host 0.0.0.0 --port 8008 --reload
```

### **15.2 Frontend Development**

```bash
cd frontend

# Install dependencies
npm install

# Run development server
ng serve

# Build for production
ng build --configuration production
```

### **15.3 Adding New Ansible Role**

1. Create role structure in `backend/project/roles/new-role/`
2. Add `prepare_inputs.py` with `get_inputs(Session)` function
3. Update role sequence in `backend/install.py`
4. Add role to appropriate list: `apps_roles`, `wkube_roles`, `nokube_roles`, or `noinf_roles`
5. Test role execution

---

## **16. Appendices**

### **16.1 Environment Variables**

| Variable | Default | Purpose |
|----------|---------|---------|
| `DATABASE_URL` | `sqlite:///./sql_app.db` | PostgreSQL connection string |
| `INFORMIXDIR` | `/opt/IBM/Informix.4.50.FC11W1` | Informix SDK path |
| `http_proxy` | `http://10.97.243.181:808/` | HTTP proxy |
| `https_proxy` | `http://10.97.243.181:808/` | HTTPS proxy |
| `no_proxy` | `localhost,127.0.0.1,...` | Proxy bypass list |

### **16.2 Container Resource Limits**

**Backend:**
- Memory: 4GB limit
- CPU shares: 1024

**PostgreSQL:**
- Memory: Default (no limit)
- Health check: 5 retries, 10s interval

### **16.3 Persistent Data Volumes**

```yaml
Backend Volumes:
- ./data/.ssh/ → /home/devops/.ssh/
- ./data/db → /home/devops/db
- ./data/.kube → /home/devops/.kube
- ./data/inventory → /home/devops/inventory
- ./data/env → /home/devops/env
- ./data/terraform → /home/devops/terraform
- ./images → /images

PostgreSQL Volumes:
- ./data/postgres → /var/lib/postgresql/data
- ./db_init → /docker-entrypoint-initdb.d
```

### **16.4 Complete Ansible Roles List**

1. `provisionnement-vms-infra` - Provision infrastructure VMs
2. `provisionnement-vms-apps` - Provision application VMs
3. `provisionnement-vms-dmz` - Provision DMZ VMs
4. `prepare-vms` - Configure base VM settings
5. `install-docker-registry` - Deploy private Docker registry
6. `install-vault` - Deploy HashiCorp Vault
7. `install-load-balancer` - Configure HAProxy load balancers
8. `install-gogs` - Deploy Git server
9. `install-rke2-apps` - Deploy RKE2 cluster for applications
10. `install-rke2-middleware` - Deploy RKE2 cluster for middleware
11. `install-rke2-dmz` - Deploy RKE2 cluster for DMZ
12. `install-rancher-server` - Deploy Rancher management platform
13. `install-argocd` - Deploy Argo CD for GitOps
14. `install-cert-manager` - Deploy certificate manager
15. `install-longhorn` - Deploy Longhorn storage
16. `setup-vault-injector` - Configure Vault secret injection
17. `install-minio` - Deploy MinIO object storage
18. `install-minio-backup` - Deploy MinIO backup instance
19. `install-keycloak` - Deploy Keycloak IAM
20. `install-kafka` - Deploy Apache Kafka
21. `install-n8n` - Deploy n8n workflow automation
22. `install-flowable` - Deploy Flowable BPM (if EServices)
23. `install-gravitee-lan` - Deploy Gravitee API Gateway (LAN)
24. `install-gravitee-dmz` - Deploy Gravitee API Gateway (DMZ)
25. `install-neuvector` - Deploy NeuVector security platform
26. `install-monitoring` - Deploy Coroot monitoring
27. `install-eservices` - Deploy EServices application
28. `install-gco` - Deploy GCO application
29. `install-bastion` - Deploy bastion host
30. `install-informix` - Configure Informix database integration
31. `install-seald` - Deploy Seald encryption service
32. `testrole` - Test role for development
33. `testrolefailed` - Test role for failure scenarios
34. `prepare_inputs.py` - Helper script for variable preparation

---

## **Conclusion**

The **Harmonisation Runner** platform represents a comprehensive, production-ready solution for automated deployment of enterprise microservices applications. Its modular architecture, extensive automation capabilities, and user-friendly interface make it an ideal choice for organizations seeking to streamline their infrastructure and application deployment processes.

For additional support or contributions, refer to the project's `AGENTS.md` and component-specific README files.

---

**Document Version:** 1.0  
**Project Version:** Latest  
**Last Updated:** 2025-11-25  
**Repository:** runner-srm-cs
