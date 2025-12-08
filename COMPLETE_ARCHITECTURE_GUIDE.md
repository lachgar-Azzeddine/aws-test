# Complete Architecture Guide - SRM-CS Automation Platform

**Purpose:** Complete, detailed architecture documentation for the SRM-CS platform. Written for anyone to understand, regardless of technical background.

**Audience:** Developers, DevOps engineers, architects, project managers, clients, new team members

**Reading Time:** 60-90 minutes for complete understanding

---

## 📖 Table of Contents

1. [What This Platform Does (Executive Summary)](#1-what-this-platform-does)
2. [Technology Stack Explained (Every Technology)](#2-technology-stack-explained)
3. [High-Level Architecture (The Big Picture)](#3-high-level-architecture)
4. [Project Structure (Every Folder Explained)](#4-project-structure)
5. [The Base Image (harmo-base) Deep Dive](#5-the-base-image-harmo-base)
6. [Backend Architecture (Complete Details)](#6-backend-architecture)
7. [Frontend Architecture](#7-frontend-architecture)
8. [Database Schema (Every Table)](#8-database-schema)
9. [Ansible Automation (How Deployment Works)](#9-ansible-automation)
10. [Docker & Containerization](#10-docker--containerization)
11. [Network Architecture](#11-network-architecture)
12. [Security Architecture](#12-security-architecture)
13. [Data Flow (Step-by-Step)](#13-data-flow)
14. [Deployment Workflow (Complete Process)](#14-deployment-workflow)
15. [Hypervisor Integration (VMware & Nutanix)](#15-hypervisor-integration)
16. [Terraform Integration](#16-terraform-integration)
17. [How Everything Connects](#17-how-everything-connects)

---

## 1. What This Platform Does

### Executive Summary

**The SRM-CS Automation Platform** is an **infrastructure automation and orchestration system** that:

1. **Takes client requirements** (number of users, network configuration, security settings)
2. **Automatically designs** the infrastructure architecture (how many VMs, their specs, network layout)
3. **Provisions virtual machines** on VMware vSphere or Nutanix AHV
4. **Deploys complete application stack** including:
   - Multiple Kubernetes clusters (for applications, middleware, DMZ)
   - Core services (Vault, Docker Registry, Git server)
   - Middleware (Kafka, Keycloak, MinIO)
   - Monitoring (Coroot)
   - Security tools (NeuVector)
   - API gateways (Gravitee)

### In Simple Terms

**Problem it solves:**
- Client: "I need infrastructure for 500 users with secure zones and high availability"
- Without this platform: Months of manual work by DevOps engineers
- With this platform: Automated deployment in hours

**What makes it special:**
- **100% database-driven**: All configuration stored in PostgreSQL
- **Generic**: Works for any client without code changes
- **Automated**: One button deploys everything
- **Multi-hypervisor**: Works with VMware or Nutanix
- **Scalable**: Adapts VM count/sizes based on user load

---

## 2. Technology Stack Explained

### Every Technology and Why It's Used

---

#### 2.1 Programming Languages

**Python 3.11**
- **What it is:** High-level programming language
- **Where used:** Backend API, Ansible roles, repository layer
- **Why chosen:**
  - Excellent libraries for infrastructure automation
  - Ansible compatibility
  - Easy database integration (SQLAlchemy)
  - Fast development

**TypeScript/JavaScript**
- **What it is:** Programming language for web applications
- **Where used:** Frontend (Angular)
- **Why chosen:**
  - Type safety (TypeScript)
  - Angular framework requirement
  - Rich ecosystem for UI components

**Bash/Shell Scripts**
- **What it is:** Linux command-line scripting
- **Where used:** Setup scripts, VM provisioning
- **Why chosen:** Native to Linux, direct system access

---

#### 2.2 Backend Technologies

**FastAPI**
- **What it is:** Modern Python web framework for building APIs
- **What it does:** Creates REST API endpoints
- **Why chosen:**
  - Automatic API documentation (Swagger UI)
  - Fast performance (async support)
  - Built-in validation (Pydantic)
  - Easy to learn and use

**SQLAlchemy**
- **What it is:** Python SQL toolkit and ORM (Object-Relational Mapping)
- **What it does:** Maps Python objects to database tables
- **Why chosen:**
  - Write Python instead of SQL
  - Database-agnostic (works with PostgreSQL, MySQL, etc.)
  - Migration support (Alembic)
  - Relationship management

**Pydantic**
- **What it is:** Data validation library
- **What it does:** Validates API request/response data
- **Why chosen:**
  - Automatic type checking
  - Clear error messages
  - FastAPI integration

**Ansible Runner**
- **What it is:** Python library to run Ansible programmatically
- **What it does:** Executes Ansible roles from Python code
- **Why chosen:**
  - Integration with backend API
  - Status tracking (role execution progress)
  - Dynamic variable passing

**Uvicorn**
- **What it is:** ASGI server (like Nginx for Python apps)
- **What it does:** Runs the FastAPI application
- **Why chosen:**
  - Fast async support
  - Production-ready
  - Hot reload in development

---

#### 2.3 Frontend Technologies

**Angular 16+**
- **What it is:** TypeScript framework for building web applications
- **What it does:** Creates the user interface (wizard, dashboards)
- **Why chosen:**
  - Component-based architecture
  - TypeScript support
  - Rich ecosystem (Angular Material)
  - Enterprise-grade

**Angular Material**
- **What it is:** UI component library
- **What it does:** Provides ready-made UI components (buttons, forms, tables)
- **Why chosen:**
  - Professional look
  - Accessibility built-in
  - Consistent design

**RxJS**
- **What it is:** Reactive programming library
- **What it does:** Handles asynchronous operations (API calls)
- **Why chosen:**
  - Angular integration
  - Powerful data stream management
  - Error handling

---

#### 2.4 Database Technologies

**PostgreSQL 15**
- **What it is:** Relational database management system (RDBMS)
- **What it does:** Stores all platform configuration and state
- **Why chosen:**
  - ACID compliance (data integrity)
  - JSON support (flexible data)
  - Advanced features (foreign keys, transactions)
  - Open-source, reliable

**Alembic**
- **What it is:** Database migration tool
- **What it does:** Manages database schema changes over time
- **Why chosen:**
  - Version control for database
  - Safe schema updates
  - Rollback capability

---

#### 2.5 Automation & Configuration

**Ansible 2.16+**
- **What it is:** IT automation tool
- **What it does:** Configures servers, installs software, orchestrates deployments
- **Why chosen:**
  - Agentless (uses SSH)
  - Declarative (describe desired state, not steps)
  - Idempotent (safe to run multiple times)
  - Huge module library (Kubernetes, Docker, VMware, etc.)

**Ansible Collections:**
  - `kubernetes.core` - Kubernetes management
  - `community.vmware` - VMware vSphere integration
  - `community.docker` - Docker management

**Jinja2**
- **What it is:** Template engine
- **What it does:** Generates configuration files dynamically
- **Where used:** Ansible templates (Kubernetes manifests, configs)
- **Why chosen:**
  - Variables in templates
  - Control flow (if/for loops)
  - Python integration

---

#### 2.6 Containerization & Orchestration

**Docker 27.x**
- **What it is:** Container platform
- **What it does:** Packages applications with dependencies into containers
- **Why chosen:**
  - Consistent environment (dev = prod)
  - Fast startup
  - Resource isolation
  - Image versioning

**Docker Compose**
- **What it is:** Multi-container orchestration tool
- **What it does:** Runs multiple Docker containers together
- **Where used:** Local development (backend + frontend + postgres + nginx)
- **Why chosen:**
  - Simple YAML configuration
  - Single command to start all services
  - Volume management

**Kubernetes (RKE2)**
- **What it is:** Container orchestration platform
- **What it does:** Manages containerized applications at scale
- **Why chosen:**
  - Auto-scaling
  - Self-healing (restarts failed containers)
  - Load balancing
  - Service discovery
  - Industry standard

**RKE2 (Rancher Kubernetes Engine 2)**
- **What it is:** Kubernetes distribution by SUSE
- **What it does:** Hardened, production-ready Kubernetes
- **Why chosen:**
  - Security-focused
  - Embedded etcd (high availability)
  - Easy multi-cluster setup
  - FIPS 140-2 compliance

---

#### 2.7 Infrastructure & Hypervisors

**VMware vSphere**
- **What it is:** Enterprise virtualization platform
- **What it does:** Creates and manages virtual machines
- **Components:**
  - vCenter: Central management
  - ESXi: Hypervisor (runs VMs)
- **Why supported:**
  - Most common enterprise hypervisor
  - Mature ecosystem
  - Advanced features (vMotion, DRS, HA)

**Nutanix AHV**
- **What it is:** Hyper-converged infrastructure platform
- **What it does:** Combines compute, storage, virtualization
- **Components:**
  - Prism Central: Management UI
  - AHV: Hypervisor
- **Why supported:**
  - Simpler than VMware
  - Lower licensing costs
  - Integrated storage (Nutanix Files)
  - API-first design

**pyvmomi**
- **What it is:** Python SDK for VMware vSphere
- **What it does:** Programmatic access to vCenter API
- **Why used:** Automate VM creation, configuration, deletion

**Terraform (Optional)**
- **What it is:** Infrastructure as Code (IaC) tool
- **What it does:** Provisions infrastructure declaratively
- **Where used:** Alternative to Ansible for VM provisioning
- **Why supported:**
  - State management
  - Plan/apply workflow
  - Multi-cloud support

---

#### 2.8 Kubernetes Tools

**Longhorn**
- **What it is:** Distributed block storage for Kubernetes
- **What it does:** Provides persistent volumes for stateful apps
- **Why chosen:**
  - Cloud-native (CNCF project)
  - Replication across nodes
  - Snapshot/backup support
  - Simple deployment

**cert-manager**
- **What it is:** Kubernetes certificate management
- **What it does:** Automatically generates and renews TLS certificates
- **Why chosen:**
  - Let's Encrypt integration
  - Automated renewal
  - CRD-based (Kubernetes-native)

**ArgoCD**
- **What it is:** GitOps continuous deployment tool
- **What it does:** Syncs Kubernetes resources from Git repositories
- **Why chosen:**
  - Git as single source of truth
  - Automated sync
  - Visual UI for deployments
  - Rollback capability

**Helm**
- **What it is:** Kubernetes package manager
- **What it does:** Installs complex applications with one command
- **Why used:**
  - Templating (customize deployments)
  - Dependency management
  - Version control

---

#### 2.9 Middleware & Applications

**HashiCorp Vault**
- **What it is:** Secrets management system
- **What it does:** Securely stores and distributes secrets (passwords, API keys)
- **Why chosen:**
  - Encryption at rest and in transit
  - Access policies
  - Audit logging
  - Dynamic secrets

**Apache Kafka**
- **What it is:** Distributed event streaming platform
- **What it does:** Message broker for microservices
- **Why included:**
  - High throughput
  - Fault-tolerant
  - Event sourcing
  - Real-time processing

**Keycloak**
- **What it is:** Identity and Access Management (IAM)
- **What it does:** Single Sign-On (SSO), user authentication
- **Why included:**
  - LDAP/AD integration
  - OAuth2/OIDC support
  - Multi-factor authentication
  - User federation

**MinIO**
- **What it is:** S3-compatible object storage
- **What it does:** Stores files, images, backups
- **Why included:**
  - AWS S3 API compatible
  - Open-source
  - Distributed mode (HA)
  - Kubernetes-native

**Gogs**
- **What it is:** Lightweight Git server
- **What it does:** Hosts Git repositories
- **Why chosen:**
  - Lightweight (vs GitLab)
  - Self-hosted
  - Simple API
  - Fast

**Docker Registry**
- **What it is:** Private container image registry
- **What it does:** Stores Docker images
- **Why needed:**
  - Air-gapped deployments
  - Image versioning
  - Faster pulls (local network)

**Gravitee**
- **What it is:** API Management platform
- **What it does:** API gateway, rate limiting, analytics
- **Why included:**
  - API security
  - Rate limiting
  - Monitoring
  - Developer portal

---

#### 2.10 Monitoring & Security

**Coroot**
- **What it is:** Observability platform
- **What it does:** Monitors applications, infrastructure, logs
- **Why chosen:**
  - Zero-config (automatic service discovery)
  - Root cause analysis
  - ClickHouse for metrics storage
  - Open-source

**NeuVector**
- **What it is:** Container security platform
- **What it does:** Runtime protection, vulnerability scanning
- **Why included:**
  - Zero-trust security
  - Network segmentation
  - Compliance reporting
  - Threat detection

**Rancher**
- **What it is:** Kubernetes management platform
- **What it does:** Multi-cluster management UI
- **Why included:**
  - Centralized management
  - RBAC
  - Monitoring dashboards
  - User-friendly

---

#### 2.11 Networking

**Calico**
- **What it is:** Kubernetes networking plugin (CNI)
- **What it does:** Pod networking, network policies
- **Why chosen:**
  - Network policy support
  - BGP routing
  - Performance
  - Security (zero-trust)

**HAProxy**
- **What it is:** Load balancer
- **What it does:** Distributes traffic across Kubernetes nodes
- **Why used:**
  - High availability
  - Health checks
  - SSL termination
  - Layer 4/7 load balancing

**Keepalived**
- **What it is:** Virtual IP (VIP) management
- **What it does:** Floating IP between load balancers
- **Why used:**
  - Automatic failover
  - VRRP protocol
  - No single point of failure

---

#### 2.12 Web Server

**Nginx**
- **What it is:** Web server and reverse proxy
- **What it does:** Serves frontend, proxies to backend API
- **Why chosen:**
  - Fast
  - Reverse proxy (route /runner/api → backend)
  - Static file serving (frontend)
  - SSL termination

---

#### 2.13 Development Tools

**Git**
- **What it is:** Version control system
- **What it does:** Tracks code changes
- **Why used:** Source code management

**VS Code / PyCharm**
- **What it is:** Code editors
- **What it does:** Write and debug code
- **Why used:** Developer productivity

**Postman / cURL**
- **What it is:** API testing tools
- **What it does:** Test REST API endpoints
- **Why used:** Backend API testing

---

## 3. High-Level Architecture

### The Big Picture

```
┌─────────────────────────────────────────────────────────────────────┐
│                        USER'S WEB BROWSER                            │
│                                                                      │
│  Accesses: http://localhost/runner/ or https://platform.client.com  │
└────────────────────────────┬─────────────────────────────────────────┘
                             │ HTTPS
                             ▼
┌──────────────────────────────────────────────────────────────────────┐
│                           NGINX (Port 80/443)                         │
│                         Reverse Proxy + Static Files                 │
│                                                                       │
│  Routes:                                                              │
│  - /runner/             → Frontend (Angular SPA)                     │
│  - /runner/api/         → Backend API                                │
│  - /corteza/            → Corteza (Low-code platform)                │
└────────────┬────────────────────────────┬──────────────────────────────┘
             │                            │
             ▼                            ▼
┌─────────────────────────┐   ┌──────────────────────────────────────┐
│    FRONTEND CONTAINER    │   │       BACKEND CONTAINER              │
│    (Angular 16+)         │   │       (FastAPI + Python 3.12+3.7)    │
│                          │   │                                      │
│  - Wizard UI             │   │  Layers:                             │
│  - Configuration forms   │   │  1. API Layer (api.py)               │
│  - VM visualization      │◄──┤     - REST endpoints                 │
│  - Deployment status     │   │     - Request validation             │
│                          │   │                                      │
│  Port: 80                │   │  2. Repository Layer (repository.py) │
│  (Production)            │   │     - Business logic                 │
└──────────────────────────┘   │     - Database queries               │
                               │     - VM scaffolding                 │
                               │                                      │
                               │  3. Ansible Integration              │
                               │     - Role execution                 │
                               │     - Variable passing               │
                               │                                      │
                               │  Port: 8008                          │
                               └──────────┬───────────────────────────┘
                                          │
                                          ▼
                               ┌──────────────────────────────────────┐
                               │   POSTGRESQL 15 CONTAINER            │
                               │   (Database)                         │
                               │                                      │
                               │  Stores:                             │
                               │  - VM configurations                 │
                               │  - Hypervisor credentials            │
                               │  - Network zones                     │
                               │  - Security settings                 │
                               │  - Deployment state                  │
                               │  - Vault keys/tokens                 │
                               │                                      │
                               │  Port: 5432                          │
                               └──────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────┐
│                    BACKEND EXECUTES ANSIBLE ROLES                     │
│                                                                       │
│  Backend uses harmo-base Docker image which contains:                │
│  - Ansible 2.16+                                                      │
│  - Python 3.12 (FastAPI) + Python 3.7 (Informix)                     │
│  - kubectl, helm, terraform, govc, mc, rke2                          │
│  - VMware tools (pyvmomi, govc)                                      │
│  - IBM Informix Client SDK 4.50.FC11W1                               │
│                                                                       │
│  Ansible roles in: backend/project/roles/                            │
│  - 32 roles for complete infrastructure deployment                   │
└──────────────────┬────────────────────────────────────────────────────┘
                   │
                   │ SSH (using keys from database)
                   ▼
┌──────────────────────────────────────────────────────────────────────┐
│              CLIENT INFRASTRUCTURE (VMware or Nutanix)                │
│                                                                       │
│  ┌─────────────────────────────────────────────────────────────────┐ │
│  │  LAN_INFRA ZONE (10.1.10.0/24)                                 │ │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐           │ │
│  │  │   vault1    │  │  gitops1    │  │ monitoring1 │           │ │
│  │  │             │  │             │  │             │           │ │
│  │  │  Vault      │  │  Gogs       │  │  Coroot     │           │ │
│  │  │  8200       │  │  Registry   │  │  Prometheus │           │ │
│  │  └─────────────┘  │  ArgoCD     │  │  Grafana    │           │ │
│  │                   └─────────────┘  └─────────────┘           │ │
│  └─────────────────────────────────────────────────────────────────┘ │
│                                                                       │
│  ┌─────────────────────────────────────────────────────────────────┐ │
│  │  LAN_APPS ZONE (10.1.20.0/24)                                  │ │
│  │  ┌──────────────────────────────────────────────────────────┐ │ │
│  │  │  RKE2-APPS Kubernetes Cluster                            │ │ │
│  │  │  ┌────────────┐  ┌────────────┐  ┌────────────┐         │ │ │
│  │  │  │ rkeapp-    │  │ rkeapp-    │  │ rkeapp-    │         │ │ │
│  │  │  │ master1    │  │ master2    │  │ master3    │         │ │ │
│  │  │  │ (control)  │  │ (control)  │  │ (control)  │         │ │ │
│  │  │  └────────────┘  └────────────┘  └────────────┘         │ │ │
│  │  │  ┌────────────┐  ┌────────────┐                         │ │ │
│  │  │  │ rkeapp-    │  │ rkeapp-    │                         │ │ │
│  │  │  │ worker1    │  │ worker2    │  ...                    │ │ │
│  │  │  │            │  │            │                         │ │ │
│  │  │  └────────────┘  └────────────┘                         │ │ │
│  │  │                                                          │ │ │
│  │  │  Runs: Business applications                            │ │ │
│  │  └──────────────────────────────────────────────────────────┘ │ │
│  └─────────────────────────────────────────────────────────────────┘ │
│                                                                       │
│  ┌─────────────────────────────────────────────────────────────────┐ │
│  │  LAN_MIDDLEWARE ZONE (10.1.30.0/24) - Optional                │ │
│  │  ┌──────────────────────────────────────────────────────────┐ │ │
│  │  │  RKE2-MIDDLEWARE Kubernetes Cluster                      │ │ │
│  │  │  ┌────────────┐  ┌────────────┐  ┌────────────┐         │ │ │
│  │  │  │rkemiddleware│  │rkemiddleware│  │rkemiddleware│       │ │ │
│  │  │  │ master1    │  │ master2    │  │ master3    │         │ │ │
│  │  │  └────────────┘  └────────────┘  └────────────┘         │ │ │
│  │  │                                                          │ │ │
│  │  │  Runs: Kafka, Keycloak, MinIO                           │ │ │
│  │  └──────────────────────────────────────────────────────────┘ │ │
│  └─────────────────────────────────────────────────────────────────┘ │
│                                                                       │
│  ┌─────────────────────────────────────────────────────────────────┐ │
│  │  DMZ ZONE (10.1.200.0/24) - Optional                          │ │
│  │  ┌──────────────────────────────────────────────────────────┐ │ │
│  │  │  RKE2-DMZ Kubernetes Cluster                             │ │ │
│  │  │  ┌────────────┐  ┌────────────┐  ┌────────────┐         │ │ │
│  │  │  │  rkedmz1   │  │  rkedmz2   │  │  rkedmz3   │         │ │ │
│  │  │  │ (all roles)│  │ (all roles)│  │ (all roles)│         │ │ │
│  │  │  └────────────┘  └────────────┘  └────────────┘         │ │ │
│  │  │                                                          │ │ │
│  │  │  Runs: Gravitee API Gateway (external-facing)           │ │ │
│  │  └──────────────────────────────────────────────────────────┘ │ │
│  │  ┌────────────┐  ┌────────────┐                             │ │
│  │  │  lbdmz1    │  │  lbdmz2    │  (Load Balancers)           │ │
│  │  └────────────┘  └────────────┘                             │ │
│  └─────────────────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────────────┘
```

### Architecture Layers

**Layer 1: Presentation Layer**
- User interacts via web browser
- Angular frontend (wizard, forms, dashboards)
- Nginx serves static files and routes API calls

**Layer 2: API Layer**
- FastAPI backend receives HTTP requests
- Validates input with Pydantic
- Routes to appropriate repository function

**Layer 3: Business Logic Layer**
- Repository pattern handles all business logic
- VM scaffolding (calculates VM architecture)
- Database operations (CRUD)
- Ansible role orchestration

**Layer 4: Data Layer**
- PostgreSQL stores all state
- SQLAlchemy ORM maps Python ↔ SQL
- Transactions ensure data integrity

**Layer 5: Automation Layer**
- Ansible roles execute infrastructure tasks
- Dynamic variable loading from database (prepare_inputs.py)
- SSH to target VMs

**Layer 6: Infrastructure Layer**
- VMware/Nutanix hypervisors
- Physical servers
- Network switches, firewalls

---

## 4. Project Structure

### Complete Directory Layout

```
runner-srm-cs-genric/
├── backend/                          # Backend API + Ansible
│   ├── project/                      # Ansible project
│   │   ├── roles/                    # 32 Ansible roles
│   │   │   ├── provisionnement-vms-infra/
│   │   │   │   ├── prepare_inputs.py  # Variables from database
│   │   │   │   ├── tasks/
│   │   │   │   │   └── main.yml      # Ansible tasks
│   │   │   │   ├── templates/        # Jinja2 templates
│   │   │   │   ├── files/            # Static files
│   │   │   │   └── requirements.txt  # Python dependencies
│   │   │   │
│   │   │   ├── install-vault/
│   │   │   ├── install-rke2-apps/
│   │   │   ├── install-argocd/
│   │   │   └── ... (28 more roles)
│   │   │
│   │   └── ansible.cfg               # Ansible configuration
│   │
│   ├── tests/                        # Test directory
│   ├── doc/                          # Backend documentation
│   ├── architecture-docs/            # MkDocs architecture docs
│   │
│   ├── api.py                        # FastAPI application (API endpoints)
│   ├── repository.py                 # Business logic + database operations
│   ├── models.py                     # SQLAlchemy ORM models + Pydantic schemas
│   ├── install.py                    # Ansible role orchestration
│   ├── initial_db.py                 # Database initialization
│   ├── entrypoint.sh                 # Container entrypoint script
│   ├── requirements.txt              # Python dependencies
│   ├── Dockerfile                    # Backend container (FROM mrabbah/harmo-base:latest)
│   ├── docker-compose.yml            # Local testing compose file
│   └── test_*.py                     # Individual test files
│
├── frontend/                         # Angular frontend
│   ├── src/
│   │   ├── app/
│   │   │   ├── components/
│   │   │   │   ├── hypervisor-config/    # Step 1: Hypervisor
│   │   │   │   ├── zone-config/          # Step 2: Zones
│   │   │   │   ├── security-config/      # Step 3: Security
│   │   │   │   ├── external-services/    # Step 4: LDAP, SMTP
│   │   │   │   ├── user-count/           # Step 5: User count
│   │   │   │   ├── vm-architecture/      # Step 6: VM review
│   │   │   │   └── deployment/           # Step 7: Deploy
│   │   │   │
│   │   │   ├── services/
│   │   │   │   ├── api.service.ts        # HTTP client
│   │   │   │   └── websocket.service.ts  # Real-time updates
│   │   │   │
│   │   │   ├── models/
│   │   │   │   ├── hypervisor.model.ts
│   │   │   │   ├── zone.model.ts
│   │   │   │   └── vm.model.ts
│   │   │   │
│   │   │   └── app.module.ts            # Angular module
│   │   │
│   │   ├── assets/                      # Images, icons
│   │   └── index.html                   # Entry point
│   │
│   ├── angular.json                     # Angular configuration
│   ├── package.json                     # npm dependencies
│   ├── tsconfig.json                    # TypeScript configuration
│   └── Dockerfile                       # Frontend container build
│
├── harmo-base/                       # Base Docker image
│   ├── Dockerfile                    # Image definition (Ubuntu 24.04 base)
│   ├── requirements.txt              # Python packages
│   ├── informix_dependencies/        # IBM Informix client SDK
│   │   ├── ibm.csdk.4.50.FC11W1.LNX.tar
│   │   └── jdk-11.0.25_linux-x64_bin.deb
│   └── informix_test.py              # Informix connection test
│
├── nginx/                            # Nginx reverse proxy
│   ├── nginx.conf                    # Nginx configuration
│   └── Dockerfile                    # Nginx container build
│
├── corteza/                          # Corteza low-code platform (optional)
│   └── docker-compose.yml
│
├── data/                             # Persistent data
│   ├── postgres/                     # PostgreSQL data directory
│   └── logs/                         # Application logs
│
├── docs/                             # Documentation (YOU ARE HERE!)
│   ├── CLAUDE.md
│   ├── BACKEND_DEEP_DIVE.md
│   ├── ANSIBLE_ROLES_EXPLAINED.md
│   ├── CLOUD_PROVIDER_ADAPTATION_GUIDE.md
│   └── ... (other guides)
│
├── docker-compose.yml                # Main orchestration file
├── .gitignore                        # Git ignore rules
├── README.md                         # Project README
└── LICENSE                           # License file
```

---

## 5. The Base Image (mrabbah/harmo-base)

### What is the mrabbah/harmo-base Image?

**Purpose:** The `mrabbah/harmo-base:latest` Docker image is a **pre-built Ubuntu 24.04 image** available on Docker Hub that contains ALL the tools and dependencies needed for infrastructure automation.

**Image Location:** `mrabbah/harmo-base:latest` (public Docker Hub registry)

**Note:** The source Dockerfile for this image is in the `harmo-base/` directory, but the backend uses the pre-built image from Docker Hub rather than building locally.

### Why Does It Exist?

**Problem:**
- The backend needs to run Ansible roles
- Ansible needs many tools: kubectl, helm, terraform, VMware tools, etc.
- Installing these during backend startup takes 10-15 minutes
- Different roles need different tools

**Solution:**
- Pre-build an image with EVERYTHING installed
- Backend container uses this image as its base
- Startup time: seconds instead of minutes
- Consistent environment every time

### What's Inside harmo-base?

Let's break down the Dockerfile line by line:

---

#### 5.1 Base Operating System

```dockerfile
FROM ubuntu:24.04
```

**What:** Ubuntu 24.04 LTS (Long Term Support)
**Why:** Stable, well-supported, large package repository

---

#### 5.2 System Update

```dockerfile
RUN apt-get update && apt-get upgrade -y
```

**What:** Updates package lists and upgrades installed packages
**Why:** Security patches, latest versions

---

#### 5.3 Core System Packages

```dockerfile
RUN apt-get install -y --fix-broken \
    rsync          # File synchronization
    sudo           # Superuser privileges
    python3        # Python 3.12 (Ubuntu 24.04 default)
    python3-pip    # Python package installer
    python3-venv   # Virtual environment support
    git            # Version control
    curl wget      # HTTP clients
    vim            # Text editor
    sshpass        # SSH with password (initial connections)
    openssl        # Encryption/certificates
    openssh-client # SSH client
    gnupg2         # GPG encryption
    p7zip-full     # 7zip compression
    zip unzip      # Zip compression
    netcat-openbsd # Network utility
    netcat-traditional # Alternative netcat
    docker.io      # Docker client (for registry operations)
    libssl-dev     # SSL development headers
    libffi-dev     # FFI development headers
    expect         # Automated interactive programs
    file           # File type detection
```

**Why each package:**
- `rsync`: Efficient file copying (used in some Ansible tasks)
- `sudo`: Run commands as root (Ansible privilege escalation)
- `python3`: Required for Ansible
- `git`: Clone repositories (Gogs integration)
- `curl/wget`: Download files, API calls
- `sshpass`: Initial SSH connection with password before keys are set up
- `openssh-client`: SSH to VMs
- `docker.io`: Interact with Docker Registry
- `expect`: Automate Informix SDK installation (interactive installer)
- Library packages (`libssl-dev`, etc.): Required for Python packages

---

#### 5.4 Kubernetes Tools

**kubectl (Kubernetes CLI)**

```dockerfile
RUN wget https://dl.k8s.io/release/v1.31.1/bin/linux/amd64/kubectl \
    -O /usr/local/bin/kubectl
RUN chmod +x /usr/local/bin/kubectl
```

**What:** Command-line tool for Kubernetes
**Why:** Manage Kubernetes clusters (deploy apps, check status, etc.)
**Version:** 1.31.1 (matches RKE2 version)

---

**mc (MinIO Client)**

```dockerfile
RUN wget https://dl.min.io/client/mc/release/linux-amd64/mc \
    -O /usr/local/bin/mc
RUN chmod +x /usr/local/bin/mc
```

**What:** Command-line client for MinIO (S3-compatible storage)
**Why:** Manage MinIO buckets, upload/download files
**Usage:** Configure S3 backups, manage object storage

---

**Terraform**

```dockerfile
RUN wget https://releases.hashicorp.com/terraform/1.9.8/terraform_1.9.8_linux_amd64.zip \
    -O /tmp/terraform.zip
RUN unzip /tmp/terraform.zip -d /usr/local/bin
RUN rm /tmp/terraform.zip
RUN chmod +x /usr/local/bin/terraform
```

**What:** Infrastructure as Code tool
**Why:** Alternative to Ansible for VM provisioning
**Version:** 1.9.8
**Usage:** `terraform apply` to provision VMs on VMware/Nutanix

---

**govc (VMware CLI)**

```dockerfile
RUN wget https://github.com/vmware/govmomi/releases/download/v0.45.0/govc_Linux_x86_64.tar.gz \
    -O /tmp/govc.tar.gz
RUN tar -xvf /tmp/govc.tar.gz -C /usr/local/bin
RUN rm /tmp/govc.tar.gz
RUN chmod +x /usr/local/bin/govc
```

**What:** Command-line tool for VMware vSphere
**Why:** Interact with vCenter API (list VMs, datastores, networks)
**Version:** 0.45.0
**Usage:** `govc vm.info vault1` to get VM details

---

**RKE2**

```dockerfile
RUN wget https://github.com/rancher/rke2/releases/download/v1.31.1%2Brke2r2/rke2.linux-amd64 \
    -O /usr/local/bin/rke2
RUN chmod +x /usr/local/bin/rke2
```

**What:** Rancher Kubernetes Engine 2 binary
**Why:** Kubernetes distribution used for clusters
**Version:** 1.31.1+rke2r2
**Usage:** Installed on VMs to create Kubernetes clusters

---

**Helm**

```dockerfile
RUN HELM_VERSION=v3.15.4 && \
    curl -fsSL https://get.helm.sh/helm-${HELM_VERSION}-linux-amd64.tar.gz -o helm.tar.gz && \
    tar -xzf helm.tar.gz && \
    mv linux-amd64/helm /usr/local/bin/helm && \
    rm -rf linux-amd64 helm.tar.gz
```

**What:** Kubernetes package manager
**Why:** Install complex apps (ArgoCD, Rancher, NeuVector) with one command
**Version:** 3.15.4
**Usage:** `helm install argocd argo/argocd`

---

#### 5.5 Python 3.7 Installation (Special)

```dockerfile
RUN wget https://www.python.org/ftp/python/3.7.10/Python-3.7.10.tar.xz
RUN tar -xvf Python-3.7.10.tar.xz
RUN cd Python-3.7.10 && \
    ./configure --enable-optimizations --with-ensurepip && \
    make -j$(nproc) && \
    make altinstall
RUN rm Python-3.7.10.tar.xz && rm -rf Python-3.7.10
```

**What:** Compiles Python 3.7.10 from source
**Why:** IBM Informix Python client (ifxpy) only works with Python 3.7
**Why `altinstall`:** Installs as `python3.7` (doesn't replace system `python3`)
**Time:** Takes ~5-10 minutes during image build

---

#### 5.6 IBM Informix Client SDK

```dockerfile
# Copy Informix dependencies
COPY ./informix_dependencies/ibm.csdk.4.50.FC11W1.LNX.tar /opt/
COPY ./informix_dependencies/jdk-11.0.25_linux-x64_bin.deb /opt/

# Extract SDK
RUN mkdir /opt/informix-installer && \
    tar -xvf /opt/ibm.csdk.4.50.FC11W1.LNX.tar -C /opt/informix-installer

# Install Java JDK (required by Informix installer)
RUN dpkg -i /opt/jdk-11.0.25_linux-x64_bin.deb

# Cleanup downloads
RUN rm /opt/ibm.csdk.4.50.FC11W1.LNX.tar && \
    rm /opt/jdk-11.0.25_linux-x64_bin.deb
```

**What:** IBM Informix Client SDK (database client)
**Why:** Connect to IBM Informix databases (legacy enterprise database)
**Version:** 4.50.FC11W1
**Size:** ~200 MB

---

**Automated Informix SDK Installation**

```dockerfile
RUN chmod +x /opt/informix-installer/installclientsdk && expect -c ' \
  set timeout 30; \
  spawn /opt/informix-installer/installclientsdk; \
  expect "PRESS <ENTER> TO CONTINUE: "; \
  send "\r"; \
  sleep 5; \
  expect "Press Enter to continue... or enter \"1\" to accept...: "; \
  send "1\r"; \
  sleep 5; \
  expect "ENTER AN ABSOLUTE PATH, OR PRESS <ENTER> TO ACCEPT THE DEFAULT\r\t: "; \
  send "\r"; \
  sleep 5; \
  expect "ENTER THE NUMBER FOR YOUR CHOICE...: "; \
  send "2\r"; \
  sleep 5; \
  expect "Press <ENTER> to install above selected features...: "; \
  send "\r"; \
  expect "PRESS <ENTER> TO CONTINUE: "; \
  send "\r"; \
  expect "PRESS <ENTER> TO EXIT THE INSTALLER: "; \
  send "\r"; \
  '
RUN rm -rf /opt/informix-installer
```

**What:** Uses `expect` to automate interactive Informix installer
**Why:** Installer is interactive (requires user input), can't be scripted normally
**How it works:**
1. Spawns installer process
2. Waits for prompts
3. Sends responses (Enter, "1" to accept license, etc.)
4. Installs to default location: `/opt/IBM/Informix.4.50.FC11W1/`

---

**Informix Environment Variables**

```dockerfile
RUN touch /opt/IBM/Informix.4.50.FC11W1/etc/sqlhosts

ENV INFORMIXDIR='/opt/IBM/Informix.4.50.FC11W1'
ENV CSDK_HOME=${INFORMIXDIR}
ENV PATH=$INFORMIXDIR/bin:$PATH
ENV LD_LIBRARY_PATH=$INFORMIXDIR/lib:$INFORMIXDIR/lib/esql:$INFORMIXDIR/lib/cli
```

**What:** Sets environment variables for Informix
**Why:**
- Programs can find Informix libraries
- `dbaccess` and other Informix commands work
- Python `ifxpy` module can locate SDK

---

#### 5.7 User Setup

```dockerfile
RUN useradd -ms /bin/bash devops
RUN usermod -aG docker devops
```

**What:** Creates non-root user `devops`
**Why:**
- Security: Don't run as root
- Matches VM user (consistency)
- Docker group: Can run docker commands

---

#### 5.8 Python Virtual Environments

**Python 3.7 Virtual Environment (for Informix)**

```dockerfile
USER devops
RUN python3.7 -m venv /home/devops/venv_37
RUN /home/devops/venv_37/bin/pip install ifxpy==3.0.2
COPY ./informix_test.py /home/devops/venv_37
```

**What:** Separate Python 3.7 environment with `ifxpy`
**Why:**
- `ifxpy` only works with Python 3.7
- Isolate from main Python 3.11/3.12
**Usage:**
```bash
# Test Informix connection
/home/devops/venv_37/bin/python informix_test.py
```

---

**Python 3.11/3.12 Virtual Environment (main)**

```dockerfile
RUN python3 -m venv /home/devops/venv
ENV PATH="/home/devops/venv/bin:$PATH"
```

**What:** Main Python virtual environment (uses Ubuntu's Python 3.12)
**Why:**
- Isolation from system Python
- Clean dependencies
- Ansible will be installed here

---

#### 5.9 Ansible Installation

```dockerfile
RUN pip3 install --no-cache-dir ansible
RUN pip3 install --no-cache-dir kubernetes PyYAML jsonpatch jmespath
RUN ansible-galaxy collection install kubernetes.core
```

**What:**
- `ansible`: Ansible automation tool
- `kubernetes`: Kubernetes Python client (for Ansible k8s modules)
- `PyYAML`: YAML parsing
- `jsonpatch`: JSON manipulation
- `jmespath`: JSON querying
- `kubernetes.core`: Ansible collection for Kubernetes

**Why:**
- Ansible is the automation engine
- Kubernetes modules manage K8s resources
- Collections provide pre-built modules

---

#### 5.10 Python Application Dependencies

```dockerfile
WORKDIR /home/devops
COPY ./requirements.txt .
USER root
RUN chown devops:devops requirements.txt
USER devops
RUN /home/devops/venv/bin/pip install --no-cache-dir -r /home/devops/requirements.txt
```

**What:** Installs all Python packages needed by backend
**File:** `harmo-base/requirements.txt`

**Key packages in requirements.txt:**
```
fastapi==0.115.0           # Web framework
uvicorn[standard]==0.31.0  # ASGI server
sqlalchemy==2.0.35         # ORM
psycopg2-binary==2.9.9     # PostgreSQL driver
pydantic==2.9.2            # Data validation
ansible-runner==2.4.0      # Programmatic Ansible
hvac==2.3.0                # Vault client
pyvmomi==8.0.3.0.1         # VMware vSphere SDK
requests==2.32.3           # HTTP client
cryptography==43.0.1       # Encryption
python-multipart==0.0.12   # File uploads
websockets==13.1           # WebSocket support
```

---

#### 5.11 Cleanup

```dockerfile
USER root
RUN apt-get clean
USER devops
```

**What:** Removes apt cache to reduce image size
**Why:** Image smaller = faster to download/transfer

---

### How Backend Uses harmo-base

**In `backend/Dockerfile`:**

```dockerfile
FROM mrabbah/harmo-base:latest

# Copy application code
COPY . /home/devops/backend/
WORKDIR /home/devops/backend

# Backend is ready to run!
CMD ["gunicorn", "--workers", "2", "--timeout", "3600", \
     "--worker-class", "uvicorn.workers.UvicornWorker", \
     "--bind", "0.0.0.0:8008", "api:app"]
```

**Flow:**
1. `docker-compose.yml` specifies backend service
2. Backend Dockerfile uses `FROM mrabbah/harmo-base:latest` (pulls from Docker Hub)
3. harmo-base contains ALL tools (no installation needed)
4. Backend just copies application code
5. Backend starts instantly (no wait for package installs)

---

### Building harmo-base (Reference Only)

**Note:** The backend automatically pulls `mrabbah/harmo-base:latest` from Docker Hub. You **don't need to build it locally** unless you're modifying the base image.

**If you need to build it locally (for development):**

```bash
# Navigate to harmo-base directory
cd harmo-base/

# Build image (takes 20-30 minutes first time)
docker build -t mrabbah/harmo-base:latest .

# Check image size
docker images mrabbah/harmo-base
# mrabbah/harmo-base    latest    abc123    2.5 GB

# Push to Docker Hub (requires login and permissions)
docker push mrabbah/harmo-base:latest

# Now backend will use this image
cd ..
docker-compose up -d backend  # Pulls from Docker Hub or uses local
```

---

### Image Size Breakdown

| Component | Size |
|-----------|------|
| Ubuntu 24.04 base | 80 MB |
| System packages | 200 MB |
| Python 3.7 (compiled) | 50 MB |
| Informix SDK | 200 MB |
| kubectl, helm, terraform, etc. | 150 MB |
| Python packages (Ansible, etc.) | 300 MB |
| Docker layers overhead | 100 MB |
| **Total** | **~2.5 GB** |

---

## 6. Backend Architecture

### Complete Backend Details

---

### 6.1 Backend Entry Point (api.py)

**Purpose:** Defines REST API endpoints

**Structure:**

```python
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
import repository as repo
from models import (
    ConfigurationModel, VMwareEsxiModel, NutanixAHVModel,
    ZoneModel, VirtualMachineModel, SecurityModel,
    AnsibleRoleModel, TaskLogModel, # ... and more
)

# Create FastAPI app
app = FastAPI()

# Enable CORS (frontend can call API from different origin)
origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database session
_, Session = repo.get_session()

# ============================================================================
# HYPERVISOR ENDPOINTS
# ============================================================================

@app.post("/vmware", response_model=VMwareEsxiModel)
def add_vmware(vmware: VMwareEsxiModel):
    """
    Add VMware vSphere configuration.

    Note: Nginx proxies /runner/api/vmware → /vmware on backend
    So users call: http://localhost/runner/api/vmware
    But backend receives: /vmware
    """
    try:
        vmware_id = repo.add_vmware_esxi_configuration(
            alias=vmware.alias,
            login=vmware.login,
            password=vmware.password,
            api_url=vmware.api_url,
            datacenter_name=vmware.datacenter_name,
            cluster_name=vmware.cluster_name,
            datastore_name=vmware.datastore_name,
            resource_pool_name=vmware.resource_pool_name,
            Session=Session
        )
        return {"id": vmware_id, "message": "VMware configuration added"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/vmware")
def get_vmware():
    """Get VMware configuration."""
    vmware = repo.get_vmware_esxi_configuration(Session)
    if not vmware:
        raise HTTPException(status_code=404, detail="VMware not configured")
    return vmware

# ============================================================================
# ZONE ENDPOINTS
# ============================================================================

@app.post("/zones", status_code=201)
def add_zone(zone: ZoneModel):
    """Add network zone."""
    zone_id = repo.add_zone(
        name=zone.name,
        sub_network=zone.sub_network,
        network_mask=zone.network_mask,
        gateway=zone.gateway,
        dns=zone.dns,
        vlan=zone.vlan,
        ip_range_start=zone.ip_range_start,
        ip_range_end=zone.ip_range_end,
        hypervisor_id=zone.hypervisor_id,
        Session=Session
    )
    return {"id": zone_id, "message": "Zone added"}

@app.get("/zones")
def get_zones():
    """Get all zones."""
    zones = repo.get_zones(Session)
    return zones

# ============================================================================
# VM ENDPOINTS
# ============================================================================

@app.get("/virtual-machines")
def get_virtual_machines():
    """
    Get all virtual machines.
    Triggers VM scaffolding if no VMs exist.
    """
    vms = repo.get_virtual_machines(Session)

    if not vms:
        # No VMs yet - trigger scaffolding
        repo.scaffold_architecture(Session)
        vms = repo.get_virtual_machines(Session)

    return vms

# ============================================================================
# DEPLOYMENT ENDPOINTS
# ============================================================================

@app.post("/start", response_model=bool)
def start_deployment(background_tasks: BackgroundTasks):
    """Start deployment (run all Ansible roles) in background."""
    from install import install_all_roles

    try:
        background_tasks.add_task(install_all_roles, Session)
        return True
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/ansible-roles")
def get_ansible_roles():
    """Get status of all Ansible roles."""
    roles = repo.get_ansible_roles(Session)
    return roles

# ... 50+ more endpoints
```

**Key Features:**
- **RESTful API:** Clean endpoint design
- **Input validation:** Pydantic models (from models.py) reject invalid data
- **Response models:** Type-safe API responses
- **Error handling:** Try/catch blocks return HTTP error codes
- **CORS:** Frontend on different origin can call API
- **Background tasks:** Long-running operations don't block API
- **Modular:** All business logic delegated to repository.py

---

### 6.2 Repository Layer (repository.py)

**Purpose:** Business logic and database operations

**Size:** ~3500 lines of Python code

**Key Functions:**

---

**Database Session Management**

```python
def get_session():
    """
    Creates database connection pool.
    Returns: (engine, Session)
    """
    DATABASE_URL = os.getenv(
        "DATABASE_URL",
        "postgresql://harmonisation:harmonisation@postgres:5432/harmonisation"
    )

    engine = create_engine(DATABASE_URL, pool_pre_ping=True)
    Session = sessionmaker(bind=engine)

    return engine, Session
```

**Why:** Single place to configure database connection

---

**Encryption/Decryption (Security)**

```python
def encrypt_password(password: str) -> str:
    """Encrypt password using Fernet symmetric encryption."""
    key = Fernet.generate_key()
    cipher = Fernet(key)
    encrypted = cipher.encrypt(password.encode())
    # Store key + encrypted data together
    return base64.b64encode(key + encrypted).decode()

def decrypt_password(encrypted: str) -> str:
    """Decrypt password."""
    data = base64.b64decode(encrypted.encode())
    key = data[:44]  # First 44 bytes is key
    encrypted_password = data[44:]
    cipher = Fernet(key)
    return cipher.decrypt(encrypted_password).decode()
```

**Why:** Passwords encrypted in database (not plain text)

---

**VMware Configuration Functions**

```python
def add_vmware_esxi_configuration(alias, login, password, api_url,
                                  datacenter_name, cluster_name,
                                  datastore_name, resource_pool_name, Session):
    """Add VMware vSphere configuration to database."""
    if Session is None:
        return None

    session = Session()

    # Encrypt password before storing
    encrypted_password = encrypt_password(password)

    vmware = VMwareESXi(
        alias=alias,
        login=login,
        password=encrypted_password,
        api_url=api_url,
        datacenter_name=datacenter_name,
        cluster_name=cluster_name,
        datastore_name=datastore_name,
        resource_pool_name=resource_pool_name,
        is_connected=False
    )

    session.add(vmware)
    session.commit()
    vmware_id = vmware.id
    session.close()

    return vmware_id

def get_vmware_esxi_configuration(Session):
    """Get VMware configuration from database."""
    if Session is None:
        return None

    session = Session()
    vmware = session.query(VMwareESXi).first()
    session.close()

    return vmware

def update_vmware_esxi_configuration(vmware_id, **kwargs):
    """Update VMware configuration."""
    # ... update logic
    pass

def delete_vmware_esxi_configuration(vmware_id, Session):
    """Delete VMware configuration."""
    # ... delete logic
    pass
```

**Pattern:** CRUD operations for every table

---

**VM Scaffolding (Architecture Generation)**

```python
def scaffold_architecture(Session):
    """
    Generates VM architecture based on:
    - User count (from configurations table)
    - VM configurations (from vm_configurations table)
    - Zones (from zones table)

    This is the BRAIN of the platform!
    """
    if Session is None:
        return

    session = Session()

    # Get configuration
    configuration = getConfiguration(Session)
    security = get_security(Session)
    user_count = configuration.number_concurrent_users

    # Get VM templates for this user count
    vm_configs = get_vm_configurations(user_count, Session)

    # Clear existing VMs
    session.query(VirtualMachine).delete()
    session.query(FlowMatrix).delete()
    session.query(Dns).delete()
    session.commit()

    # Get zones
    zone_lan = get_zone_by_id(id=1, Session=Session)        # LAN_APPS
    zone_infra = get_zone_by_id(id=2, Session=Session)      # LAN_INFRA
    zone_dmz = get_zone_by_id(id=3, Session=Session)        # DMZ

    # Map VM types to zones
    zone_map = {
        "RKEAPPS_CONTROL": zone_lan,
        "RKEAPPS_WORKER": zone_lan,
        "RKEMIDDLEWARE_CONTROL": zone_lan,
        "RKEMIDDLEWARE_WORKER": zone_lan,
        "RKEDMZ": zone_dmz,
        "VAULT": zone_infra,
        "GITOPS": zone_infra,
        "MONITORING": zone_infra,
        "LBLAN": zone_lan,
        "LBDMZ": zone_dmz,
        # ... more mappings
    }

    # Hostname prefixes
    hostname_map = {
        "RKEAPPS_CONTROL": "rkeapp-master",
        "RKEAPPS_WORKER": "rkeapp-worker",
        "VAULT": "vault",
        "GITOPS": "gitops",
        # ... more mappings
    }

    # Group assignments (for Ansible)
    group_map = {
        "RKEAPPS_CONTROL": "RKEAPPS",
        "RKEAPPS_WORKER": "RKEAPPS_WORKER",
        "VAULT": "vault",
        # ... more mappings
    }

    # Environment prefix (e.g., "prod-")
    prefix = "" if security.env_prefix == "" else security.env_prefix + "-"

    # For each VM type in configs
    for vm_type, config in vm_configs.items():
        zone = zone_map.get(vm_type)
        hostname_prefix = hostname_map.get(vm_type)
        group = group_map.get(vm_type)

        if not zone or not hostname_prefix:
            continue  # Skip if no mapping

        # Create N VMs (where N = config.node_count)
        for i in range(1, config.node_count + 1):
            hostname = f"{prefix}{hostname_prefix}{i}"

            # Get next available IP from zone pool
            ip = get_next_available_ip(zone.id, Session)

            # Add VM to database
            add_virtual_machine(
                hostname=hostname,
                ip=ip,
                zone_id=zone.id,
                group=group,
                roles=config.roles,
                nb_cpu=config.cpu_per_node,
                ram=config.ram_per_node,
                os_disk_size=config.os_disk_size,
                data_disk_size=config.data_disk_size,
                Session=Session
            )

    # Add flow matrix rules (firewall rules between zones)
    # Allow INFRA → APPS
    add_flow_matrix_rule(
        source_zone_id=zone_infra.id,
        destination_zone_id=zone_lan.id,
        allowed_ports="22,6443,443",
        Session=Session
    )

    # ... more flow rules

    session.commit()
    session.close()
```

**This function is THE CORE of the platform:**
- Takes user count (e.g., 100 users)
- Queries vm_configurations table for templates
- Calculates how many VMs needed
- Assigns IPs from zones
- Creates VM records in database

---

**IP Address Management**

```python
def get_next_available_ip(zone_id, Session):
    """
    Gets next available IP from zone's pool.

    Example:
    Zone: 10.1.10.0/24
    Pool: 10.1.10.10 - 10.1.10.50

    Returns: 10.1.10.10 (if none used)
             10.1.10.11 (if 10.10 used)
             etc.
    """
    if Session is None:
        return None

    session = Session()

    # Get zone
    zone = session.query(Zone).filter(Zone.id == zone_id).first()
    if not zone:
        return None

    # Get all used IPs in this zone
    used_ips = session.query(VirtualMachine.ip) \
                      .filter(VirtualMachine.zone_id == zone_id) \
                      .all()
    used_ips = [ip[0] for ip in used_ips]

    # Convert IP range to list
    ip_start = ipaddress.IPv4Address(zone.ip_range_start)
    ip_end = ipaddress.IPv4Address(zone.ip_range_end)

    # Find first unused IP
    current_ip = ip_start
    while current_ip <= ip_end:
        if str(current_ip) not in used_ips:
            session.close()
            return str(current_ip)
        current_ip += 1

    # Pool exhausted!
    session.close()
    raise Exception(f"No available IPs in zone {zone.name}")
```

**Why:** Automatic IP assignment (no manual IP planning)

---

### 6.3 Database Models (models.py)

**Purpose:** Define database schema using SQLAlchemy ORM

**Example Model:**

```python
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

# ============================================================================
# VMware Configuration
# ============================================================================

class VMwareESXi(Base):
    __tablename__ = "vmware_esxi"

    id = Column(Integer, primary_key=True, index=True)
    alias = Column(String, nullable=False)                # User-friendly name
    login = Column(String, nullable=False)                # Username
    password = Column(String, nullable=False)             # Encrypted password
    api_url = Column(String, nullable=False)              # vCenter URL
    datacenter_name = Column(String)                      # Datacenter
    cluster_name = Column(String)                         # Cluster
    datastore_name = Column(String)                       # Datastore
    resource_pool_name = Column(String)                   # Resource pool
    is_connected = Column(Boolean, default=False)         # Connection status

    # Relationship: VMware → Zones
    zones = relationship("Zone", back_populates="hypervisor")

# ============================================================================
# Network Zone
# ============================================================================

class Zone(Base):
    __tablename__ = "zones"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)                 # LAN_APPS, LAN_INFRA, DMZ
    sub_network = Column(String, nullable=False)          # 10.1.10.0
    network_mask = Column(String, nullable=False)         # 24
    gateway = Column(String, nullable=False)              # 10.1.10.1
    dns = Column(String, nullable=False)                  # 8.8.8.8
    vlan = Column(String)                                 # VLAN10
    ip_range_start = Column(String, nullable=False)       # 10.1.10.10
    ip_range_end = Column(String, nullable=False)         # 10.1.10.50
    hypervisor_id = Column(Integer, ForeignKey("vmware_esxi.id"))  # FK to VMware

    # Relationships
    hypervisor = relationship("VMwareESXi", back_populates="zones")
    virtual_machines = relationship("VirtualMachine", back_populates="zone")

# ============================================================================
# Virtual Machine
# ============================================================================

class VirtualMachine(Base):
    __tablename__ = "virtual_machines"

    id = Column(Integer, primary_key=True, index=True)
    hostname = Column(String, nullable=False, unique=True)  # vault1, rkeapp-master1
    ip = Column(String, nullable=False, unique=True)        # 10.1.10.10
    zone_id = Column(Integer, ForeignKey("zones.id"))       # Which zone?
    group = Column(String)                                  # Ansible group (vault, RKEAPPS)
    roles = Column(String)                                  # Ansible roles (vault,docker)
    nb_cpu = Column(Integer)                                # CPU count
    ram = Column(Integer)                                   # RAM in MB
    os_disk_size = Column(Integer)                          # OS disk in GB
    data_disk_size = Column(Integer)                        # Data disk in GB

    # Relationship
    zone = relationship("Zone", back_populates="virtual_machines")

# ============================================================================
# VM Configuration Templates
# ============================================================================

class VMConfiguration(Base):
    __tablename__ = "vm_configurations"

    id = Column(Integer, primary_key=True, index=True)
    user_count = Column(Integer, nullable=False)        # 100, 500, 1000, 10000
    vm_type = Column(String, nullable=False)            # RKEAPPS_CONTROL, VAULT, etc.
    node_count = Column(Integer, nullable=False)        # How many VMs to create
    cpu_per_node = Column(Integer, nullable=False)      # CPU per VM
    ram_per_node = Column(Integer, nullable=False)      # RAM per VM (MB)
    os_disk_size = Column(Integer, nullable=False)      # OS disk (GB)
    data_disk_size = Column(Integer, nullable=False)    # Data disk (GB)
    roles = Column(String, nullable=False)              # Ansible roles

# ... 20+ more models
```

**Relationships:**
- VMware → Zones (one-to-many)
- Zone → VMs (one-to-many)
- Configuration → User count (templates)

---

### 6.4 Pydantic Schemas (in models.py)

**Purpose:** API request/response validation

**Important:** Both SQLAlchemy ORM models AND Pydantic validation models are defined in **models.py** (not in a separate schemas.py file).

**Structure of models.py:**
- SQLAlchemy models (inherit from `Base`) - for database tables
- Pydantic models (inherit from `BaseModel`) - for API validation

**Example Pydantic Models:**

```python
from pydantic import BaseModel, Field, validator
from typing import Optional

# ============================================================================
# VMware Pydantic Models (in models.py)
# ============================================================================

class VMwareEsxiModel(BaseModel):
    """Request model for creating VMware configuration."""
    alias: str = Field(..., min_length=1, description="VMware alias")
    login: str = Field(..., description="vCenter username")
    password: str = Field(..., min_length=8, description="vCenter password")
    api_url: str = Field(..., description="vCenter URL")
    datacenter_name: str = Field(..., description="Datacenter name")
    cluster_name: str = Field(..., description="Cluster name")
    datastore_name: str = Field(..., description="Datastore name")
    resource_pool_name: Optional[str] = Field(None, description="Resource pool")

    @validator('api_url')
    def validate_url(cls, v):
        """Ensure URL format is correct."""
        if not v.startswith(('http://', 'https://')):
            raise ValueError('URL must start with http:// or https://')
        return v

    class Config:
        from_attributes = True  # Allow SQLAlchemy models to be converted

# ============================================================================
# Zone Pydantic Models (in models.py)
# ============================================================================

class ZoneModel(BaseModel):
    """Request model for creating zone."""
    name: str = Field(..., description="Zone name")
    sub_network: str = Field(..., description="Network address")
    network_mask: str = Field(..., description="Subnet mask")
    gateway: str = Field(..., description="Gateway IP")
    dns: str = Field(..., description="DNS server IP")
    vlan: Optional[str] = Field(None, description="VLAN name")
    ip_range_start: str = Field(..., description="IP pool start")
    ip_range_end: str = Field(..., description="IP pool end")
    hypervisor_id: int = Field(..., description="Hypervisor ID")

    @validator('sub_network', 'gateway', 'dns', 'ip_range_start', 'ip_range_end')
    def validate_ip(cls, v):
        """Validate IP address format."""
        import ipaddress
        try:
            ipaddress.IPv4Address(v)
            return v
        except:
            raise ValueError(f'{v} is not a valid IP address')

# ... more schemas
```

**Benefits:**
- **Automatic validation:** FastAPI rejects bad data before it reaches your code
- **Clear error messages:** "password must be at least 8 characters" instead of generic errors
- **Type safety:** IDE autocomplete and type checking
- **Self-documenting:** Field descriptions explain what each field does

**Why both ORM and Pydantic models in same file?**
- **Convenience:** All models in one place
- **Code reuse:** Pydantic models can reference ORM models
- **Simpler imports:** `from models import *` gets everything

---

### 6.5 Role Orchestration (install.py)

**Purpose:** Orchestrates the execution of all Ansible roles in the correct sequence

**Flow:**

```python
import sys
import os
import ansible_runner
import importlib
import repository as repo

# Database session
_, Session = repo.get_session()

# Define role sequences
ALL_ROLES = [
    "provisionnement-vms-infra",      # 1. Create infrastructure VMs
    "provisionnement-vms-apps",       # 2. Create apps VMs
    "provisionnement-vms-dmz",        # 3. Create DMZ VMs
    "prepare-vms",                    # 4. Base configuration
    "install-docker-registry",        # 5. Private container registry
    "install-vault",                  # 6. HashiCorp Vault
    "install-gogs",                   # 7. Git server
    "install-haproxy-infra",          # 8. Load balancers (infra)
    "install-rke2-apps",              # 9. Kubernetes cluster (apps)
    "install-rke2-middleware",        # 10. Kubernetes cluster (middleware)
    "install-rke2-dmz",               # 11. Kubernetes cluster (DMZ)
    "install-rancher",                # 12. Rancher management
    "install-argocd",                 # 13. GitOps
    "install-cert-manager",           # 14. TLS certificates
    "install-longhorn",               # 15. Storage
    "setup-vault-injector",           # 16. Vault Kubernetes integration
    "install-minio",                  # 17. Object storage
    "install-keycloak",               # 18. Identity management
    "install-kafka",                  # 19. Event streaming
    "install-n8n",                    # 20. Workflow automation
    "install-gravitee-lan",           # 21. API Gateway (LAN)
    "install-gravitee-dmz",           # 22. API Gateway (DMZ)
    "install-neuvector",              # 23. Security (optional)
    "install-coroot",                 # 24. Monitoring (optional)
]

async def install_all_roles(Session):
    """
    Execute all Ansible roles in sequence.

    For each role:
    1. Load prepare_inputs.py
    2. Call get_inputs(Session) to get vars from database
    3. Execute Ansible role with ansible-runner
    4. Log output to database
    5. Update role status
    6. Run post_install.py if exists
    """

    for role_name in ALL_ROLES:
        print(f"\n{'='*60}")
        print(f"STARTING ROLE: {role_name}")
        print(f"{'='*60}\n")

        # Update status: in_progress
        repo.update_ansible_role_status(role_name, "in_progress", Session)

        try:
            # 1. Import prepare_inputs module
            module_path = f"project.roles.{role_name}.prepare_inputs"
            prepare_module = importlib.import_module(module_path)

            # 2. Get inputs from database
            extra_vars, inventory = prepare_module.get_inputs(Session)

            # 3. Execute role
            result = ansible_runner.run(
                playbook=f"project/roles/{role_name}/tasks/main.yml",
                extravars=extra_vars,
                inventory=inventory,
                verbosity=2
            )

            # 4. Log output
            for event in result.events:
                if 'stdout' in event:
                    repo.add_task_log(
                        role_name=role_name,
                        task_name=event.get('task', 'unknown'),
                        output=event['stdout'],
                        Session=Session
                    )

            # 5. Check result
            if result.status == "successful":
                repo.update_ansible_role_status(
                    role_name,
                    "completed",
                    Session,
                    output=result.stdout.read()
                )

                # 6. Post-install hook
                try:
                    post_module = importlib.import_module(
                        f"project.roles.{role_name}.post_install"
                    )
                    post_module.run(Session)
                except ModuleNotFoundError:
                    # No post_install.py - that's okay
                    pass

            else:
                # Role failed
                repo.update_ansible_role_status(
                    role_name,
                    "failed",
                    Session,
                    output=result.stdout.read()
                )
                raise Exception(f"Role {role_name} failed")

        except Exception as e:
            print(f"ERROR in {role_name}: {str(e)}")
            repo.update_ansible_role_status(
                role_name,
                "failed",
                Session,
                output=str(e)
            )
            raise  # Stop deployment

    print("\n\n🎉 ALL ROLES COMPLETED SUCCESSFULLY!")
```

**Key Features:**
- **Sequential execution:** Roles run in dependency order
- **Database-driven:** All variables come from database
- **Logging:** Every task output saved to database
- **Status tracking:** Frontend can show progress
- **Error handling:** Failed role stops deployment
- **Extensible:** Easy to add new roles

---

## 7. Frontend Architecture

### Angular Application Structure

**Purpose:** Provide a user-friendly wizard for infrastructure configuration

---

### 7.1 Component Overview

```
frontend/src/app/
├── components/
│   ├── hyperviseur/                # Step 1: VMware or Nutanix config
│   ├── reseaux/                    # Step 2: Network zones
│   ├── securite/                   # Step 3: SSL, domain, proxy
│   ├── services/                   # Step 4: LDAP, SMTP, databases
│   ├── palier/                     # Step 5: Number of concurrent users (tier)
│   ├── recapitulatif/              # Step 6: Review generated architecture
│   ├── installation/               # Step 7: Start deployment
│   ├── progression/                # Real-time deployment progress
│   ├── database/                   # Database configuration
│   ├── monitoring/                 # Monitoring configuration
│   ├── gestion-utilisateurs/       # User management
│   ├── historique/                 # Deployment history
│   ├── header/                     # Header component
│   ├── footer/                     # Footer component
│   ├── sidebar/                    # Sidebar navigation
│   ├── stepper/                    # Wizard stepper component
│   └── toast/                      # Toast notifications
│
├── Services/                       # Note: Capital 'S'
│   ├── data-service.service.ts     # HTTP client for backend API
│   └── shared.service.ts           # Shared state and utilities
│
├── Models/                         # Note: Capital 'M' - 40+ model files
│   ├── hypervisor.model.ts
│   ├── vmware-esxi.model.ts
│   ├── nutanix-ahv.model.ts
│   ├── zone.model.ts
│   ├── virtual-machine.model.ts
│   ├── configuration.model.ts
│   ├── security.model.ts
│   ├── database.model.ts
│   ├── ldap.model.ts
│   ├── ansible-role.model.ts
│   ├── task-log.model.ts
│   ├── flow-matrix.model.ts
│   ├── monitoring.model.ts
│   ├── smtp-server.model.ts
│   ├── sms-provider.model.ts
│   └── ... (25+ more model files)
│
└── app.component.ts                # Main application component
```

**Note:** Component names are in French as this is a French organization's codebase.

---

### 7.2 Example Component (Hyperviseur - Hypervisor Configuration)

```typescript
// components/hyperviseur/hyperviseur.component.ts

import { Component, inject, Input, Output, EventEmitter } from '@angular/core';
import { CommonModule } from '@angular/common';
import { DataServiceService } from '../../Services/data-service.service';
import { SharedService } from '../../Services/shared.service';
import { FormBuilder, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';
import { INutanix } from '../../Models/nutanix-ahv.model';
import { IVmware, Vmware } from '../../Models/vmware-esxi.model';
import { NgbModal } from '@ng-bootstrap/ng-bootstrap';
import { ToastComponent } from '../toast/toast.component';

@Component({
  selector: 'app-hyperviseur',
  standalone: true,  // Modern Angular standalone component
  imports: [CommonModule, ReactiveFormsModule, ToastComponent],
  templateUrl: './hyperviseur.component.html',
  styleUrls: ['./hyperviseur.component.css'],
})
export class HyperviseurComponent {
  @Input() currentStep!: number;
  @Input() isReadOnly: boolean = false;
  @Output() stepChange = new EventEmitter<number>();

  // Inject service using modern inject() API
  dataHyperviseurs = inject(DataServiceService);

  hyperviseurs: (IVmware | INutanix)[] = [
    { id: 1, alias: 'VMWare Hypervisor', type: 'VMWare' },
    { id: 2, alias: 'Nutanix Hypervisor', type: 'Nutanix' },
  ];

  isEditing: boolean = false;
  selectedHyperviseur: IVmware | INutanix = this.hyperviseurs[0];
  hyperviseurForm!: FormGroup;
  isLoading: boolean = false;

  // Test connection status
  isVmwareValid: boolean | null = null;
  vmwareErrors: string[] = [];

  // Toast notifications
  isAdd = false;
  isUpdate = false;
  toastMessage = '';
  toastTitle = '';
  showToast = false;

  private initialFormValues = {
    id: 0,
    type: 'VMWare',
    alias: '',
    login: '',
    password: '',
    allow_unverified_ssl: false,
    is_connected: false,
    api_url: '',
    datacenter_name: '',
    datastore_name: '',
    pool_ressource_name: '',
    // ... more fields
  };

  constructor(
    private fb: FormBuilder,
    private modalService: NgbModal,
    // ...
  ) {
    this.initializeForm();
  }

  initializeForm(): void {
    this.hyperviseurForm = this.fb.group({
      type: ['VMWare'],
      alias: ['', Validators.required],
      api_url: ['', [Validators.required, Validators.pattern(/^https?:\/\/.+/)]],
      login: ['', Validators.required],
      password: ['', Validators.required],
      datacenter_name: [''],
      datastore_name: ['', Validators.required],
      // ... more controls
    });
  }

  testVmwareConnection(): void {
    if (this.hyperviseurForm.invalid) {
      this.showToastMessage('Error', 'Please fill all required fields', true);
      return;
    }

    this.isLoading = true;
    this.dataHyperviseurs.testVmwareConnection(this.hyperviseurForm.value).subscribe({
      next: (result) => {
        this.isVmwareValid = result.success;
        this.isLoading = false;
        if (result.success) {
          this.showToastMessage('Success', 'Connection successful!', false);
        } else {
          this.vmwareErrors = result.errors || [];
          this.showToastMessage('Error', 'Connection failed', true);
        }
      },
      error: (err) => {
        this.isVmwareValid = false;
        this.isLoading = false;
        this.showToastMessage('Error', err.message, true);
      }
    });
  }

  saveConfiguration(): void {
    // Save and emit step change
    this.dataHyperviseurs.saveVmware(this.hyperviseurForm.value).subscribe({
      next: () => {
        this.showToastMessage('Success', 'Configuration saved', false);
        this.stepChange.emit(this.currentStep + 1);
      },
      error: (err) => {
        this.showToastMessage('Error', 'Failed to save', true);
      }
    });
  }

  private showToastMessage(title: string, message: string, isError: boolean): void {
    this.toastTitle = title;
    this.toastMessage = message;
    this.showToast = true;
    // Toast auto-hides after 3 seconds
  }
}
```

**Key Differences from Traditional Angular:**
- Uses `standalone: true` (Angular 16+ feature)
- Uses `inject()` function instead of constructor injection
- French component/variable names
- Custom toast notifications instead of alerts
- Event emitters for wizard navigation

---

### 7.3 Data Service (HTTP Client)

```typescript
// Services/data-service.service.ts

import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { Product } from '../Models/product.model';
import { IVmware } from '../Models/vmware-esxi.model';
import { INutanix } from '../Models/nutanix-ahv.model';
import { Database } from '../Models/database.model';
import { IConfiguration } from '../Models/configuration.model';
import { Monitoring } from '../Models/monitoring.model';
import { ILdap } from '../Models/ldap.model';
import { Security } from '../Models/security.model';
import { Zone } from '../Models/zone.model';
import { IVirtualMachine } from '../Models/virtual-machine.model';
import { IAnsibleRole } from '../Models/ansible-role.model';
import { ITaskLog } from '../Models/task-log.model';
import { User } from '../Models/user.model';
// ... 30+ more imports

@Injectable({
  providedIn: 'root',
})
export class DataServiceService {
  private apiUrl = '/runner/api';

  constructor(private http: HttpClient) {}

  // ========================================
  // User Management
  // ========================================

  getUsers(): Observable<User[]> {
    return this.http.get<User[]>(`${this.apiUrl}/get_users`);
  }

  addUser(data: any): Observable<User> {
    return this.http.post<User>(`${this.apiUrl}/add_user`, data);
  }

  deleteUser(id: number): Observable<any> {
    return this.http.delete(`${this.apiUrl}/user/${id}`);
  }

  updateUser(data: any): Observable<User> {
    return this.http.put(`${this.apiUrl}/user`, data);
  }

  // ========================================
  // Hypervisors
  // ========================================

  getVmwareEsxi(): Observable<IVmware> {
    return this.http.get<IVmware>(`${this.apiUrl}/vmware`);
  }

  saveVmware(data: IVmware): Observable<IVmware> {
    return this.http.post<IVmware>(`${this.apiUrl}/vmware`, data);
  }

  testVmwareConnection(data: IVmware): Observable<any> {
    return this.http.post(`${this.apiUrl}/test-vmware-esxi`, data);
  }

  getNutanix(): Observable<INutanix> {
    return this.http.get<INutanix>(`${this.apiUrl}/nutanix`);
  }

  saveNutanix(data: INutanix): Observable<INutanix> {
    return this.http.post<INutanix>(`${this.apiUrl}/nutanix`, data);
  }

  testNutanixConnection(data: INutanix): Observable<any> {
    return this.http.post(`${this.apiUrl}/test-nutanix`, data);
  }

  // ========================================
  // Zones
  // ========================================

  getZones(): Observable<Zone[]> {
    return this.http.get<Zone[]>(`${this.apiUrl}/zones`);
  }

  addZone(data: Zone): Observable<Zone> {
    return this.http.post<Zone>(`${this.apiUrl}/zone`, data);
  }

  updateZone(id: number, data: Zone): Observable<Zone> {
    return this.http.put(`${this.apiUrl}/zone/${id}`, data);
  }

  deleteZone(id: number): Observable<any> {
    return this.http.delete(`${this.apiUrl}/zone/${id}`);
  }

  // ========================================
  // Virtual Machines
  // ========================================

  getVirtualMachines(): Observable<IVirtualMachine[]> {
    return this.http.get<IVirtualMachine[]>(`${this.apiUrl}/virtual-machines`);
  }

  // ========================================
  // Configuration & Security
  // ========================================

  getConfiguration(): Observable<IConfiguration> {
    return this.http.get<IConfiguration>(`${this.apiUrl}/configuration`);
  }

  getSecurity(): Observable<Security> {
    return this.http.get<Security>(`${this.apiUrl}/security`);
  }

  saveSecurity(data: Security): Observable<Security> {
    return this.http.post<Security>(`${this.apiUrl}/security`, data);
  }

  // ========================================
  // Database
  // ========================================

  getDatabases(): Observable<Database[]> {
    return this.http.get<Database[]>(`${this.apiUrl}/databases`);
  }

  addDatabaseItem(data: Database): Observable<Database> {
    return this.http.post<Database>(`${this.apiUrl}/database`, data);
  }

  testDatabase(data: Database): Observable<any> {
    return this.http.post(`${this.apiUrl}/test-database`, data);
  }

  // ========================================
  // LDAP
  // ========================================

  getLdap(): Observable<ILdap> {
    return this.http.get<ILdap>(`${this.apiUrl}/ldap`);
  }

  saveLdap(data: ILdap): Observable<ILdap> {
    return this.http.post<ILdap>(`${this.apiUrl}/ldap`, data);
  }

  testLdap(data: ILdap): Observable<any> {
    return this.http.post(`${this.apiUrl}/test-ldap`, data);
  }

  // ========================================
  // Deployment & Ansible
  // ========================================

  startInstallation(): Observable<any> {
    return this.http.post(`${this.apiUrl}/start-install`, {});
  }

  getAnsibleRoles(): Observable<IAnsibleRole[]> {
    return this.http.get<IAnsibleRole[]>(`${this.apiUrl}/ansible-roles`);
  }

  getTaskLogs(): Observable<ITaskLog[]> {
    return this.http.get<ITaskLog[]>(`${this.apiUrl}/task-logs`);
  }

  // ========================================
  // Monitoring
  // ========================================

  getMonitoring(): Observable<Monitoring> {
    return this.http.get<Monitoring>(`${this.apiUrl}/monitoring`);
  }

  saveMonitoring(data: Monitoring): Observable<Monitoring> {
    return this.http.post<Monitoring>(`${this.apiUrl}/monitoring`, data);
  }

  // ... 50+ more methods for other entities
}
```

**Note:** The service is named `DataServiceService` (double "Service") and contains 100+ methods for all backend API endpoints.

---

### 7.4 Shared Service (State Management)

```typescript
// Services/shared.service.ts

import { Injectable } from '@angular/core';
import { BehaviorSubject, Subject } from 'rxjs';
import { DataServiceService } from './data-service.service';
import { IGlobalRecap } from '../Models/global-recap.model';

@Injectable({
  providedIn: 'root',
})
export class SharedService {
  // State management using RxJS
  private installationStart = new BehaviorSubject<boolean>(false);
  private runnerIdent = new BehaviorSubject<string | null>(null);
  private stepName = new BehaviorSubject<string | null>(null);
  private globalRecapSubject = new BehaviorSubject<IGlobalRecap[]>([]);
  private dnsInserted = new Subject<void>();
  private FlowsInserted = new Subject<void>();

  constructor(private dataService: DataServiceService) {}

  // ========================================
  // Installation Status
  // ========================================

  getInstallationStart$() {
    return this.installationStart.asObservable();
  }

  notifyInstallationStart(): void {
    this.installationStart.next(true);
  }

  // ========================================
  // Runner Identifier (Ansible run ID)
  // ========================================

  getRunnerIdent$() {
    return this.runnerIdent.asObservable();
  }

  notifyRunnerIdent(runnerIdent: string): void {
    this.runnerIdent.next(runnerIdent);
  }

  // ========================================
  // Current Step Name
  // ========================================

  getStepName$() {
    return this.stepName.asObservable();
  }

  notifyStepName(stepName: string): void {
    this.stepName.next(stepName);
  }

  // ========================================
  // Global Recap (Configuration Summary)
  // ========================================

  getGlobalRecap$() {
    return this.globalRecapSubject.asObservable();
  }

  notifyGlobalRecap(data: IGlobalRecap[]): void {
    this.globalRecapSubject.next(data);
  }

  // ========================================
  // DNS and Flow Matrix Notifications
  // ========================================

  getDnsInserted$() {
    return this.dnsInserted.asObservable();
  }

  notifyDnsInserted$() {
    this.dnsInserted.next();
  }

  getFlowsInserted$() {
    return this.FlowsInserted.asObservable();
  }

  notifyFlowsInserted$() {
    this.FlowsInserted.next();
  }

  // ========================================
  // Utility Functions
  // ========================================

  isValidIP(ip: string): boolean {
    const ipRegex = new RegExp(
      '^((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\\.){3}(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$'
    );
    return ipRegex.test(ip);
  }
}
```

**Purpose:** This service provides centralized state management across components using RxJS observables. Components can subscribe to state changes and notify other components of events.

**Note:** The application uses **HTTP polling** (periodic GET requests to `/runner/api/ansible-roles` and `/runner/api/task-logs`) for real-time updates during deployment, NOT WebSockets.

---

### 7.5 User Flow

```
User opens: http://localhost/runner/

┌─────────────────────────────────────────────────────────┐
│ Step 1: Choose Hypervisor                               │
│                                                          │
│ ○ VMware vSphere    ○ Nutanix AHV                      │
│                                                          │
│ vCenter URL: [https://vcenter.example.com  ]           │
│ Username:    [administrator@vsphere.local  ]           │
│ Password:    [********************         ]           │
│ Datacenter:  [DC1                          ]           │
│ Cluster:     [Cluster01                    ]           │
│ Datastore:   [Datastore01                  ]           │
│                                                          │
│          [ Test Connection ]  [ Next → ]                │
└─────────────────────────────────────────────────────────┘

↓

┌─────────────────────────────────────────────────────────┐
│ Step 2: Configure Network Zones                         │
│                                                          │
│ ┌─── Zone: LAN_APPS ──────────────────────────────┐   │
│ │ Network: 10.1.10.0/24                            │   │
│ │ Gateway: 10.1.10.1                               │   │
│ │ VLAN:    VLAN10                                  │   │
│ │ IP Pool: 10.1.10.10 - 10.1.10.50                │   │
│ └──────────────────────────────────────────────────┘   │
│                                                          │
│ ┌─── Zone: LAN_INFRA ─────────────────────────────┐   │
│ │ Network: 10.1.20.0/24                            │   │
│ │ ...                                              │   │
│ └──────────────────────────────────────────────────┘   │
│                                                          │
│          [ ← Back ]  [ Add Zone ]  [ Next → ]          │
└─────────────────────────────────────────────────────────┘

↓

┌─────────────────────────────────────────────────────────┐
│ Step 5: Number of Concurrent Users                      │
│                                                          │
│ How many concurrent users will this platform support?   │
│                                                          │
│ ○ 100 users                                             │
│ ○ 500 users                                             │
│ ○ 1000 users                                            │
│ ● 5000 users                                            │
│ ○ 10000 users                                           │
│                                                          │
│          [ ← Back ]  [ Next → ]                         │
└─────────────────────────────────────────────────────────┘

↓

┌─────────────────────────────────────────────────────────┐
│ Step 6: Review Architecture                             │
│                                                          │
│ Based on 5000 users, we will create:                   │
│                                                          │
│ LAN_APPS Zone:                                          │
│   • 3x RKE2-APPS Control Nodes (8 CPU, 16 GB RAM)      │
│   • 10x RKE2-APPS Worker Nodes (16 CPU, 32 GB RAM)     │
│   • 3x RKE2-MIDDLEWARE Control (8 CPU, 16 GB RAM)      │
│   • 5x RKE2-MIDDLEWARE Worker (12 CPU, 24 GB RAM)      │
│                                                          │
│ LAN_INFRA Zone:                                         │
│   • 2x Vault (4 CPU, 8 GB RAM)                         │
│   • 1x GitOps (4 CPU, 8 GB RAM)                        │
│   • 1x Monitoring (8 CPU, 16 GB RAM)                   │
│   • 2x HAProxy (4 CPU, 8 GB RAM)                       │
│                                                          │
│ DMZ Zone:                                               │
│   • 3x RKE2-DMZ Nodes (8 CPU, 16 GB RAM)               │
│   • 2x Load Balancers (4 CPU, 8 GB RAM)                │
│                                                          │
│ Total: 31 VMs, 264 vCPUs, 528 GB RAM                   │
│                                                          │
│          [ ← Back ]  [ Modify ]  [ Next → ]            │
└─────────────────────────────────────────────────────────┘

↓

┌─────────────────────────────────────────────────────────┐
│ Step 7: Start Deployment                                │
│                                                          │
│ Ready to deploy infrastructure!                         │
│                                                          │
│ Estimated time: 4-6 hours                               │
│                                                          │
│ This will:                                              │
│ ✓ Provision 31 virtual machines                        │
│ ✓ Configure 3 Kubernetes clusters (RKE2)               │
│ ✓ Install middleware (Kafka, Keycloak, MinIO)          │
│ ✓ Deploy API gateways (Gravitee)                       │
│ ✓ Configure security (NeuVector)                       │
│ ✓ Setup monitoring (Coroot)                            │
│                                                          │
│          [ ← Back ]  [ 🚀 START DEPLOYMENT ]           │
└─────────────────────────────────────────────────────────┘

↓

┌─────────────────────────────────────────────────────────┐
│ Deployment in Progress...                               │
│                                                          │
│ ✓ provisionnement-vms-infra      [COMPLETED] 15 min    │
│ ✓ provisionnement-vms-apps       [COMPLETED] 25 min    │
│ ✓ provisionnement-vms-dmz        [COMPLETED] 10 min    │
│ ✓ prepare-vms                    [COMPLETED] 12 min    │
│ ✓ install-docker-registry        [COMPLETED] 8 min     │
│ ✓ install-vault                  [COMPLETED] 10 min    │
│ ⏳ install-rke2-apps              [IN PROGRESS] 35%     │
│   └─ Installing RKE2 on rkeapp-master1...              │
│ ⏸ install-rke2-middleware        [PENDING]             │
│ ⏸ install-argocd                 [PENDING]             │
│ ⏸ install-cert-manager           [PENDING]             │
│ ... (15 more roles)                                     │
│                                                          │
│ Overall Progress: [████████░░░░░░░░░] 42%              │
│                                                          │
│          [ View Logs ]  [ Cancel Deployment ]          │
└─────────────────────────────────────────────────────────┘
```

---

## 8. Database Schema (Every Table)

### Complete Database Structure

---

### 8.1 Hypervisor Tables

**VMware ESXi Configuration**

```sql
CREATE TABLE vmware_esxi (
    id SERIAL PRIMARY KEY,
    alias VARCHAR(255) NOT NULL,                  -- User-friendly name
    login VARCHAR(255) NOT NULL,                  -- vCenter username
    password VARCHAR(255) NOT NULL,               -- Encrypted password
    api_url VARCHAR(255) NOT NULL,                -- vCenter URL (https://vcenter.example.com)
    api_timeout INTEGER NOT NULL,                 -- API timeout in seconds
    allow_unverified_ssl BOOLEAN NOT NULL,        -- Allow self-signed certificates
    datacenter_name VARCHAR(255) NOT NULL,        -- Datacenter name
    datacenter_id VARCHAR(255) NOT NULL,          -- Datacenter MoID
    target_name VARCHAR(255) NOT NULL,            -- Host/Cluster name
    target_id VARCHAR(255) NOT NULL,              -- Target MoID
    target_type VARCHAR(255) NOT NULL,            -- 'host' or 'cluster'
    datastore_name VARCHAR(255) NOT NULL,         -- Datastore name
    datastore_id VARCHAR(255) NOT NULL,           -- Datastore MoID
    pool_ressource_name VARCHAR(255),             -- Resource pool name (optional)
    pool_ressource_id VARCHAR(255),               -- Resource pool MoID (optional)
    is_connected BOOLEAN DEFAULT FALSE,           -- Connection test result
    configuration_id INTEGER REFERENCES configurations(id)
);
```

**Nutanix AHV Configuration**

```sql
CREATE TABLE nutanix_ahv (
    id SERIAL PRIMARY KEY,
    alias VARCHAR(255) NOT NULL,                  -- User-friendly name
    login VARCHAR(255) NOT NULL,                  -- Prism username
    password VARCHAR(255) NOT NULL,               -- Encrypted password
    host VARCHAR(255) NOT NULL,                   -- Prism host/IP
    port INTEGER NOT NULL,                        -- Prism port (typically 9440)
    allow_unverified_ssl BOOLEAN NOT NULL,        -- Allow self-signed certificates
    is_connected BOOLEAN DEFAULT FALSE,           -- Connection test result
    configuration_id INTEGER REFERENCES configurations(id) NOT NULL
);
```

---

### 8.2 Network Tables

**Zones (Network Segments)**

```sql
CREATE TABLE zones (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,                   -- LAN_APPS, LAN_INFRA, DMZ
    sub_network VARCHAR(50) NOT NULL,             -- 10.1.10.0
    network_mask INTEGER NOT NULL,                -- 24 (CIDR notation)
    gateway VARCHAR(50) NOT NULL,                 -- 10.1.10.1
    dns VARCHAR(255) NOT NULL,                    -- 8.8.8.8,8.8.4.4
    domain VARCHAR(255) DEFAULT 'local',          -- Domain name
    vlan_name VARCHAR(50) NOT NULL,               -- VLAN10
    ip_pool_start VARCHAR(50) NOT NULL,           -- 10.1.10.10
    ip_pool_end VARCHAR(50) NOT NULL,             -- 10.1.10.50
    hypervisor_type VARCHAR(20) NOT NULL,         -- 'vmware' or 'nutanix'
    vmware_id INTEGER REFERENCES vmware_esxi(id), -- FK to vmware_esxi (if VMware)
    nutanix_id INTEGER REFERENCES nutanix_ahv(id) -- FK to nutanix_ahv (if Nutanix)
);
```

**Flow Matrix (Firewall Rules)**

```sql
CREATE TABLE flow_matrix (
    id SERIAL PRIMARY KEY,
    source_zone_id INTEGER REFERENCES zones(id),
    destination_zone_id INTEGER REFERENCES zones(id),
    protocol VARCHAR(20) DEFAULT 'TCP',           -- TCP, UDP, ICMP, ALL
    ports TEXT,                                   -- '22,80,443' or '1-65535'
    description TEXT,
    is_enabled BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

### 8.3 Virtual Machine Tables

**Virtual Machines**

```sql
CREATE TABLE virtual_machines (
    id SERIAL PRIMARY KEY,
    hostname VARCHAR(255) NOT NULL,               -- vault1, rkeapp-master1
    ip VARCHAR(50) NOT NULL,                      -- 10.1.10.10
    zone_id INTEGER REFERENCES zones(id) NOT NULL,
    group VARCHAR(100) NOT NULL,                  -- Ansible inventory group
    roles VARCHAR(255) NOT NULL,                  -- Comma-separated roles
    nb_cpu INTEGER NOT NULL,                      -- CPU count
    ram INTEGER NOT NULL,                         -- RAM in MB
    os_disk_size INTEGER NOT NULL,                -- OS disk in GB
    data_disk_size INTEGER DEFAULT 0,             -- Data disk in GB
    status VARCHAR(50) DEFAULT 'to_create'        -- to_create, creating, created, failed
);
```

**VM Configuration Templates**

```sql
CREATE TABLE vm_configurations (
    id SERIAL PRIMARY KEY,
    user_count INTEGER NOT NULL,                  -- 100, 500, 1000, 5000, 10000
    vm_type VARCHAR(100) NOT NULL,                -- RKEAPPS_CONTROL, VAULT, etc.
    node_count INTEGER NOT NULL,                  -- Number of VMs to create
    cpu_per_node INTEGER NOT NULL,                -- CPU per VM
    ram_per_node INTEGER NOT NULL,                -- RAM per VM (MB)
    os_disk_size INTEGER NOT NULL,                -- OS disk (GB)
    data_disk_size INTEGER NOT NULL,              -- Data disk (GB)
    roles TEXT NOT NULL,                          -- Ansible roles to assign
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_count, vm_type)                   -- One config per user_count + vm_type
);
```

**Example Data:**

```sql
INSERT INTO vm_configurations VALUES
(1, 100, 'RKEAPPS_CONTROL', 3, 4, 8192, 100, 200, 'docker,rke2-server', 'RKE2 control plane'),
(2, 100, 'RKEAPPS_WORKER', 3, 8, 16384, 100, 500, 'docker,rke2-agent', 'RKE2 worker nodes'),
(3, 500, 'RKEAPPS_CONTROL', 3, 8, 16384, 100, 200, 'docker,rke2-server', 'RKE2 control plane'),
(4, 500, 'RKEAPPS_WORKER', 10, 16, 32768, 100, 1000, 'docker,rke2-agent', 'RKE2 worker nodes'),
(5, 1000, 'RKEAPPS_CONTROL', 3, 8, 16384, 100, 200, 'docker,rke2-server', 'RKE2 control plane'),
(6, 1000, 'RKEAPPS_WORKER', 20, 16, 32768, 100, 1000, 'docker,rke2-agent', 'RKE2 worker nodes');
```

---

### 8.4 Security & Configuration Tables

**Security Configuration**

```sql
CREATE TABLE security (
    id SERIAL PRIMARY KEY,
    use_proxy BOOLEAN DEFAULT FALSE,              -- Enable proxy usage
    porxy_host VARCHAR(255),                      -- Proxy host (typo in actual code!)
    proxy_port VARCHAR(50),                       -- Proxy port
    proxy_login VARCHAR(255) DEFAULT '',          -- Proxy username
    proxy_password VARCHAR(255) DEFAULT '',       -- Proxy password (encrypted)
    ssh_pulic_key TEXT NOT NULL,                  -- SSH public key (typo in actual code!)
    ssh_private_key TEXT NOT NULL,                -- SSH private key
    ssh_private_key_pwd VARCHAR(255) DEFAULT '',  -- SSH key password
    base_domain VARCHAR(255) NOT NULL,            -- platform.example.com
    env_prefix VARCHAR(50) NOT NULL,              -- Environment prefix (prod-, dev-, etc.)
    pem_certificate TEXT NOT NULL,                -- SSL certificate + private key (PEM)
    configuration_id INTEGER REFERENCES configurations(id)
);
```

**Note:** The actual code contains typos: `porxy_host` and `ssh_pulic_key` instead of correct spellings.

**LDAP Configuration**

```sql
CREATE TABLE ldaps (
    id SERIAL PRIMARY KEY,
    ldap_type VARCHAR(50) NOT NULL,               -- 'internal_users' or 'external_users'
    ldap_url VARCHAR(255) NOT NULL,               -- ldap://ldap.example.com
    ldap_port VARCHAR(10) NOT NULL,               -- 389 or 636
    bind_dn VARCHAR(255),                         -- CN=admin,DC=example,DC=com
    bind_credentials VARCHAR(255) NOT NULL,       -- Encrypted bind password
    user_dn VARCHAR(255),                         -- OU=Users,DC=example,DC=com
    user_ldap_attributes VARCHAR(255),            -- Comma-separated attributes
    search_scope VARCHAR(50),                     -- SUBTREE, ONELEVEL, BASE
    configuration_id INTEGER REFERENCES configurations(id) NOT NULL
);
```

**SMTP Configuration**

```sql
CREATE TABLE smtp_servers (
    id SERIAL PRIMARY KEY,
    host VARCHAR(255) NOT NULL,                   -- smtp.gmail.com
    port INTEGER NOT NULL,                        -- 587
    login VARCHAR(255),                           -- SMTP username (optional)
    password VARCHAR(255),                        -- Encrypted SMTP password
    mail_from VARCHAR(255) NOT NULL,              -- From email address
    use_tls_ssl BOOLEAN NOT NULL,                 -- Use TLS/SSL
    configuration_id INTEGER REFERENCES configurations(id)
);
```

**External Databases**

```sql
CREATE TABLE database (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,                   -- Database name
    type VARCHAR(50) NOT NULL,                    -- postgresql, informix, mysql, mssql
    alias VARCHAR(100) NOT NULL,                  -- User-friendly alias
    host VARCHAR(255) NOT NULL,                   -- Database host/IP
    servername VARCHAR(255),                      -- Server name (for Informix)
    port INTEGER NOT NULL,                        -- Database port
    login VARCHAR(255) NOT NULL,                  -- Database username
    password VARCHAR(255) NOT NULL,               -- Encrypted password
    is_connected BOOLEAN DEFAULT FALSE,           -- Connection test result
    configuration_id INTEGER REFERENCES configurations(id) NOT NULL
);
```

---

### 8.5 Deployment Tracking Tables

**Ansible Roles**

```sql
CREATE TABLE ansible_roles (
    id SERIAL PRIMARY KEY,
    role_name VARCHAR(255) NOT NULL,              -- install-vault, install-rke2-apps
    order INTEGER NOT NULL,                       -- Execution order
    runner_ident VARCHAR(255) UNIQUE,             -- Ansible Runner UUID
    status VARCHAR(50) NOT NULL,                  -- pending, running, successful, failed
    start_time TIMESTAMP NOT NULL,                -- Role start time
    end_time TIMESTAMP                            -- Role end time (NULL if still running)
);
```

**Task Logs**

```sql
CREATE TABLE task_logs (
    id SERIAL PRIMARY KEY,
    event VARCHAR(255) NOT NULL,                  -- Event type (runner_on_ok, runner_on_failed, etc.)
    task VARCHAR(255) NOT NULL,                   -- Ansible task name
    stdout TEXT,                                  -- Task output
    runner_ident VARCHAR(255) REFERENCES ansible_roles(runner_ident) -- FK to ansible_roles
);
```

---

### 8.6 Vault & Secrets Tables

**Vault Credentials**

```sql
CREATE TABLE vault_credentials (
    id SERIAL PRIMARY KEY,
    type VARCHAR(255) NOT NULL,                   -- Credential type (e.g., 'root_token', 'unseal_key_1')
    value VARCHAR(255) NOT NULL                   -- Credential value (encrypted)
);
```

**Note:** This is a key-value table. Multiple rows store different vault credentials. Example:
- Row 1: type='root_token', value='encrypted_token'
- Row 2: type='unseal_key_1', value='encrypted_key_1'
- Row 3: type='unseal_key_2', value='encrypted_key_2'

---

### 8.7 Application Configuration Tables

**Global Configuration**

```sql
CREATE TABLE configurations (
    id SERIAL PRIMARY KEY,
    number_concurrent_users INTEGER NOT NULL      -- 100, 500, 1000, 5000, 10000
);
```

**Note:** This table has only one field. All other configuration details are stored in related tables (security, vmware_esxi, nutanix_ahv, ldaps, smtp_servers, database, etc.) via foreign key relationships.

**Rancher Configuration**

```sql
CREATE TABLE rancher_config (
    id SERIAL PRIMARY KEY,
    rancher_url VARCHAR(255),                     -- https://rancher.example.com
    admin_password TEXT,                          -- Encrypted password
    api_token TEXT,                               -- Encrypted API token
    cluster_apps_id VARCHAR(255),                 -- Rancher cluster ID
    cluster_middleware_id VARCHAR(255),
    cluster_dmz_id VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

## 9. Ansible Automation (How Deployment Works)

### Complete Ansible Integration

The platform uses **32 Ansible roles** located in `backend/project/roles/` to orchestrate infrastructure deployment. However, only **23 roles** are actively used in the main deployment sequence defined in `install.py`.

**Roles in Main Deployment Sequence (23 total):**
- **3 VM Provisioning Roles**: provisionnement-vms-infra, provisionnement-vms-apps, provisionnement-vms-dmz
- **9 Infrastructure Roles**: prepare-vms, install-docker-registry, install-vault, install-load-balancer, install-rke2-apps, install-rke2-middleware, install-rke2-dmz, install-gogs, install-rancher-server
- **11 Kubernetes Application Roles**: install-argocd, install-cert-manager, install-longhorn, setup-vault-injector, install-minio-backup, install-minio, install-keycloak, install-kafka, install-n8n, install-gravitee-lan, install-gravitee-dmz
- **2 Optional Monitoring Roles**: install-monitoring, install-neuvector (added dynamically if monitoring is enabled)

**Additional Roles (Not in Main Sequence):**
- install-bastion, install-informix, install-seald (special-purpose roles)
- testrole, testrolefailed (test/development roles)

---

### 9.1 Ansible Role Structure

**Every role follows this structure:**

```
backend/project/roles/install-vault/
├── prepare_inputs.py          # Loads variables from database
├── post_install.py            # Optional post-execution tasks
├── tasks/
│   └── main.yml               # Ansible tasks
├── templates/
│   ├── vault-config.hcl.j2    # Jinja2 templates
│   └── vault.service.j2
├── files/
│   └── vault-binary           # Static files
└── requirements.txt           # Python dependencies (if needed)
```

---

### 9.2 Example: install-vault Role

**prepare_inputs.py** (Loads data from database)

```python
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../../../'))
import repository as repo

def get_inputs(Session):
    """
    Query database and return (extra_vars, inventory) for Ansible.

    Returns:
        extra_vars: dict - Variables passed to Ansible
        inventory: dict - Ansible inventory (hosts, groups)
    """

    # Get Vault VMs from database
    vault_vms = repo.get_virtual_machines_by_group('vault', Session)

    # Get security config
    security = repo.get_security(Session)

    # Build extra_vars
    extra_vars = {
        'vault_version': '1.15.0',
        'vault_download_url': 'https://releases.hashicorp.com/vault/1.15.0/vault_1.15.0_linux_amd64.zip',
        'vault_config_dir': '/etc/vault',
        'vault_data_dir': '/opt/vault/data',
        'vault_cluster_name': 'vault-cluster',
        'domain_name': security.domain_name,
        'vault_nodes': []
    }

    # Build vault_nodes list
    for vm in vault_vms:
        extra_vars['vault_nodes'].append({
            'hostname': vm.hostname,
            'ip': vm.ip,
            'node_id': vm.hostname  # vault1, vault2
        })

    # Build inventory
    inventory = {
        'vault': {
            'hosts': {}
        }
    }

    for vm in vault_vms:
        inventory['vault']['hosts'][vm.hostname] = {
            'ansible_host': vm.ip,
            'ansible_user': 'root',
            'ansible_ssh_private_key_file': '/home/devops/.ssh/id_rsa'
        }

    return extra_vars, inventory
```

**tasks/main.yml** (Ansible playbook)

```yaml
---
- name: Install Vault
  hosts: vault
  become: yes

  tasks:
    - name: Download Vault binary
      get_url:
        url: "{{ vault_download_url }}"
        dest: /tmp/vault.zip
        mode: '0644'

    - name: Unzip Vault binary
      unarchive:
        src: /tmp/vault.zip
        dest: /usr/local/bin
        remote_src: yes
        mode: '0755'

    - name: Create Vault system user
      user:
        name: vault
        system: yes
        shell: /bin/false

    - name: Create Vault directories
      file:
        path: "{{ item }}"
        state: directory
        owner: vault
        group: vault
        mode: '0750'
      loop:
        - "{{ vault_config_dir }}"
        - "{{ vault_data_dir }}"

    - name: Generate Vault configuration
      template:
        src: vault-config.hcl.j2
        dest: "{{ vault_config_dir }}/vault.hcl"
        owner: vault
        group: vault
        mode: '0640'

    - name: Create Vault systemd service
      template:
        src: vault.service.j2
        dest: /etc/systemd/system/vault.service
        mode: '0644'

    - name: Start and enable Vault service
      systemd:
        name: vault
        state: started
        enabled: yes
        daemon_reload: yes

    - name: Wait for Vault to be ready
      wait_for:
        port: 8200
        delay: 5
        timeout: 60

    - name: Initialize Vault (run on first node only)
      shell: vault operator init -key-shares=5 -key-threshold=3 -format=json
      environment:
        VAULT_ADDR: "http://127.0.0.1:8200"
      register: vault_init_output
      run_once: true
      delegate_to: "{{ vault_nodes[0].hostname }}"
      when: inventory_hostname == vault_nodes[0].hostname

    - name: Save Vault keys to file
      copy:
        content: "{{ vault_init_output.stdout }}"
        dest: /tmp/vault-keys.json
      delegate_to: localhost
      run_once: true
      when: vault_init_output.changed

    - name: Parse Vault unseal keys and root token
      set_fact:
        vault_unseal_keys: "{{ (vault_init_output.stdout | from_json).unseal_keys_b64 }}"
        vault_root_token: "{{ (vault_init_output.stdout | from_json).root_token }}"
      run_once: true
      when: vault_init_output.changed

    - name: Unseal Vault (all nodes)
      shell: |
        vault operator unseal {{ vault_unseal_keys[0] }}
        vault operator unseal {{ vault_unseal_keys[1] }}
        vault operator unseal {{ vault_unseal_keys[2] }}
      environment:
        VAULT_ADDR: "http://127.0.0.1:8200"
      when: vault_unseal_keys is defined
```

**templates/vault-config.hcl.j2** (Jinja2 template)

```hcl
# Vault Configuration for {{ inventory_hostname }}

listener "tcp" {
  address     = "0.0.0.0:8200"
  tls_disable = 0

  tls_cert_file = "/etc/vault/tls/vault.crt"
  tls_key_file  = "/etc/vault/tls/vault.key"
}

storage "raft" {
  path    = "{{ vault_data_dir }}"
  node_id = "{{ inventory_hostname }}"

  {% for node in vault_nodes %}
  {% if node.hostname != inventory_hostname %}
  retry_join {
    leader_api_addr = "https://{{ node.ip }}:8200"
  }
  {% endif %}
  {% endfor %}
}

cluster_addr  = "https://{{ ansible_host }}:8201"
api_addr      = "https://{{ ansible_host }}:8200"
ui            = true
disable_mlock = false
```

**post_install.py** (Save credentials to database)

```python
import sys
import os
import json
sys.path.append(os.path.join(os.path.dirname(__file__), '../../../'))
import repository as repo

def run(Session):
    """
    Post-installation tasks:
    - Save Vault credentials to database
    - Mark Vault as unsealed
    """

    # Read vault keys from file
    with open('/tmp/vault-keys.json', 'r') as f:
        vault_data = json.load(f)

    # Save to database
    repo.save_vault_credentials(
        vault_url='https://vault1.example.com:8200',
        root_token=vault_data['root_token'],
        unseal_keys=vault_data['unseal_keys_b64'],
        Session=Session
    )

    # Cleanup sensitive file
    os.remove('/tmp/vault-keys.json')

    print("✓ Vault credentials saved to database")
```

---

### 9.3 Dynamic Inventory Generation

**Example: RKE2 Apps Cluster Inventory**

```python
# From install-rke2-apps/prepare_inputs.py

def get_inputs(Session):
    """Generate inventory for RKE2 Apps cluster."""

    # Get VMs
    master_vms = repo.get_virtual_machines_by_group('RKEAPPS_CONTROL', Session)
    worker_vms = repo.get_virtual_machines_by_group('RKEAPPS_WORKER', Session)

    # Get registry info
    registry = repo.get_registry_config(Session)

    extra_vars = {
        'rke2_version': 'v1.31.1+rke2r2',
        'cluster_name': 'rke2-apps',
        'registry_url': f"{registry.ip}:5000",
        'cluster_cidr': '10.42.0.0/16',
        'service_cidr': '10.43.0.0/16',
        'cluster_dns': '10.43.0.10'
    }

    inventory = {
        'all': {
            'children': {
                'masters': {
                    'hosts': {}
                },
                'workers': {
                    'hosts': {}
                }
            }
        }
    }

    # Add masters
    for vm in master_vms:
        inventory['all']['children']['masters']['hosts'][vm.hostname] = {
            'ansible_host': vm.ip,
            'node_ip': vm.ip,
            'node_name': vm.hostname
        }

    # Add workers
    for vm in worker_vms:
        inventory['all']['children']['workers']['hosts'][vm.hostname] = {
            'ansible_host': vm.ip,
            'node_ip': vm.ip,
            'node_name': vm.hostname
        }

    return extra_vars, inventory
```

**Generated Inventory (YAML format):**

```yaml
all:
  children:
    masters:
      hosts:
        rkeapp-master1:
          ansible_host: 10.1.10.10
          node_ip: 10.1.10.10
          node_name: rkeapp-master1
        rkeapp-master2:
          ansible_host: 10.1.10.11
          node_ip: 10.1.10.11
          node_name: rkeapp-master2
        rkeapp-master3:
          ansible_host: 10.1.10.12
          node_ip: 10.1.10.12
          node_name: rkeapp-master3
    workers:
      hosts:
        rkeapp-worker1:
          ansible_host: 10.1.10.20
          node_ip: 10.1.10.20
          node_name: rkeapp-worker1
        rkeapp-worker2:
          ansible_host: 10.1.10.21
          node_ip: 10.1.10.21
          node_name: rkeapp-worker2
        # ... more workers
```

---

## 10. Docker & Containerization

### Docker Compose Setup

**docker-compose.yml** (Main orchestration)

```yaml
services:
  # ========================================
  # Nginx (Reverse Proxy)
  # ========================================
  nginx:
    image: nginx:latest
    container_name: nginx
    restart: unless-stopped
    networks:
      - proxy
      - internal
    ports:
      - 80:80
    volumes:
      - ./nginx/custom.conf:/etc/nginx/conf.d/default.conf:ro
    depends_on:
      - corteza
      - frontend
      - backend
      - postgres

  # ========================================
  # Corteza (Low-code platform)
  # ========================================
  corteza:
    build:
      context: ./corteza
      dockerfile: Dockerfile
    container_name: corteza
    image: corteza-harmonisation:latest
    restart: unless-stopped
    environment:
      PROVISION_ENABLED: "false"
      HTTP_WEBAPP_ENABLED: "true"
      ACTIONLOG_ENABLED: "false"
      HTTP_ADDR: ":80"
      DB_DSN: "postgres://harmonisation:harmonisation@postgres:5432/harmonisation?sslmode=disable"
      LOCALE_LANGUAGES: "fr,en"
      LOCALE_PATH: "/corteza/locale"
      LOCALE_RESOURCE_TRANSLATIONS_ENABLED: "true"
      LOCALE_DEVELOPMENT_MODE: "true"
      LOCALE_LOG: "true"
      PROVISION_ALWAYS: "false"
      UPGRADE_ALWAYS: "false"
      UPGRADE_DEBUG: "false"
    volumes:
      - ./server:/data
      - ./odbc/odbcinst.ini:/etc/odbcinst.ini
      - ./odbc/odbc.ini:/root/.odbc.ini
      - ./odbc/sqlhosts:/root/odbc/etc/sqlhosts
    networks:
      - internal
    depends_on:
      postgres:
        condition: service_healthy

  # ========================================
  # Frontend (Angular)
  # ========================================
  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    container_name: frontend
    image: frontend-harmonisation:latest
    restart: unless-stopped
    networks:
      - internal

  # ========================================
  # Backend (FastAPI + Ansible)
  # ========================================
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    container_name: backend
    image: backend-harmonisation:latest
    mem_limit: 4g
    cpu_shares: 1024
    restart: unless-stopped
    environment:
      DATABASE_URL: "postgresql://harmonisation:harmonisation@postgres:5432/harmonisation"
    volumes:
      - ./data/.ssh/:/home/devops/.ssh/
      - ./data/db:/home/devops/db
      - ./data/.kube:/home/devops/.kube
      - ./data/inventory:/home/devops/inventory
      - ./data/env:/home/devops/env
      - ./data/terraform/apps:/home/devops/terraform/apps
      - ./data/terraform/infra:/home/devops/terraform/infra
      - ./data/terraform/dmz:/home/devops/terraform/dmz
      - ./images:/images
    networks:
      - internal
    depends_on:
      postgres:
        condition: service_healthy

  # ========================================
  # PostgreSQL Database
  # ========================================
  postgres:
    image: postgres:15
    container_name: postgres
    restart: unless-stopped
    environment:
      POSTGRES_USER: harmonisation
      POSTGRES_PASSWORD: harmonisation
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U harmonisation"]
      interval: 10s
      timeout: 5s
      retries: 5
    volumes:
      - ./data/postgres:/var/lib/postgresql/data
      - ./db_init:/docker-entrypoint-initdb.d
    networks:
      - internal

networks:
  proxy:
    driver: bridge
  internal: {}
```

**Key Architecture Points:**

1. **No Direct Backend Port Exposure**: Backend runs on port 8008 internally but is NOT exposed to host - all traffic goes through Nginx reverse proxy
2. **Network Isolation**: Two networks (proxy and internal) for security separation
3. **Health Checks**: PostgreSQL has health checks that other services depend on
4. **Resource Limits**: Backend has memory limit (4GB) and CPU shares (1024)
5. **Restart Policy**: All services use `unless-stopped` for automatic recovery
6. **Nginx Configuration**: Uses custom.conf (not nginx.conf) with read-only mount

---

### Backend Dockerfile

**backend/Dockerfile**

```dockerfile
# Use mrabbah/harmo-base as foundation (from Docker Hub)
FROM mrabbah/harmo-base:latest

USER devops
WORKDIR /home/devops

# Create directories for data persistence
RUN mkdir -p /home/devops/.local/bin /home/devops/data/.kube \
    /home/devops/data/inventory /home/devops/data/env \
    /home/devops/data/terraform /home/devops/data/doc

# Install Node.js 24 via nvm
ENV NVM_DIR="/home/devops/.nvm"
ENV NODE_VERSION="24"
RUN curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.3/install.sh | bash && \
    . $NVM_DIR/nvm.sh && \
    nvm install $NODE_VERSION && \
    ln -s "$(nvm which $NODE_VERSION)" /home/devops/.local/bin/node && \
    ln -s "$(dirname $(nvm which $NODE_VERSION))/npm" /home/devops/.local/bin/npm

# Install Claude CLI
RUN curl -fsSL https://claude.ai/install.sh | bash

# Copy application files
COPY api.py repository.py initial_db.py models.py install.py README.md CHANGELOG.md .
COPY entrypoint.sh /usr/local/bin/entrypoint.sh
COPY env /home/devops/data/env
COPY inventory /home/devops/data/inventory
COPY project /home/devops/data/project
COPY doc /home/devops/data/doc
COPY tar_images.py /home/devops/data/

# Switch to root for permission changes
USER root
RUN chown devops:devops api.py repository.py initial_db.py models.py install.py \
    README.md CHANGELOG.md /home/devops/data/tar_images.py && \
    chown -R devops:devops /home/devops/data/inventory /home/devops/data/doc \
    /home/devops/data/project /home/devops/data/env && \
    chown devops:devops /usr/local/bin/entrypoint.sh && \
    chmod +x /usr/local/bin/entrypoint.sh

# Switch back to devops user
USER devops

# Set environment variables
ENV INFORMIXDIR='/opt/IBM/Informix.4.50.FC11W1'
ENV CSDK_HOME=${INFORMIXDIR}
ENV PATH=$INFORMIXDIR/bin:/home/devops/.local/bin:$PATH
ENV LD_LIBRARY_PATH=$INFORMIXDIR/lib:$INFORMIXDIR/lib/esql:$INFORMIXDIR/lib/cli

# Entrypoint and command
ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]
CMD ["gunicorn", "--workers", "2", "--timeout", "3600", \
     "--worker-class", "uvicorn.workers.UvicornWorker", \
     "--bind", "0.0.0.0:8008", "api:app"]
```

---

### Frontend Dockerfile

**frontend/Dockerfile**

```dockerfile
# Stage 1: Build Angular app
FROM node:20-alpine AS builder

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci

# Copy source code
COPY . .

# Build for production
RUN npm run build --configuration production

# Stage 2: Serve with Nginx
FROM nginx:alpine

# Copy built app
COPY --from=builder /app/dist/frontend /usr/share/nginx/html

# Copy nginx config
COPY nginx.conf /etc/nginx/nginx.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
```

---

## 11. Network Architecture

### Three-Zone Network Design

```
┌──────────────────────────────────────────────────────────────────┐
│                    PHYSICAL DATACENTER                            │
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  LAN_INFRA Zone (10.1.20.0/24, VLAN 20)                  │   │
│  │  ┌────────┐  ┌────────┐  ┌────────┐  ┌────────┐         │   │
│  │  │vault1  │  │gitops1 │  │haproxy1│  │haproxy2│         │   │
│  │  │.20.10  │  │.20.20  │  │.20.30  │  │.20.31  │         │   │
│  │  └────────┘  └────────┘  └────────┘  └────────┘         │   │
│  │                                                           │   │
│  │  Services: Vault, Gogs, Docker Registry, ArgoCD          │   │
│  └──────────────────────────────────────────────────────────┘   │
│                              │                                   │
│                              │ Firewall Rules                    │
│                              │ Ports: 22, 443, 6443              │
│                              ▼                                   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  LAN_APPS Zone (10.1.10.0/24, VLAN 10)                   │   │
│  │  ┌─────────────────────────────────────────────────────┐ │   │
│  │  │  RKE2-APPS Cluster                                  │ │   │
│  │  │  ┌──────────┐  ┌──────────┐  ┌──────────┐          │ │   │
│  │  │  │rkeapp-   │  │rkeapp-   │  │rkeapp-   │          │ │   │
│  │  │  │master1   │  │master2   │  │master3   │          │ │   │
│  │  │  │.10.10    │  │.10.11    │  │.10.12    │          │ │   │
│  │  │  └──────────┘  └──────────┘  └──────────┘          │ │   │
│  │  │  ┌──────────┐  ┌──────────┐  ...                   │ │   │
│  │  │  │rkeapp-   │  │rkeapp-   │                         │ │   │
│  │  │  │worker1   │  │worker2   │                         │ │   │
│  │  │  │.10.20    │  │.10.21    │                         │ │   │
│  │  │  └──────────┘  └──────────┘                         │ │   │
│  │  └─────────────────────────────────────────────────────┘ │   │
│  │                                                           │   │
│  │  ┌─────────────────────────────────────────────────────┐ │   │
│  │  │  RKE2-MIDDLEWARE Cluster                            │ │   │
│  │  │  Runs: Kafka, Keycloak, MinIO, n8n                  │ │   │
│  │  └─────────────────────────────────────────────────────┘ │   │
│  └──────────────────────────────────────────────────────────┘   │
│                              │                                   │
│                              │ Firewall Rules                    │
│                              │ Ports: 443, 80, API Gateway       │
│                              ▼                                   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  DMZ Zone (10.1.200.0/24, VLAN 200)                      │   │
│  │  ┌─────────────────────────────────────────────────────┐ │   │
│  │  │  RKE2-DMZ Cluster                                   │ │   │
│  │  │  ┌──────────┐  ┌──────────┐  ┌──────────┐          │ │   │
│  │  │  │rkedmz1   │  │rkedmz2   │  │rkedmz3   │          │ │   │
│  │  │  │.200.10   │  │.200.11   │  │.200.12   │          │ │   │
│  │  │  └──────────┘  └──────────┘  └──────────┘          │ │   │
│  │  │                                                      │ │   │
│  │  │  Runs: Gravitee API Gateway (external-facing)       │ │   │
│  │  └─────────────────────────────────────────────────────┘ │   │
│  │                                                           │   │
│  │  ┌──────────┐  ┌──────────┐                              │   │
│  │  │  lbdmz1  │  │  lbdmz2  │  (HAProxy Load Balancers)    │   │
│  │  │.200.30   │  │.200.31   │                              │   │
│  │  └──────────┘  └──────────┘                              │   │
│  └──────────────────────────────────────────────────────────┘   │
│                              │                                   │
│                              │ NAT / Firewall                    │
│                              ▼                                   │
│                       INTERNET / USERS                           │
└──────────────────────────────────────────────────────────────────┘
```

### Flow Matrix (Firewall Rules)

**Default Rules:**

| Source | Destination | Ports | Protocol | Purpose |
|--------|-------------|-------|----------|---------|
| LAN_INFRA | LAN_APPS | 22, 6443, 443 | TCP | Kubernetes management |
| LAN_INFRA | LAN_APPS | All | TCP | Vault, Gogs access |
| LAN_APPS | LAN_INFRA | 8200, 3000, 5000 | TCP | Vault, Gogs, Registry |
| LAN_APPS | DMZ | 443, 80 | TCP | API Gateway access |
| DMZ | LAN_APPS | 443 | TCP | Backend API calls |
| Internet | DMZ | 443, 80 | TCP | External users |

---

## 12. Security Architecture

### Multi-Layer Security

**Layer 1: Network Segmentation**
- 3 isolated VLANs (LAN_INFRA, LAN_APPS, DMZ)
- Firewall rules between zones (flow matrix)
- Private networks (no direct internet access except DMZ)

**Layer 2: TLS Encryption**
- Cert-Manager for automatic certificate generation
- Let's Encrypt integration or internal CA
- All communication encrypted (HTTPS, TLS)

**Layer 3: Secrets Management (Vault)**
- All passwords/tokens stored in Vault
- Vault Kubernetes integration (sidecar injection)
- No secrets in Git repositories
- Automatic secret rotation

**Layer 4: Access Control**
- Keycloak SSO (Single Sign-On)
- LDAP/AD integration
- Role-Based Access Control (RBAC)
- Multi-Factor Authentication (MFA)

**Layer 5: Runtime Security (NeuVector)**
- Container runtime protection
- Network micro-segmentation
- Vulnerability scanning
- Compliance reporting

**Layer 6: Database Encryption**
- Passwords encrypted with Fernet
- Database connections over TLS
- Separate encryption keys per record

---

## 13. Data Flow (Step-by-Step)

### Complete Request Flow: Create VM Architecture

```
Step 1: User submits user count (5000 users)
┌─────────────┐
│   Browser   │  POST /runner/api/configuration
│  (Angular)  │  Body: {number_concurrent_users: 5000}
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  Nginx:80   │  Reverse proxy
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  Backend    │  api.py: @app.post("/runner/api/configuration")
│  (FastAPI)  │  1. Validates input (Pydantic)
└──────┬──────┘  2. Calls repository.save_configuration()
       │
       ▼
┌─────────────┐
│ Repository  │  repository.py: save_configuration()
│ (Business   │  1. Creates Configuration record
│  Logic)     │  2. Encrypts sensitive data
└──────┬──────┘  3. Saves to database
       │
       ▼
┌─────────────┐
│ PostgreSQL  │  INSERT INTO configurations VALUES (...)
│  Database   │
└─────────────┘

Step 2: User requests VM architecture
┌─────────────┐
│   Browser   │  GET /runner/api/virtual-machines
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  Backend    │  api.py: @app.get("/runner/api/virtual-machines")
└──────┬──────┘  1. Checks if VMs exist
       │          2. If not → calls scaffold_architecture()
       ▼
┌─────────────┐
│ Repository  │  repository.py: scaffold_architecture()
│             │
│ BRAIN OF    │  1. Get user_count from configurations table
│  PLATFORM   │     → 5000 users
│             │
│             │  2. Query vm_configurations table:
│             │     SELECT * FROM vm_configurations
│             │     WHERE user_count = 5000
│             │
│             │     Returns:
│             │     - RKEAPPS_CONTROL: 3 nodes, 8 CPU, 16 GB
│             │     - RKEAPPS_WORKER: 20 nodes, 16 CPU, 32 GB
│             │     - RKEMIDDLEWARE_CONTROL: 3 nodes, 8 CPU, 16 GB
│             │     - RKEMIDDLEWARE_WORKER: 10 nodes, 12 CPU, 24 GB
│             │     - VAULT: 2 nodes, 4 CPU, 8 GB
│             │     - etc.
│             │
│             │  3. For each VM type:
│             │     a. Assign to zone (zone_map)
│             │     b. Generate hostname (prefix + type + number)
│             │     c. Get next available IP from zone pool
│             │     d. Create VirtualMachine record
│             │
│             │  4. Add flow_matrix rules between zones
│             │
│             │  5. Commit to database
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ PostgreSQL  │  Database now contains:
│             │
│             │  virtual_machines table:
│             │  +----+------------------+-------------+-------+
│             │  | id | hostname         | ip          | zone  |
│             │  +----+------------------+-------------+-------+
│             │  | 1  | rkeapp-master1   | 10.1.10.10  | LAN   |
│             │  | 2  | rkeapp-master2   | 10.1.10.11  | LAN   |
│             │  | 3  | rkeapp-master3   | 10.1.10.12  | LAN   |
│             │  | 4  | rkeapp-worker1   | 10.1.10.20  | LAN   |
│             │  | 5  | rkeapp-worker2   | 10.1.10.21  | LAN   |
│             │  | ...                                          |
│             │  | 38 | vault1           | 10.1.20.10  | INFRA |
│             │  | 39 | vault2           | 10.1.20.11  | INFRA |
│             │  +----+------------------+-------------+-------+
└──────┬──────┘
       │
       ▼
┌─────────────┐
│   Browser   │  Receives JSON response:
│             │  {
│             │    "total_vms": 42,
│             │    "total_cpu": 456,
│             │    "total_ram": 912384,
│             │    "vms": [
│             │      {
│             │        "hostname": "rkeapp-master1",
│             │        "ip": "10.1.10.10",
│             │        "cpu": 8,
│             │        "ram": 16384,
│             │        "zone": "LAN_APPS"
│             │      },
│             │      ...
│             │    ]
│             │  }
└─────────────┘
```

---

## 14. Deployment Workflow (Complete Process)

### Full Deployment Sequence

```
┌──────────────────────────────────────────────────────────────────┐
│ USER CLICKS "START DEPLOYMENT" BUTTON                            │
└──────────────────────────────────────────────────────────────────┘
                             │
                             ▼
┌──────────────────────────────────────────────────────────────────┐
│ Frontend: POST /runner/api/start                                 │
└──────────────────────────────────────────────────────────────────┘
                             │
                             ▼
┌──────────────────────────────────────────────────────────────────┐
│ Backend: api.py - start_deployment()                             │
│ Launches install.py in background thread                         │
└──────────────────────────────────────────────────────────────────┘
                             │
                             ▼
┌──────────────────────────────────────────────────────────────────┐
│ install.py - Main Orchestrator                                   │
│ Loops through ALL_ROLES list                                     │
└──────────────────────────────────────────────────────────────────┘
                             │
         ┌───────────────────┴───────────────────┐
         │                                       │
         ▼                                       ▼
┌─────────────────────┐               ┌─────────────────────┐
│ PHASE 1: PROVISION  │               │ Database Update     │
│ VMs (Terraform)     │               │ role_status =       │
└─────────────────────┘               │ "in_progress"       │
         │                             └─────────────────────┘
         │
         ▼
Role: provisionnement-vms-infra
┌──────────────────────────────────────────────────────────────────┐
│ 1. prepare_inputs.py:                                            │
│    - Query zones table (LAN_INFRA zone)                          │
│    - Query virtual_machines table (group='vault', 'gitops', etc.)│
│    - Query vmware_esxi table (vCenter credentials)               │
│    - Returns extra_vars dict and inventory to Ansible            │
│                                                                   │
│    extra_vars = {                                                │
│      'vcenter_server': 'vcenter.example.com',                    │
│      'vcenter_user': 'administrator@vsphere.local',              │
│      'vcenter_password': decrypt('encrypted_pass'),              │
│      'datacenter': 'DC1',                                        │
│      'datastore': 'datastore1',                                  │
│      'network': 'LAN_INFRA',                                     │
│      'template': 'ubuntu-22.04-template',                        │
│      'vms': [                                                    │
│        {                                                          │
│          'name': 'vault1',                                       │
│          'cpu': 4,                                               │
│          'memory': 8192,                                         │
│          'disk': 100,                                            │
│          'ip': '10.1.20.10',                                     │
│          'netmask': '255.255.255.0',                             │
│          'gateway': '10.1.20.1',                                 │
│          'dns': ['8.8.8.8']                                      │
│        },                                                         │
│        # ... vault2, gitops1, haproxy1, haproxy2                 │
│      ]                                                            │
│    }                                                              │
│                                                                   │
│ 2. Ansible tasks:                                                │
│    - Copy static Terraform files from roles/files/               │
│      (main.tf, variables.tf, versions.tf)                        │
│    - Generate terraform.tfvars from Jinja2 template             │
│      using extra_vars from prepare_inputs.py                     │
│                                                                   │
│ 3. Ansible executes Terraform:                                   │
│    - terraform init                                              │
│    - terraform plan                                              │
│    - terraform apply -auto-approve                               │
│                                                                   │
│ 4. Terraform connects to vCenter API:                            │
│    - Clones VM from template                                     │
│    - Customizes VM (hostname, IP, DNS)                           │
│    - Powers on VM                                                │
│    - Waits for VMware Tools                                      │
│                                                                   │
│ 5. Terraform state saved to: /data/terraform/terraform.tfstate   │
│                                                                   │
│ Result: 6 VMs created in LAN_INFRA zone                          │
│ Time: ~15 minutes                                                │
└──────────────────────────────────────────────────────────────────┘
         │
         ▼
Role: provisionnement-vms-apps
(Same process for LAN_APPS zone → creates 33 VMs)
Time: ~25 minutes
         │
         ▼
Role: provisionnement-vms-dmz
(Same process for DMZ zone → creates 5 VMs)
Time: ~10 minutes
         │
         ▼
┌──────────────────────────────────────────────────────────────────┐
│ PHASE 2: BASE CONFIGURATION                                      │
└──────────────────────────────────────────────────────────────────┘
         │
         ▼
Role: prepare-vms
┌──────────────────────────────────────────────────────────────────┐
│ 1. prepare_inputs.py:                                            │
│    - Query ALL virtual_machines                                  │
│    - Generate inventory (all VMs)                                │
│                                                                   │
│ 2. Ansible tasks:                                                │
│    - Update OS packages (apt update && apt upgrade)              │
│    - Install base packages (curl, wget, vim, git)                │
│    - Configure SSH keys                                          │
│    - Set /etc/hosts entries                                      │
│    - Configure NTP time sync                                     │
│    - Disable firewall (managed by external firewall)             │
│                                                                   │
│ Time: ~12 minutes                                                │
└──────────────────────────────────────────────────────────────────┘
         │
         ▼
┌──────────────────────────────────────────────────────────────────┐
│ PHASE 3: INFRASTRUCTURE SERVICES                                 │
└──────────────────────────────────────────────────────────────────┘
         │
         ▼
Role: install-docker-registry
┌──────────────────────────────────────────────────────────────────┐
│ 1. Ansible tasks:                                                │
│    - Install Docker Engine                                       │
│    - Run Docker Registry v2 container                            │
│    - Configure TLS certificates                                  │
│    - Upload Kubernetes images to registry                        │
│                                                                   │
│ 2. Post-install:                                                 │
│    - Save registry URL to database                               │
│                                                                   │
│ Time: ~8 minutes                                                 │
└──────────────────────────────────────────────────────────────────┘
         │
         ▼
Role: install-vault
(Already explained in section 9.2)
Time: ~10 minutes
         │
         ▼
Role: install-gogs
(Git server for storing Kubernetes manifests)
Time: ~5 minutes
         │
         ▼
Role: install-load-balancer
(HAProxy load balancers for Kubernetes API servers)
Time: ~7 minutes
         │
         ▼
┌──────────────────────────────────────────────────────────────────┐
│ PHASE 4: KUBERNETES CLUSTERS                                     │
└──────────────────────────────────────────────────────────────────┘
         │
         ▼
Role: install-rke2-apps
┌──────────────────────────────────────────────────────────────────┐
│ 1. prepare_inputs.py:                                            │
│    - Get RKEAPPS_CONTROL nodes (masters)                         │
│    - Get RKEAPPS_WORKER nodes (workers)                          │
│    - Get registry URL                                            │
│    - Get HAProxy VIP                                             │
│                                                                   │
│ 2. Ansible tasks (on first master):                              │
│    - Download RKE2 binary                                        │
│    - Create /etc/rancher/rke2/config.yaml:                       │
│        system-default-registry: registry1:5000                   │
│        cluster-cidr: 10.42.0.0/16                                │
│        service-cidr: 10.43.0.0/16                                │
│        tls-san:                                                  │
│          - haproxy-vip-ip                                        │
│    - Start rke2-server service                                   │
│    - Wait for cluster to be ready                                │
│    - Fetch kubeconfig                                            │
│                                                                   │
│ 3. Ansible tasks (on additional masters):                        │
│    - Create config.yaml with server: https://first-master:9345  │
│    - Copy node token from first master                           │
│    - Start rke2-server service                                   │
│                                                                   │
│ 4. Ansible tasks (on workers):                                   │
│    - Create config.yaml with server URL                          │
│    - Start rke2-agent service                                    │
│                                                                   │
│ 5. Verify cluster:                                               │
│    - kubectl get nodes (should show all nodes Ready)             │
│                                                                   │
│ Time: ~30 minutes                                                │
└──────────────────────────────────────────────────────────────────┘
         │
         ▼
Role: install-rke2-middleware
(Same process for middleware cluster)
Time: ~25 minutes
         │
         ▼
Role: install-rke2-dmz
(Same process for DMZ cluster)
Time: ~20 minutes
         │
         ▼
┌──────────────────────────────────────────────────────────────────┐
│ PHASE 5: KUBERNETES FOUNDATION                                   │
└──────────────────────────────────────────────────────────────────┘
         │
         ▼
Role: install-rancher
┌──────────────────────────────────────────────────────────────────┐
│ 1. Ansible tasks:                                                │
│    - Add Helm repo: rancher-stable                               │
│    - Install Rancher via Helm:                                   │
│        helm install rancher rancher-stable/rancher \             │
│          --namespace cattle-system \                             │
│          --set hostname=rancher.example.com \                    │
│          --set bootstrapPassword=admin123                        │
│    - Wait for Rancher pods to be ready                           │
│    - Import all 3 clusters into Rancher                          │
│                                                                   │
│ 2. Post-install:                                                 │
│    - Save Rancher URL and API token to database                  │
│                                                                   │
│ Time: ~15 minutes                                                │
└──────────────────────────────────────────────────────────────────┘
         │
         ▼
Role: install-argocd
(GitOps deployment tool)
Time: ~10 minutes
         │
         ▼
Role: install-cert-manager
(TLS certificate automation)
Time: ~8 minutes
         │
         ▼
Role: install-longhorn
(Distributed storage)
Time: ~12 minutes
         │
         ▼
Role: setup-vault-injector
(Vault Kubernetes integration)
Time: ~10 minutes
         │
         ▼
┌──────────────────────────────────────────────────────────────────┐
│ PHASE 6: MIDDLEWARE                                              │
└──────────────────────────────────────────────────────────────────┘
         │
         ▼
Role: install-minio
(S3-compatible object storage)
Time: ~10 minutes
         │
         ▼
Role: install-keycloak
(Identity and Access Management)
Time: ~15 minutes
         │
         ▼
Role: install-kafka
(Event streaming platform)
Time: ~18 minutes
         │
         ▼
Role: install-n8n
(Workflow automation)
Time: ~8 minutes
         │
         ▼
┌──────────────────────────────────────────────────────────────────┐
│ PHASE 7: API GATEWAYS                                            │
└──────────────────────────────────────────────────────────────────┘
         │
         ▼
Role: install-gravitee-lan
(API Gateway for LAN)
Time: ~20 minutes
         │
         ▼
Role: install-gravitee-dmz
(API Gateway for DMZ)
Time: ~18 minutes
         │
         ▼
┌──────────────────────────────────────────────────────────────────┐
│ PHASE 8: SECURITY & MONITORING (Optional)                        │
└──────────────────────────────────────────────────────────────────┘
         │
         ▼
Role: install-neuvector
(Container security)
Time: ~15 minutes
         │
         ▼
Role: install-monitoring
(Coroot observability platform)
Time: ~20 minutes
         │
         ▼
┌──────────────────────────────────────────────────────────────────┐
│ ✅ DEPLOYMENT COMPLETE!                                          │
│                                                                   │
│ Total Time: ~5 hours 30 minutes                                  │
│ Total VMs: 42                                                    │
│ Total vCPUs: 456                                                 │
│ Total RAM: 912 GB                                                │
│                                                                   │
│ Deployed Services:                                               │
│ ✓ 3 Kubernetes Clusters (RKE2)                                   │
│ ✓ Rancher Management                                             │
│ ✓ ArgoCD (GitOps)                                                │
│ ✓ Cert-Manager (TLS)                                             │
│ ✓ Longhorn (Storage)                                             │
│ ✓ Vault (Secrets)                                                │
│ ✓ MinIO (Object Storage)                                         │
│ ✓ Keycloak (SSO)                                                 │
│ ✓ Kafka (Event Streaming)                                        │
│ ✓ Gravitee (API Gateway)                                         │
│ ✓ NeuVector (Security)                                           │
│ ✓ Coroot (Monitoring)                                            │
│                                                                   │
│ Access URLs:                                                     │
│ - Rancher:   https://rancher.example.com                         │
│ - ArgoCD:    https://argocd.example.com                          │
│ - Keycloak:  https://keycloak.example.com                        │
│ - MinIO:     https://minio.example.com                           │
│ - Gravitee:  https://api.example.com                             │
│ - Coroot:    https://monitoring.example.com                      │
│                                                                   │
│ All credentials saved in database (encrypted)                    │
└──────────────────────────────────────────────────────────────────┘
```

---

## 15. Hypervisor Integration (VMware & Nutanix)

### Detailed VMware Integration

**Architecture:**

```
Backend Container
├─ pyvmomi (Python vSphere SDK)
├─ govc (vSphere CLI)
└─ Terraform vsphere provider

        │
        │ HTTPS API (Port 443)
        ▼

┌──────────────────────────────────────────────────────────────────┐
│                    VMware vCenter Server                          │
│                                                                   │
│  ┌──────────────────┐  ┌──────────────────┐                     │
│  │   vCenter API    │  │   Web UI         │                     │
│  └──────────────────┘  └──────────────────┘                     │
│           │                                                       │
│           ▼                                                       │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │           Datacenter: DC1                                │   │
│  │  ┌───────────────────────────────────────────────────┐  │   │
│  │  │  Cluster: Cluster01                               │  │   │
│  │  │  ┌─────────┐  ┌─────────┐  ┌─────────┐           │  │   │
│  │  │  │  ESXi1  │  │  ESXi2  │  │  ESXi3  │           │  │   │
│  │  │  │  Host   │  │  Host   │  │  Host   │           │  │   │
│  │  │  └─────────┘  └─────────┘  └─────────┘           │  │   │
│  │  └───────────────────────────────────────────────────┘  │   │
│  │  ┌───────────────────────────────────────────────────┐  │   │
│  │  │  Datastore: Datastore01 (2TB SSD)                 │  │   │
│  │  └───────────────────────────────────────────────────┘  │   │
│  │  ┌───────────────────────────────────────────────────┐  │   │
│  │  │  Network: VLAN10 (LAN_APPS)                       │  │   │
│  │  │  Network: VLAN20 (LAN_INFRA)                      │  │   │
│  │  │  Network: VLAN200 (DMZ)                           │  │   │
│  │  └───────────────────────────────────────────────────┘  │   │
│  └─────────────────────────────────────────────────────────┘   │
└──────────────────────────────────────────────────────────────────┘
```

**Connection Testing:**

```python
# backend/repository.py

def test_vmware_connection(api_url, login, password, Session):
    """
    Test VMware vCenter connection using pyvmomi.
    """
    from pyVim.connect import SmartConnect, Disconnect
    import ssl

    try:
        # Disable SSL verification (for self-signed certs)
        context = ssl._create_unverified_context()

        # Connect to vCenter
        service_instance = SmartConnect(
            host=api_url.replace('https://', '').replace('http://', ''),
            user=login,
            pwd=password,
            sslContext=context
        )

        # Get vCenter version
        about = service_instance.content.about

        # Disconnect
        Disconnect(service_instance)

        return {
            'success': True,
            'message': f'Connected to vCenter {about.version}',
            'version': about.version,
            'build': about.build
        }

    except Exception as e:
        return {
            'success': False,
            'message': str(e)
        }
```

---

### Detailed Nutanix Integration

**Architecture:**

```
Backend Container
├─ Terraform nutanix provider
└─ REST API client (requests library)

        │
        │ HTTPS API (Port 9440)
        ▼

┌──────────────────────────────────────────────────────────────────┐
│                    Nutanix Prism Central                          │
│                                                                   │
│  ┌──────────────────┐  ┌──────────────────┐                     │
│  │   REST API v3    │  │   Web UI         │                     │
│  └──────────────────┘  └──────────────────┘                     │
│           │                                                       │
│           ▼                                                       │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │           Cluster: Nutanix-Cluster-01                    │   │
│  │  ┌───────────────────────────────────────────────────┐  │   │
│  │  │  AHV Hypervisor                                   │  │   │
│  │  │  ┌─────────┐  ┌─────────┐  ┌─────────┐           │  │   │
│  │  │  │  Node1  │  │  Node2  │  │  Node3  │           │  │   │
│  │  │  │  (HCI)  │  │  (HCI)  │  │  (HCI)  │           │  │   │
│  │  │  └─────────┘  └─────────┘  └─────────┘           │  │   │
│  │  └───────────────────────────────────────────────────┘  │   │
│  │  ┌───────────────────────────────────────────────────┐  │   │
│  │  │  Storage Container: default-storage (10TB)        │  │   │
│  │  └───────────────────────────────────────────────────┘  │   │
│  │  ┌───────────────────────────────────────────────────┐  │   │
│  │  │  Subnet: VLAN10 (LAN_APPS)                        │  │   │
│  │  │  Subnet: VLAN20 (LAN_INFRA)                       │  │   │
│  │  │  Subnet: VLAN200 (DMZ)                            │  │   │
│  │  └───────────────────────────────────────────────────┘  │   │
│  └─────────────────────────────────────────────────────────┘   │
└──────────────────────────────────────────────────────────────────┘
```

**Terraform Nutanix Provider:**

```hcl
# Generated by prepare_inputs.py

terraform {
  required_providers {
    nutanix = {
      source  = "nutanix/nutanix"
      version = "~> 1.9.0"
    }
  }
}

provider "nutanix" {
  username  = var.prism_username
  password  = var.prism_password
  endpoint  = var.prism_endpoint
  port      = 9440
  insecure  = true  # For self-signed certs
}

# Get cluster info
data "nutanix_cluster" "cluster" {
  name = var.cluster_name
}

# Get subnet info
data "nutanix_subnet" "lan_apps" {
  subnet_name = "VLAN10"
}

# Create VM
resource "nutanix_virtual_machine" "vault1" {
  name                 = "vault1"
  cluster_uuid         = data.nutanix_cluster.cluster.id
  num_vcpus_per_socket = 1
  num_sockets          = 4
  memory_size_mib      = 8192

  # OS Disk (clone from image)
  disk_list {
    data_source_reference = {
      kind = "image"
      uuid = var.ubuntu_image_uuid
    }
    device_properties {
      device_type = "DISK"
      disk_address = {
        device_index = 0
        adapter_type = "SCSI"
      }
    }
    disk_size_mib = 102400  # 100 GB
  }

  # Data Disk (empty)
  disk_list {
    disk_size_mib = 204800  # 200 GB
    device_properties {
      device_type = "DISK"
      disk_address = {
        device_index = 1
        adapter_type = "SCSI"
      }
    }
  }

  # Network
  nic_list {
    subnet_uuid = data.nutanix_subnet.lan_apps.id
    ip_endpoint_list {
      ip   = "10.1.20.10"
      type = "ASSIGNED"
    }
  }

  # Cloud-init customization
  guest_customization_cloud_init_user_data = base64encode(<<-EOF
    #cloud-config
    hostname: vault1
    fqdn: vault1.example.com
    manage_etc_hosts: true

    users:
      - name: devops
        sudo: ALL=(ALL) NOPASSWD:ALL
        shell: /bin/bash
        ssh_authorized_keys:
          - ${var.ssh_public_key}

    package_update: true
    package_upgrade: true

    packages:
      - curl
      - wget
      - vim
      - git
  EOF
  )
}
```

**Connection Testing:**

```python
# backend/repository.py

def test_nutanix_connection(prism_url, username, password, Session):
    """
    Test Nutanix Prism Central connection using REST API.
    """
    import requests
    import json

    try:
        # Nutanix API endpoint
        url = f"{prism_url}:9440/api/nutanix/v3/clusters/list"

        # Headers
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }

        # Auth
        auth = (username, password)

        # Request body
        data = {
            'kind': 'cluster',
            'length': 10
        }

        # Make request
        response = requests.post(
            url,
            auth=auth,
            headers=headers,
            json=data,
            verify=False  # For self-signed certs
        )

        if response.status_code == 200:
            clusters = response.json().get('entities', [])
            return {
                'success': True,
                'message': f'Connected to Prism Central. Found {len(clusters)} cluster(s)',
                'clusters': [c['spec']['name'] for c in clusters]
            }
        else:
            return {
                'success': False,
                'message': f'HTTP {response.status_code}: {response.text}'
            }

    except Exception as e:
        return {
            'success': False,
            'message': str(e)
        }
```

---

## 16. Terraform Integration

### Why Terraform?

**Terraform vs Ansible for VM Provisioning:**

| Feature | Terraform | Ansible |
|---------|-----------|---------|
| **State Management** | Yes (tracks infrastructure) | No |
| **Idempotency** | Yes | Yes |
| **Dry-run** | Yes (`terraform plan`) | Limited |
| **Rollback** | Easy | Manual |
| **Multi-cloud** | Excellent | Good |
| **VM Customization** | Limited | Excellent |
| **Learning Curve** | Moderate | Easy |

**Platform uses both:**
- **Terraform** for VM provisioning (create/destroy VMs)
- **Ansible** for VM configuration (install software, configure services)

---

### Terraform Workflow in Platform

```
┌──────────────────────────────────────────────────────────────────┐
│ Step 1: User Configuration Saved to Database                     │
└──────────────────────────────────────────────────────────────────┘
                             │
                             ▼
┌──────────────────────────────────────────────────────────────────┐
│ Step 2: Ansible Role Starts (provisionnement-vms-infra)          │
└──────────────────────────────────────────────────────────────────┘
                             │
                             ▼
┌──────────────────────────────────────────────────────────────────┐
│ Step 3: prepare_inputs.py Returns Variables from Database        │
│                                                                   │
│ 1. Query database:                                               │
│    - vmware_esxi table → vCenter credentials                     │
│    - zones table → Network info                                  │
│    - virtual_machines table → VMs to create                      │
│                                                                   │
│ 2. Returns to Ansible:                                           │
│    - extra_vars: Dictionary with all variables                   │
│      {                                                            │
│        "machines": [...],                                         │
│        "login": "admin@vsphere.local",                            │
│        "password": "decrypted_password",                          │
│        "url": "vcenter.example.com",                              │
│        "datacenter": "DC1",                                       │
│        "datastore": "Datastore01",                                │
│        ...                                                        │
│      }                                                            │
│    - inventory: Ansible inventory (localhost)                    │
└──────────────────────────────────────────────────────────────────┘
                             │
                             ▼
┌──────────────────────────────────────────────────────────────────┐
│ Step 4: Ansible Tasks Setup Terraform Environment                │
│                                                                   │
│ - name: Create terraform directory                               │
│   file:                                                          │
│     path: /home/devops/terraform/infra                           │
│     state: directory                                             │
│                                                                   │
│ - name: Copy static Terraform files                              │
│   copy:                                                          │
│     src: files/                                                  │
│     dest: /home/devops/terraform/infra                           │
│   # Copies:                                                      │
│   #   - main.tf (static VM resource definitions)                 │
│   #   - variables.tf (variable declarations)                     │
│   #   - versions.tf (provider versions)                          │
│   #   - .terraformrc (Terraform config)                          │
│                                                                   │
│ - name: Generate terraform.tfvars from template                  │
│   template:                                                      │
│     src: terraform-vcenter.tfvars.j2                             │
│     dest: /home/devops/terraform/infra/terraform.tfvars          │
│   # Uses extra_vars from prepare_inputs.py to populate values    │
└──────────────────────────────────────────────────────────────────┘
                             │
                             ▼
┌──────────────────────────────────────────────────────────────────┐
│ Step 5: Ansible Executes Terraform Commands                      │
│                                                                   │
│ - name: Initialize Terraform                                     │
│   command: terraform init                                        │
│   args:                                                          │
│     chdir: /home/devops/terraform/infra                          │
│                                                                   │
│ - name: Apply infrastructure                                     │
│   command: terraform apply -auto-approve                         │
│   args:                                                          │
│     chdir: /home/devops/terraform/infra                          │
│   register: terraform_output                                     │
│   environment:                                                   │
│     TF_PLUGIN_CACHE_DIR: /home/devops/terraform/infra/providers_cache │
│     TF_CLI_CONFIG_FILE: /home/devops/terraform/infra/.terraformrc │
│     TF_VAR_skip_ssl: "{{ skip_ssl | lower }}"                   │
└──────────────────────────────────────────────────────────────────┘
                             │
                             ▼
┌──────────────────────────────────────────────────────────────────┐
│ Step 6: Terraform Provisions VMs                                 │
│                                                                   │
│ Terraform connects to vCenter API and:                           │
│ 1. Creates VMs from template (using template_mapping by group)   │
│    - RKE roles (RKEAPPS/RKEMIDDLEWARE/RKEDMZ): harmo-rke-agents │
│    - Docker roles (vault/gitops/monitoring): harmo-docker-agents │
│ 2. Configures resources (CPU, RAM, disks)                        │
│ 3. Uses cloud-init for customization (userdata + metadata)       │
│    - Sets hostname, domain, static IP, gateway, DNS              │
│    - Configures disk mounts (/var/lib/longhorn or /data)         │
│ 4. Powers on VMs and waits for VMware Tools                      │
│ 5. Saves state to /home/devops/terraform/infra/terraform.tfstate │
└──────────────────────────────────────────────────────────────────┘
                             │
                             ▼
┌──────────────────────────────────────────────────────────────────┐
│ Step 7: Post-Provisioning                                        │
│                                                                   │
│ Ansible waits for SSH to be available:                           │
│                                                                   │
│ - name: Wait for SSH                                             │
│   wait_for:                                                      │
│     host: "{{ item.ip }}"                                        │
│     port: 22                                                     │
│     timeout: 300                                                 │
│   loop: "{{ virtual_machines }}"                                 │
│                                                                   │
│ Then marks VMs as provisioned in database:                       │
│                                                                   │
│ UPDATE virtual_machines                                          │
│ SET is_provisioned = TRUE, provisioned_at = NOW()                │
│ WHERE hostname IN ('vault1', 'vault2', ...)                      │
└──────────────────────────────────────────────────────────────────┘
```

---

### Terraform State Management

**terraform.tfstate** (Tracks provisioned infrastructure)

```json
{
  "version": 4,
  "terraform_version": "1.9.8",
  "serial": 15,
  "lineage": "abc123-def456-ghi789",
  "outputs": {},
  "resources": [
    {
      "mode": "managed",
      "type": "vsphere_virtual_machine",
      "name": "vault1",
      "provider": "provider[\"registry.terraform.io/hashicorp/vsphere\"]",
      "instances": [
        {
          "schema_version": 3,
          "attributes": {
            "id": "vm-12345",
            "name": "vault1",
            "num_cpus": 4,
            "memory": 8192,
            "guest_id": "ubuntu64Guest",
            "datastore_id": "datastore-67890",
            "network_interface": [
              {
                "network_id": "network-11111",
                "adapter_type": "vmxnet3",
                "mac_address": "00:50:56:ab:cd:ef"
              }
            ],
            "disk": [
              {
                "label": "disk0",
                "size": 100,
                "thin_provisioned": true,
                "unit_number": 0
              }
            ],
            "default_ip_address": "10.1.20.10",
            "guest_ip_addresses": ["10.1.20.10"],
            "uuid": "42056f3a-6d1e-5e59-9c8f-1234567890ab",
            "power_state": "on"
          }
        }
      ]
    },
    {
      "mode": "managed",
      "type": "vsphere_virtual_machine",
      "name": "vault2",
      "provider": "provider[\"registry.terraform.io/hashicorp/vsphere\"]",
      "instances": [
        {
          "schema_version": 3,
          "attributes": {
            "id": "vm-12346",
            "name": "vault2",
            "num_cpus": 4,
            "memory": 8192,
            // ... more attributes
          }
        }
      ]
    }
    // ... more VMs
  ]
}
```

**Why state matters:**
- Terraform knows which VMs it created
- Can update VM specs (`terraform apply` again)
- Can destroy infrastructure (`terraform destroy`)
- Prevents duplicate VM creation

---

### Scaling Infrastructure

**Add More VMs:**

1. User increases user count: 5000 → 10000
2. Frontend calls: `POST /configuration {user_count: 10000}`
3. Backend re-runs `scaffold_architecture()`
4. New VMs added to `virtual_machines` table
5. Re-run provisioning role to regenerate terraform.tfvars
6. Re-run Terraform:
   ```bash
   cd /home/devops/terraform/infra
   terraform plan  # Shows: +15 to add
   terraform apply -auto-approve  # Creates 15 new VMs
   ```
7. Terraform updates state file with new VMs

**Remove VMs:**

1. User decreases user count: 10000 → 5000
2. Backend removes VMs from `virtual_machines` table
3. Re-run provisioning role to update terraform.tfvars
4. Re-run Terraform:
   ```bash
   cd /home/devops/terraform/infra
   terraform plan  # Shows: -15 to destroy
   terraform apply -auto-approve  # Deletes 15 VMs
   ```
5. Terraform removes from state file

---

## 17. How Everything Connects

### End-to-End Data Flow Diagram

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                                                                                  │
│                              USER WORKSTATION                                    │
│                                                                                  │
│  ┌───────────────────────────────────────────────────────────────────────────┐ │
│  │  Web Browser: http://platform.example.com/runner/                         │ │
│  │                                                                            │ │
│  │  [Wizard Step 1] → Choose VMware or Nutanix                               │ │
│  │  [Wizard Step 2] → Configure network zones                                │ │
│  │  [Wizard Step 3] → Security settings                                      │ │
│  │  [Wizard Step 4] → External services (LDAP, SMTP, databases)              │ │
│  │  [Wizard Step 5] → Select user count (100, 500, 1000, 5000, 10000)        │ │
│  │  [Wizard Step 6] → Review generated VM architecture                       │ │
│  │  [Wizard Step 7] → Click "Start Deployment"                               │ │
│  └───────────────────────────────────────────────────────────────────────────┘ │
│                                        │                                         │
│                                        │ HTTP POST /runner/api/start            │
│                                        ▼                                         │
└─────────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────────┐
│                                                                                  │
│                         DOCKER COMPOSE STACK (Local)                             │
│                                                                                  │
│  ┌────────────────────────────────────────────────────────────────────────┐    │
│  │  NGINX Container                                                        │    │
│  │  ┌──────────────────────────────────────────────────────────────────┐  │    │
│  │  │  Reverse Proxy Rules:                                            │  │    │
│  │  │  /runner/             → frontend:4200                            │  │    │
│  │  │  /runner/api/         → backend:8000                             │  │    │
│  │  │  /corteza/            → corteza:18080                            │  │    │
│  │  └──────────────────────────────────────────────────────────────────┘  │    │
│  └────────────────────────────────────────────────────────────────────────┘    │
│          │                         │                                            │
│          │                         │                                            │
│          ▼                         ▼                                            │
│  ┌─────────────────┐      ┌──────────────────────────────────────────────┐    │
│  │  FRONTEND       │      │  BACKEND                                      │    │
│  │  (Angular)      │      │  (FastAPI + Ansible + harmo-base)             │    │
│  │  Port: 4200     │      │  Port: 8000                                   │    │
│  │                 │      │                                               │    │
│  │  Serves:        │      │  Contains:                                    │    │
│  │  - HTML/CSS/JS  │      │  - Python 3.12 (FastAPI)                      │    │
│  │  - Angular app  │      │  - Python 3.7 (Informix)                      │    │
│  └─────────────────┘      │  - Ansible 2.16+                              │    │
│                           │  - kubectl, helm, terraform                   │    │
│                           │  - govc (VMware CLI)                          │    │
│                           │  - IBM Informix SDK                           │    │
│                           │                                               │    │
│                           │  api.py        → REST endpoints               │    │
│                           │  repository.py → Business logic               │    │
│                           │  models.py     → Database models              │    │
│                           │  install.py    → Ansible orchestrator         │    │
│                           │                                               │    │
│                           └───────────────────┬───────────────────────────┘    │
│                                               │                                 │
│                                               │ SQL Queries                     │
│                                               ▼                                 │
│                           ┌──────────────────────────────────────────────┐    │
│                           │  POSTGRESQL Container                         │    │
│                           │  Port: 5432                                   │    │
│                           │                                               │    │
│                           │  Database: harmonisation                      │    │
│                           │                                               │    │
│                           │  Tables (30+):                                │    │
│                           │  - vmware_esxi                                │    │
│                           │  - nutanix_ahv                                │    │
│                           │  - zones                                      │    │
│                           │  - virtual_machines                           │    │
│                           │  - vm_configurations                          │    │
│                           │  - ansible_roles                              │    │
│                           │  - task_logs                                  │    │
│                           │  - vault_credentials                          │    │
│                           │  - ldap, smtp_server, security, ...           │    │
│                           │                                               │    │
│                           │  Persistent Volume:                           │    │
│                           │  ./data/postgres → /var/lib/postgresql/data   │    │
│                           └──────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────────────────┘

                                     │
                                     │ Ansible connects via SSH
                                     │ Terraform connects via API
                                     ▼

┌─────────────────────────────────────────────────────────────────────────────────┐
│                                                                                  │
│                         CLIENT DATACENTER INFRASTRUCTURE                         │
│                                                                                  │
│  ┌────────────────────────────────────────────────────────────────────────┐    │
│  │  VMware vCenter  OR  Nutanix Prism Central                             │    │
│  │  ┌──────────────────────────────────────────────────────────────────┐  │    │
│  │  │  Terraform provisions VMs via API:                              │  │    │
│  │  │  - Clones from template                                         │  │    │
│  │  │  - Sets hostname, IP, CPU, RAM, disk                            │  │    │
│  │  │  - Powers on VM                                                 │  │    │
│  │  │  - Stores state in terraform.tfstate                            │  │    │
│  │  └──────────────────────────────────────────────────────────────────┘  │    │
│  └────────────────────────────────────────────────────────────────────────┘    │
│                                     │                                           │
│                                     │ Provisions VMs                            │
│                                     ▼                                           │
│  ┌────────────────────────────────────────────────────────────────────────┐    │
│  │                       DEPLOYED VIRTUAL MACHINES                         │    │
│  │                                                                         │    │
│  │  ┌────────────────────────────────────────────────────────────────┐   │    │
│  │  │  LAN_INFRA Zone (10.1.20.0/24, VLAN 20)                        │   │    │
│  │  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐      │   │    │
│  │  │  │  vault1  │  │ gitops1  │  │haproxy1  │  │haproxy2  │      │   │    │
│  │  │  │  4CPU    │  │  4CPU    │  │  4CPU    │  │  4CPU    │      │   │    │
│  │  │  │  8GB     │  │  8GB     │  │  8GB     │  │  8GB     │      │   │    │
│  │  │  │.20.10    │  │.20.20    │  │.20.30    │  │.20.31    │      │   │    │
│  │  │  └──────────┘  └──────────┘  └──────────┘  └──────────┘      │   │    │
│  │  │                                                                │   │    │
│  │  │  Ansible configures:                                          │   │    │
│  │  │  - Vault cluster (HA)                                         │   │    │
│  │  │  - Gogs Git server                                            │   │    │
│  │  │  - Docker Registry                                            │   │    │
│  │  │  - ArgoCD                                                     │   │    │
│  │  │  - HAProxy (Kubernetes API LB)                                │   │    │
│  │  └────────────────────────────────────────────────────────────────┘   │    │
│  │                                                                         │    │
│  │  ┌────────────────────────────────────────────────────────────────┐   │    │
│  │  │  LAN_APPS Zone (10.1.10.0/24, VLAN 10)                         │   │    │
│  │  │  ┌─────────────────────────────────────────────────────────┐  │   │    │
│  │  │  │  RKE2-APPS Kubernetes Cluster                           │  │   │    │
│  │  │  │  ┌────────────┐  ┌────────────┐  ┌────────────┐        │  │   │    │
│  │  │  │  │rkeapp-     │  │rkeapp-     │  │rkeapp-     │        │  │   │    │
│  │  │  │  │master1     │  │master2     │  │master3     │        │  │   │    │
│  │  │  │  │8CPU/16GB   │  │8CPU/16GB   │  │8CPU/16GB   │        │  │   │    │
│  │  │  │  │.10.10      │  │.10.11      │  │.10.12      │        │  │   │    │
│  │  │  │  └────────────┘  └────────────┘  └────────────┘        │  │   │    │
│  │  │  │  ┌────────────┐  ┌────────────┐  ┌────────────┐        │  │   │    │
│  │  │  │  │rkeapp-     │  │rkeapp-     │  │rkeapp-     │  ...   │  │   │    │
│  │  │  │  │worker1     │  │worker2     │  │worker3     │        │  │   │    │
│  │  │  │  │16CPU/32GB  │  │16CPU/32GB  │  │16CPU/32GB  │        │  │   │    │
│  │  │  │  │.10.20      │  │.10.21      │  │.10.22      │        │  │   │    │
│  │  │  │  └────────────┘  └────────────┘  └────────────┘        │  │   │    │
│  │  │  │                                                         │  │   │    │
│  │  │  │  Ansible installs:                                      │  │   │    │
│  │  │  │  - RKE2 Kubernetes v1.31.1                              │  │   │    │
│  │  │  │  - Rancher management                                   │  │   │    │
│  │  │  │  - ArgoCD (GitOps)                                      │  │   │    │
│  │  │  │  - Cert-Manager (TLS)                                   │  │   │    │
│  │  │  │  - Longhorn (Storage)                                   │  │   │    │
│  │  │  │  - Gravitee API Gateway (LAN)                           │  │   │    │
│  │  │  └─────────────────────────────────────────────────────────┘  │   │    │
│  │  │                                                                │   │    │
│  │  │  ┌─────────────────────────────────────────────────────────┐  │   │    │
│  │  │  │  RKE2-MIDDLEWARE Kubernetes Cluster                     │  │   │    │
│  │  │  │  Masters (3x) + Workers (10x)                           │  │   │    │
│  │  │  │                                                          │  │   │    │
│  │  │  │  Runs:                                                   │  │   │    │
│  │  │  │  - Apache Kafka (event streaming)                       │  │   │    │
│  │  │  │  - Keycloak (SSO/IAM)                                   │  │   │    │
│  │  │  │  - MinIO (S3 object storage)                            │  │   │    │
│  │  │  │  - n8n (workflow automation)                            │  │   │    │
│  │  │  └─────────────────────────────────────────────────────────┘  │   │    │
│  │  └────────────────────────────────────────────────────────────────┘   │    │
│  │                                                                         │    │
│  │  ┌────────────────────────────────────────────────────────────────┐   │    │
│  │  │  DMZ Zone (10.1.200.0/24, VLAN 200)                            │   │    │
│  │  │  ┌─────────────────────────────────────────────────────────┐  │   │    │
│  │  │  │  RKE2-DMZ Kubernetes Cluster                            │  │   │    │
│  │  │  │  ┌────────────┐  ┌────────────┐  ┌────────────┐        │  │   │    │
│  │  │  │  │  rkedmz1   │  │  rkedmz2   │  │  rkedmz3   │        │  │   │    │
│  │  │  │  │8CPU/16GB   │  │8CPU/16GB   │  │8CPU/16GB   │        │  │   │    │
│  │  │  │  │.200.10     │  │.200.11     │  │.200.12     │        │  │   │    │
│  │  │  │  └────────────┘  └────────────┘  └────────────┘        │  │   │    │
│  │  │  │                                                         │  │   │    │
│  │  │  │  Runs:                                                  │  │   │    │
│  │  │  │  - Gravitee API Gateway (DMZ - external-facing)        │  │   │    │
│  │  │  │  - Public APIs                                         │  │   │    │
│  │  │  └─────────────────────────────────────────────────────────┘  │   │    │
│  │  │                                                                │   │    │
│  │  │  ┌────────────┐  ┌────────────┐                              │   │    │
│  │  │  │  lbdmz1    │  │  lbdmz2    │  (HAProxy Load Balancers)    │   │    │
│  │  │  │4CPU/8GB    │  │4CPU/8GB    │                              │   │    │
│  │  │  │.200.30     │  │.200.31     │                              │   │    │
│  │  │  └────────────┘  └────────────┘                              │   │    │
│  │  └────────────────────────────────────────────────────────────────┘   │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                              │
│  Total: 42 VMs, 456 vCPUs, 912 GB RAM                                       │
└──────────────────────────────────────────────────────────────────────────────┘

                                     │
                                     │ Users access services
                                     ▼

┌─────────────────────────────────────────────────────────────────────────────────┐
│                                                                                  │
│                              END USERS                                           │
│                                                                                  │
│  Internal Users (LAN):                                                          │
│  - https://rancher.example.com        → Rancher management                      │
│  - https://argocd.example.com         → GitOps deployments                      │
│  - https://keycloak.example.com       → SSO login                               │
│  - https://minio.example.com          → Object storage                          │
│  - https://api.internal.example.com   → Gravitee API Gateway (LAN)              │
│  - https://monitoring.example.com     → Coroot observability                    │
│                                                                                  │
│  External Users (Internet):                                                     │
│  - https://api.example.com            → Gravitee API Gateway (DMZ)              │
│  - https://app.example.com            → Public applications                     │
│                                                                                  │
└─────────────────────────────────────────────────────────────────────────────────┘
```

---

## Summary: The Complete Picture

**This platform is:**

1. **A Virtual Machine Orchestrator**: Automatically calculates and provisions the right number of VMs based on user count
2. **A Kubernetes Deployment Engine**: Creates 3 production-ready Kubernetes clusters with all necessary components
3. **A Middleware Installer**: Deploys Kafka, Keycloak, MinIO, and other services
4. **A Security Framework**: Implements Vault, NeuVector, TLS encryption, and network segmentation
5. **A Monitoring Platform**: Installs Coroot for observability
6. **A Multi-Hypervisor Solution**: Works seamlessly with both VMware vSphere and Nutanix AHV

**The harmo-base Docker image** is the foundation that makes everything possible by providing:
- All required CLI tools (kubectl, helm, terraform, govc, mc, rke2)
- Both Python 3.7 (for Informix) and Python 3.12 (for FastAPI/Ansible)
- IBM Informix Client SDK for legacy database integration
- Ansible automation engine
- All necessary system libraries and dependencies

**The result:**
A fully automated datacenter-in-a-box that transforms weeks of manual DevOps work into hours of automated deployment, with complete configurability and database-driven architecture.

---

**END OF DOCUMENTATION**

*Total Word Count: ~35,000 words*
*Reading Time: 2-3 hours for complete understanding*
*Target Audience: Everyone from non-technical stakeholders to expert DevOps engineers*