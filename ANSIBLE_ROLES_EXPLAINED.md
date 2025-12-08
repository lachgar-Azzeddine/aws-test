# Ansible Roles - Complete Explanation

**Purpose:** This guide explains what each Ansible role does, what it installs, and why it's needed.

**Total Roles:** 31 roles

---

## 📋 Role Execution Order

Roles execute in this sequence (as defined in `backend/install.py`):

```
Phase 1: VM Provisioning
  1. provisionnement-vms-infra
  2. provisionnement-vms-apps
  3. provisionnement-vms-dmz

Phase 2: VM Preparation
  4. prepare-vms

Phase 3: Infrastructure Services
  5. install-vault
  6. install-docker-registry
  7. install-gogs

Phase 4: Kubernetes Clusters
  8. install-rke2-apps
  9. install-rke2-middleware
  10. install-rke2-dmz

Phase 5: Kubernetes Tools
  11. install-cert-manager
  12. install-longhorn
  13. setup-vault-injector
  14. install-argocd

Phase 6: Networking & Load Balancers
  15. install-load-balancer
  16. install-bastion

Phase 7: Monitoring & Security
  17. install-monitoring
  18. install-neuvector
  19. install-rancher-server

Phase 8: Middleware & Applications
  20. install-kafka
  21. install-keycloak
  22. install-minio
  23. install-minio-backup
  24. install-informix
  25. install-n8n
  26. install-seald
  27. install-gravitee-lan
  28. install-gravitee-dmz
```

---

## 🏗️ Roles by Category

---

## 1️⃣ VM Provisioning Roles (Phase 1)

These roles create VMs on your hypervisor (VMware/Nutanix).

---

### `provisionnement-vms-infra`

**Purpose:** Creates infrastructure VMs (core services)

**VMs Created:**
- Vault VM (secrets management)
- GitOps VM (Gogs + Docker Registry)
- Monitoring VM (Coroot)

**Zone:** LAN_INFRA

**What it does:**
- Connects to VMware vCenter or Nutanix Prism Central
- Creates VMs based on vm_configurations table
- Assigns IPs from LAN_INFRA zone pool
- Configures CPU, RAM, disk sizes
- Enables cloud-init with temporary password

**Technologies:** Python (pyvmomi for VMware, REST API for Nutanix)

**Dependencies:** None (runs first)

---

### `provisionnement-vms-apps`

**Purpose:** Creates application Kubernetes cluster VMs

**VMs Created:**
- RKEAPPS master nodes (3 VMs)
- RKEAPPS worker nodes (0-N VMs based on user count)
- RKEAPPS CNS nodes (Container-Native Storage)

**Zone:** LAN_APPS

**What it does:**
- Creates VMs for the main application Kubernetes cluster
- This cluster will host business applications
- Assigns IPs from LAN_APPS zone pool

**Technologies:** Same as provisionnement-vms-infra

**Dependencies:** None (parallel with provisionnement-vms-infra)

---

### `provisionnement-vms-dmz`

**Purpose:** Creates DMZ Kubernetes cluster VMs

**VMs Created:**
- RKEDMZ nodes (3 VMs - combined master/worker/cns)
- LBDMZ load balancer nodes (2 VMs)

**Zone:** DMZ

**What it does:**
- Creates VMs for DMZ (internet-facing) cluster
- This cluster hosts externally accessible services
- Assigns IPs from DMZ zone pool

**Technologies:** Same as provisionnement-vms-infra

**Dependencies:** None (parallel with other provisioning roles)

---

## 2️⃣ VM Preparation Roles (Phase 2)

---

### `prepare-vms`

**Purpose:** Prepares ALL VMs for use (security & SSH setup)

**Target VMs:** ALL VMs (every VM provisioned in Phase 1)

**What it does:**

1. **SSH Key Authentication Setup:**
   - Connects using temporary password (devops/devops)
   - Copies SSH public key from database to VM
   - Adds key to `/home/devops/.ssh/authorized_keys`

2. **Security Hardening:**
   - Disables password authentication in `/etc/ssh/sshd_config`
   - Sets `PasswordAuthentication no`
   - Restarts SSH service
   - From now on, only SSH keys work

3. **System Preparation:**
   - Creates devops user (if not exists)
   - Sets up sudo permissions
   - Installs Python3 (for Ansible)
   - Updates system packages
   - Configures hostname

4. **Firewall Configuration:**
   - Opens necessary ports based on VM role
   - Examples:
     - Vault: 8200
     - Registry: 8443, 5000
     - RKE2: 6443, 9345, 10250

**Technologies:** Ansible (copy, lineinfile, service modules)

**Dependencies:** VMs must exist (Phase 1 complete)

**Critical:** This must run before ANY other installation role!

---

## 3️⃣ Infrastructure Services (Phase 3)

Core platform services that run on dedicated VMs (not in Kubernetes).

---

### `install-vault`

**Purpose:** Install and configure HashiCorp Vault (secrets management)

**Target VM:** vault1 (LAN_INFRA zone)

**What it does:**

1. **Install Vault:**
   - Downloads Vault binary
   - Creates systemd service
   - Configures Vault to use TLS (HTTPS)

2. **Initialize Vault:**
   - Generates 5 unseal keys
   - Generates root token
   - Stores keys and token in database (`vault_keys`, `vault_token` tables)

3. **Unseal Vault:**
   - Uses 3 of 5 keys to unseal Vault
   - Enables KV v2 secrets engine at path `harmonisation/`

4. **Store Initial Secrets:**
   - Stores credentials for all services:
     - Gogs: devops/devops
     - Registry: devops/devops
     - MinIO: devops/aq9rj9R1
     - Keycloak: admin_user/Admin_Password
     - ArgoCD: admin/admin
     - Rancher: devops/devops
     - Database credentials from database

**Why it's needed:** Centralized secrets management for all services

**Technologies:** HashiCorp Vault, Python (hvac library)

**Post-Install:** `post_install.py` script runs to initialize Vault

**Dependencies:** prepare-vms

---

### `install-docker-registry`

**Purpose:** Install private Docker container registry

**Target VM:** gitops1 (LAN_INFRA zone)

**What it does:**

1. **Install Docker:**
   - Installs Docker CE
   - Starts Docker service

2. **Install Registry:**
   - Runs Docker Registry v2 as container
   - Exposes on port 8443 (HTTPS) and 5000 (HTTP)
   - Configures TLS certificates from database

3. **Authentication:**
   - Sets up basic auth (username: devops, password: devops)
   - Stores credentials in Vault

4. **Storage:**
   - Uses `/var/lib/registry` for image storage
   - Mounts data disk for persistence

**Why it's needed:**
- Stores container images locally
- Air-gapped deployments don't need internet
- Faster image pulls (local network)

**Technologies:** Docker, Docker Registry

**URL:** `https://{prefix}registry.{domain}:8443`

**Dependencies:** prepare-vms, install-vault

---

### `install-gogs`

**Purpose:** Install Gogs (lightweight Git server)

**Target VM:** gitops1 (same VM as Docker Registry)

**What it does:**

1. **Install Gogs:**
   - Downloads Gogs binary
   - Creates systemd service
   - Configures SQLite database (embedded)

2. **Configuration:**
   - Sets up base domain from database
   - Configures SSH access on port 3000
   - Enables private repositories

3. **Initial Setup:**
   - Creates admin user: devops/devops
   - Stores credentials in Vault
   - Creates initial repository for GitOps

**Why it's needed:**
- Stores Kubernetes manifests
- ArgoCD syncs from Gogs repositories
- Infrastructure as Code storage

**Technologies:** Gogs (Go-based Git server)

**URL:** `https://{prefix}gogs.{domain}`

**Dependencies:** prepare-vms, install-vault

---

## 4️⃣ Kubernetes Clusters (Phase 4)

Install RKE2 (Rancher Kubernetes Engine) clusters.

---

### `install-rke2-apps`

**Purpose:** Install Kubernetes cluster for business applications

**Target VMs:**
- rkeapp-master1, rkeapp-master2, rkeapp-master3 (control plane)
- rkeapp-worker1, rkeapp-worker2, ... (worker nodes)

**Cluster Name:** RKE2-APPS

**What it does:**

1. **Install RKE2 on Masters:**
   - Downloads RKE2 artifacts (offline installation)
   - Installs first master (creates cluster)
   - Joins additional masters (HA control plane)
   - Generates kubeconfig

2. **Install RKE2 on Workers:**
   - Downloads RKE2 artifacts
   - Joins workers to cluster using token

3. **Configure Networking:**
   - Sets up Calico CNI (pod networking)
   - Configures cluster CIDR (pod IPs)
   - Configures service CIDR (service IPs)

4. **Configure Registry:**
   - Points to private Docker registry
   - Configures authentication

5. **Generate kubeconfig:**
   - Stores in `/home/devops/.kube/config.yaml`
   - Used by kubectl for cluster access

**Why it's needed:** Main cluster for deploying business applications

**Technologies:** RKE2, Kubernetes, Calico

**Dependencies:** prepare-vms, install-docker-registry

---

### `install-rke2-middleware`

**Purpose:** Install Kubernetes cluster for middleware services

**Target VMs:**
- rkemiddleware-master1, rkemiddleware-master2, rkemiddleware-master3
- rkemiddleware-worker1, ... (if any)

**Cluster Name:** RKE2-MIDDLEWARE

**What it does:**
- Same as install-rke2-apps but for a separate cluster
- Hosts middleware: Kafka, Keycloak, MinIO

**Why it's needed:**
- Separation of concerns (apps vs middleware)
- Independent scaling
- Security isolation

**Technologies:** RKE2, Kubernetes, Calico

**Dependencies:** prepare-vms, install-docker-registry

---

### `install-rke2-dmz`

**Purpose:** Install Kubernetes cluster for DMZ (internet-facing services)

**Target VMs:**
- rkedmz1, rkedmz2, rkedmz3 (combined master/worker)

**Cluster Name:** RKE2-DMZ

**What it does:**
- Same as install-rke2-apps but for DMZ zone
- Hosts API gateways (Gravitee) for external access

**Why it's needed:**
- Security isolation (DMZ separate from internal LAN)
- Internet-facing services isolated

**Technologies:** RKE2, Kubernetes, Calico

**Dependencies:** prepare-vms, install-docker-registry

---

## 5️⃣ Kubernetes Tools (Phase 5)

Tools that run ON the Kubernetes clusters.

---

### `install-cert-manager`

**Purpose:** Install cert-manager (TLS certificate management)

**Target Cluster:** RKE2-APPS (can also install on MIDDLEWARE and DMZ)

**What it does:**

1. **Install cert-manager:**
   - Deploys cert-manager CRDs (Custom Resource Definitions)
   - Deploys cert-manager controllers
   - Runs in `cert-manager` namespace

2. **Configure Issuers:**
   - Creates self-signed ClusterIssuer (for testing)
   - Can configure Let's Encrypt (for production)

**Why it's needed:**
- Automatically generates TLS certificates for services
- Manages certificate renewals
- Required for HTTPS ingresses

**Technologies:** cert-manager (Kubernetes operator)

**Dependencies:** install-rke2-apps

---

### `install-longhorn`

**Purpose:** Install Longhorn (distributed block storage)

**Target Cluster:** RKE2-APPS (also on MIDDLEWARE)

**What it does:**

1. **Install Longhorn:**
   - Deploys Longhorn components (manager, driver, UI)
   - Creates StorageClass: `longhorn`

2. **Configure Storage:**
   - Uses `/var/lib/longhorn` on each node
   - Replicates data across 3 nodes (default)
   - Provides PersistentVolumes for applications

**Why it's needed:**
- Persistent storage for stateful applications
- Database storage (PostgreSQL, MongoDB, etc.)
- Replication for high availability

**Technologies:** Longhorn (CNCF project)

**Dependencies:** install-rke2-apps

---

### `setup-vault-injector`

**Purpose:** Install Vault Agent Injector (secrets injection into pods)

**Target Cluster:** RKE2-APPS

**What it does:**

1. **Install Vault Agent:**
   - Deploys Vault Agent as sidecar injector
   - Configures connection to Vault VM

2. **Enable Kubernetes Auth:**
   - Configures Vault to trust Kubernetes service accounts
   - Allows pods to authenticate to Vault

3. **Inject Secrets:**
   - Automatically injects secrets from Vault into pod filesystems
   - Applications read secrets from files (not environment variables)

**Why it's needed:**
- Secure secrets management (no secrets in pod specs)
- Dynamic secret rotation
- Audit trail of secret access

**Technologies:** Vault Agent, Kubernetes admission controller

**Dependencies:** install-rke2-apps, install-vault, install-longhorn

---

### `install-argocd`

**Purpose:** Install ArgoCD (GitOps continuous deployment)

**Target Cluster:** RKE2-APPS (can deploy to all clusters)

**What it does:**

1. **Install ArgoCD:**
   - Deploys ArgoCD controllers
   - Deploys ArgoCD UI
   - Runs in `argocd` namespace

2. **Configure Repository Connection:**
   - Connects to Gogs repository
   - Authenticates with credentials from Vault

3. **Create Initial Applications:**
   - Sets up application definitions
   - Syncs from Git to Kubernetes

**Why it's needed:**
- GitOps workflow (Git as source of truth)
- Automated application deployment
- Rollback capabilities

**Technologies:** ArgoCD (CNCF project)

**URL:** `https://{prefix}argocd.{domain}`

**Dependencies:** install-rke2-apps, install-gogs, install-vault

---

## 6️⃣ Networking & Load Balancers (Phase 6)

---

### `install-load-balancer`

**Purpose:** Install HAProxy load balancers

**Target VMs:**
- lblan1, lblan2 (load balancers for LAN_APPS)
- lbdmz1, lbdmz2 (load balancers for DMZ)
- lbintegration1, lbintegration2 (load balancers for integrations)

**What it does:**

1. **Install HAProxy:**
   - Installs HAProxy
   - Configures systemd service

2. **Configure Backends:**
   - LAN load balancers: Point to RKE2-APPS masters
   - DMZ load balancers: Point to RKE2-DMZ nodes
   - Configures health checks

3. **Configure Virtual IPs:**
   - Sets up Keepalived for HA
   - Floating VIP between 2 load balancers

**Why it's needed:**
- High availability (if one LB fails, VIP moves to other)
- Load distribution across Kubernetes nodes
- Single entry point for applications

**Technologies:** HAProxy, Keepalived

**Dependencies:** prepare-vms, install-rke2-apps

---

### `install-bastion`

**Purpose:** Install bastion/jump host for secure SSH access

**Target VM:** Bastion VM (if exists)

**What it does:**

1. **Configure SSH:**
   - Sets up SSH bastion configuration
   - Configures port forwarding
   - Logs all SSH sessions

2. **Security:**
   - Disables direct SSH to other VMs
   - Forces all SSH through bastion

**Why it's needed:**
- Security best practice
- Audit trail of SSH access
- Single point of access control

**Technologies:** OpenSSH, auditd

**Dependencies:** prepare-vms

---

## 7️⃣ Monitoring & Security (Phase 7)

---

### `install-monitoring`

**Purpose:** Install Coroot monitoring stack

**Target VM:** monitoring1 (LAN_INFRA zone)

**What it does:**

1. **Install Coroot:**
   - Installs Coroot (observability platform)
   - Installs ClickHouse (metrics database)
   - Installs Prometheus (metrics collection)
   - Installs Grafana (visualization)

2. **Configure Data Collection:**
   - Scrapes metrics from all Kubernetes clusters
   - Collects logs from all VMs
   - Monitors system resources

3. **Setup Dashboards:**
   - Pre-configured dashboards for Kubernetes
   - Application performance monitoring
   - Infrastructure health

**Why it's needed:**
- Observability (metrics, logs, traces)
- Troubleshooting
- Capacity planning
- Alerting

**Technologies:** Coroot, Prometheus, Grafana, ClickHouse

**URL:** `https://{prefix}coroot.{domain}`

**Dependencies:** prepare-vms, install-rke2-apps

---

### `install-neuvector`

**Purpose:** Install NeuVector (container security)

**Target Cluster:** RKE2-APPS

**What it does:**

1. **Install NeuVector:**
   - Deploys NeuVector controllers
   - Deploys NeuVector enforcers (on every node)
   - Runs in `neuvector` namespace

2. **Configure Security Policies:**
   - Network segmentation policies
   - Runtime security rules
   - Vulnerability scanning

3. **Enable Monitoring:**
   - Monitors container behavior
   - Detects anomalies
   - Blocks suspicious activities

**Why it's needed:**
- Container runtime security
- Network policy enforcement
- Vulnerability scanning
- Compliance reporting

**Technologies:** NeuVector (SUSE)

**URL:** `https://{prefix}neuvector.{domain}`

**Dependencies:** install-rke2-apps, install-longhorn

---

### `install-rancher-server`

**Purpose:** Install Rancher (Kubernetes management UI)

**Target Cluster:** RKE2-APPS

**What it does:**

1. **Install Rancher:**
   - Deploys Rancher server
   - Runs in `cattle-system` namespace

2. **Import Clusters:**
   - Imports RKE2-APPS cluster
   - Imports RKE2-MIDDLEWARE cluster
   - Imports RKE2-DMZ cluster

3. **Setup Authentication:**
   - Configures admin user (devops/devops)
   - Stores credentials in Vault

**Why it's needed:**
- Central management of multiple Kubernetes clusters
- User-friendly UI for Kubernetes
- RBAC management
- Cluster monitoring

**Technologies:** Rancher (SUSE)

**URL:** `https://{prefix}rancher.{domain}`

**Dependencies:** install-rke2-apps, install-vault, install-cert-manager

---

## 8️⃣ Middleware & Applications (Phase 8)

Applications and middleware services.

---

### `install-kafka`

**Purpose:** Install Apache Kafka (message broker)

**Target Cluster:** RKE2-MIDDLEWARE

**What it does:**

1. **Install Kafka:**
   - Deploys Kafka brokers (3 replicas)
   - Deploys Zookeeper (3 replicas)
   - Uses Longhorn for persistent storage

2. **Configure Topics:**
   - Creates initial topics
   - Configures retention policies

3. **Expose Service:**
   - Internal: kafka.middleware.svc.cluster.local:9092
   - External: kafka.{domain}:9092

**Why it's needed:**
- Event streaming
- Microservices communication
- Asynchronous messaging

**Technologies:** Apache Kafka, Zookeeper

**Dependencies:** install-rke2-middleware, install-longhorn

---

### `install-keycloak`

**Purpose:** Install Keycloak (identity and access management)

**Target Cluster:** RKE2-MIDDLEWARE

**What it does:**

1. **Install Keycloak:**
   - Deploys Keycloak server
   - Uses PostgreSQL for database (deployed with Keycloak)

2. **Configure Realms:**
   - Creates application realm
   - Configures clients (applications)

3. **LDAP Integration:**
   - Connects to LDAP from database config
   - Syncs users from LDAP

4. **SSO Setup:**
   - Configures SAML/OIDC
   - Enables single sign-on for all applications

**Why it's needed:**
- Single sign-on (SSO)
- User authentication
- Authorization (RBAC)
- LDAP/AD integration

**Technologies:** Keycloak, PostgreSQL

**URL:** `https://{prefix}keycloak.{domain}`

**Dependencies:** install-rke2-middleware, install-longhorn, install-vault

---

### `install-minio`

**Purpose:** Install MinIO (S3-compatible object storage)

**Target Cluster:** RKE2-MIDDLEWARE

**What it does:**

1. **Install MinIO:**
   - Deploys MinIO servers (distributed mode, 4 nodes)
   - Uses Longhorn for persistent storage

2. **Create Buckets:**
   - Creates initial buckets for applications
   - Configures access policies

3. **Setup Credentials:**
   - Admin credentials: devops/aq9rj9R1
   - Stores in Vault

**Why it's needed:**
- Object storage for applications
- File uploads (images, documents)
- Backup storage
- S3-compatible API

**Technologies:** MinIO

**URL:** `https://{prefix}minio.{domain}`

**Dependencies:** install-rke2-middleware, install-longhorn, install-vault

---

### `install-minio-backup`

**Purpose:** Configure MinIO backup to external storage

**Target:** MinIO cluster (RKE2-MIDDLEWARE)

**What it does:**

1. **Setup Backup Jobs:**
   - Creates CronJob for scheduled backups
   - Backs up MinIO data to external location

2. **Configure Retention:**
   - Keeps backups for N days
   - Rotates old backups

**Why it's needed:**
- Data protection
- Disaster recovery

**Technologies:** MinIO mc (client), Kubernetes CronJob

**Dependencies:** install-minio

---

### `install-informix`

**Purpose:** Install IBM Informix database

**Target VM:** Database VM (if required)

**What it does:**

1. **Install Informix:**
   - Installs Informix database server
   - Configures storage spaces

2. **Create Databases:**
   - Creates application databases
   - Creates users with proper permissions

3. **Configure Connectivity:**
   - Exposes on port 2034
   - Stores credentials in Vault

**Why it's needed:**
- Legacy application requirement
- Database for business applications

**Technologies:** IBM Informix

**Dependencies:** prepare-vms, install-vault

---

### `install-n8n`

**Purpose:** Install n8n (workflow automation)

**Target Cluster:** RKE2-APPS

**What it does:**

1. **Install n8n:**
   - Deploys n8n server
   - Uses PostgreSQL for workflow storage

2. **Configure Integrations:**
   - Connects to Vault for credentials
   - Configures webhooks

**Why it's needed:**
- Workflow automation
- Integration between systems
- No-code automation

**Technologies:** n8n

**URL:** `https://{prefix}n8n.{domain}`

**Dependencies:** install-rke2-apps, install-longhorn, install-vault

---

### `install-seald`

**Purpose:** Install Seald (end-to-end encryption SDK)

**Target Cluster:** RKE2-APPS

**What it does:**

1. **Install Seald:**
   - Deploys Seald server
   - Configures encryption keys

2. **Setup SDK:**
   - Provides encryption/decryption APIs
   - Integrates with applications

**Why it's needed:**
- End-to-end encryption for sensitive data
- Secure file sharing
- Encryption SDK for applications

**Technologies:** Seald

**URL:** `https://{prefix}seald.{domain}`

**Dependencies:** install-rke2-apps, install-longhorn, install-vault

---

### `install-gravitee-lan`

**Purpose:** Install Gravitee API Gateway (LAN - internal APIs)

**Target Cluster:** RKE2-APPS

**What it does:**

1. **Install Gravitee:**
   - Deploys Gravitee API Gateway
   - Deploys Gravitee Management UI
   - Uses MongoDB and Elasticsearch

2. **Configure APIs:**
   - Sets up internal API routes
   - Configures authentication (Keycloak)
   - Enables rate limiting

3. **Setup Portal:**
   - Developer portal for API documentation
   - API key management

**Why it's needed:**
- API management for internal services
- Rate limiting, throttling
- API analytics
- Security policies

**Technologies:** Gravitee, MongoDB, Elasticsearch

**URL:** `https://{prefix}gravitee-lan.{domain}`

**Dependencies:** install-rke2-apps, install-longhorn, install-keycloak, install-vault

---

### `install-gravitee-dmz`

**Purpose:** Install Gravitee API Gateway (DMZ - external APIs)

**Target Cluster:** RKE2-DMZ

**What it does:**
- Same as install-gravitee-lan but for DMZ cluster
- Exposes APIs to external users (internet)

**Why it's needed:**
- API management for external-facing APIs
- Security for public APIs
- DDoS protection

**Technologies:** Gravitee, MongoDB, Elasticsearch

**URL:** `https://{prefix}gravitee-dmz.{domain}`

**Dependencies:** install-rke2-dmz, install-longhorn, install-keycloak, install-vault

---

## 🧪 Test Roles

---

### `testrole`

**Purpose:** Test role for development/debugging

**What it does:**
- Simple role to test Ansible execution
- Prints "Hello World"
- Used to verify Ansible Runner works

**Dependencies:** None

---

### `testrolefailed`

**Purpose:** Test role that intentionally fails

**What it does:**
- Fails with exit code 1
- Tests error handling in install.py

**Dependencies:** None

---

## 📊 Role Summary Table

| Role | Phase | Target | Purpose | Critical? |
|------|-------|--------|---------|-----------|
| **provisionnement-vms-infra** | 1 | Hypervisor | Create INFRA VMs | ✅ Yes |
| **provisionnement-vms-apps** | 1 | Hypervisor | Create APPS VMs | ✅ Yes |
| **provisionnement-vms-dmz** | 1 | Hypervisor | Create DMZ VMs | ⚠️ Optional (no DMZ) |
| **prepare-vms** | 2 | All VMs | SSH setup, security | ✅ Yes |
| **install-vault** | 3 | vault1 | Secrets management | ✅ Yes |
| **install-docker-registry** | 3 | gitops1 | Container registry | ✅ Yes |
| **install-gogs** | 3 | gitops1 | Git server | ✅ Yes |
| **install-rke2-apps** | 4 | RKEAPPS VMs | Main K8s cluster | ✅ Yes |
| **install-rke2-middleware** | 4 | RKEMIDDLEWARE VMs | Middleware K8s cluster | ⚠️ Optional |
| **install-rke2-dmz** | 4 | RKEDMZ VMs | DMZ K8s cluster | ⚠️ Optional (no DMZ) |
| **install-cert-manager** | 5 | K8s Cluster | TLS certificates | ✅ Yes |
| **install-longhorn** | 5 | K8s Cluster | Persistent storage | ✅ Yes |
| **setup-vault-injector** | 5 | K8s Cluster | Inject secrets to pods | ✅ Yes |
| **install-argocd** | 5 | K8s Cluster | GitOps deployment | ✅ Yes |
| **install-load-balancer** | 6 | LB VMs | HAProxy LBs | ⚠️ Optional |
| **install-bastion** | 6 | Bastion VM | SSH jump host | ⚠️ Optional |
| **install-monitoring** | 7 | monitoring1 | Observability | ⚠️ Recommended |
| **install-neuvector** | 7 | K8s Cluster | Container security | ⚠️ Recommended |
| **install-rancher-server** | 7 | K8s Cluster | K8s management UI | ⚠️ Optional |
| **install-kafka** | 8 | K8s Middleware | Message broker | ⚠️ App-specific |
| **install-keycloak** | 8 | K8s Middleware | IAM/SSO | ⚠️ App-specific |
| **install-minio** | 8 | K8s Middleware | Object storage | ⚠️ App-specific |
| **install-minio-backup** | 8 | K8s Middleware | MinIO backups | ⚠️ Optional |
| **install-informix** | 8 | DB VM | Informix database | ⚠️ App-specific |
| **install-n8n** | 8 | K8s Apps | Workflow automation | ⚠️ Optional |
| **install-seald** | 8 | K8s Apps | E2E encryption | ⚠️ App-specific |
| **install-gravitee-lan** | 8 | K8s Apps | API gateway (internal) | ⚠️ App-specific |
| **install-gravitee-dmz** | 8 | K8s DMZ | API gateway (external) | ⚠️ App-specific |

**Legend:**
- ✅ **Critical:** Required for basic platform functionality
- ⚠️ **Optional:** Can be skipped for minimal setup
- ⚠️ **App-specific:** Only needed if using specific applications

---

## 🎯 Minimal Setup (5 VMs)

For testing with minimal resources, you only need:

**Essential Roles (10 roles):**
1. provisionnement-vms-infra
2. provisionnement-vms-apps
3. prepare-vms
4. install-vault
5. install-docker-registry
6. install-gogs
7. install-rke2-apps
8. install-cert-manager
9. install-longhorn
10. setup-vault-injector

**Optional but Recommended:**
11. install-argocd
12. install-monitoring

**Skip for Minimal:**
- All middleware roles (Kafka, Keycloak, MinIO)
- DMZ roles (no DMZ VMs)
- Load balancers (direct access to VMs)
- Gravitee (API gateway not essential)
- NeuVector (security nice-to-have)
- Rancher (can use kubectl)

---

## 🔄 Execution Flow Example

**Full deployment sequence:**

```
1. provisionnement-vms-infra → Creates vault1, gitops1, monitoring1
2. provisionnement-vms-apps → Creates rkeapp-master1,2,3 + workers
3. provisionnement-vms-dmz → Creates rkedmz1,2,3 + lbdmz1,2
   ↓
4. prepare-vms → Sets up SSH keys on ALL VMs
   ↓
5. install-vault → vault1: Install Vault, initialize, store secrets
6. install-docker-registry → gitops1: Install Docker Registry
7. install-gogs → gitops1: Install Git server
   ↓
8. install-rke2-apps → RKE2-APPS: Create K8s cluster on APPS VMs
9. install-rke2-middleware → RKE2-MIDDLEWARE: Create K8s cluster
10. install-rke2-dmz → RKE2-DMZ: Create K8s cluster on DMZ VMs
   ↓
11. install-cert-manager → RKE2-APPS: TLS certificate management
12. install-longhorn → RKE2-APPS: Persistent storage
13. setup-vault-injector → RKE2-APPS: Vault secrets injection
14. install-argocd → RKE2-APPS: GitOps deployment tool
   ↓
15. install-load-balancer → lblan1,2, lbdmz1,2: HAProxy LBs
16. install-bastion → bastion1: SSH jump host
   ↓
17. install-monitoring → monitoring1: Coroot observability
18. install-neuvector → RKE2-APPS: Container security
19. install-rancher-server → RKE2-APPS: K8s management UI
   ↓
20. install-kafka → RKE2-MIDDLEWARE: Message broker
21. install-keycloak → RKE2-MIDDLEWARE: SSO/IAM
22. install-minio → RKE2-MIDDLEWARE: Object storage
23. install-gravitee-lan → RKE2-APPS: Internal API gateway
24. install-gravitee-dmz → RKE2-DMZ: External API gateway
```

**Each role:**
- Queries database via `prepare_inputs.py`
- Gets variables (IPs, credentials, configs)
- Runs Ansible tasks
- Updates database with results

---

## 📚 Summary

**Total: 31 roles**

**Categories:**
- **3** VM provisioning roles (create VMs on hypervisor)
- **1** VM preparation role (SSH setup)
- **3** Infrastructure services (Vault, Registry, Gogs)
- **3** Kubernetes clusters (APPS, MIDDLEWARE, DMZ)
- **4** Kubernetes tools (cert-manager, Longhorn, Vault injector, ArgoCD)
- **2** Networking (load balancers, bastion)
- **3** Monitoring & security (Coroot, NeuVector, Rancher)
- **10** Middleware & applications (Kafka, Keycloak, MinIO, etc.)
- **2** Test roles

**Key Points:**
- Each role is independent and modular
- All roles query database for configuration (database-driven)
- Roles can be skipped for minimal setups
- Order matters (dependencies must run first)
- All roles are generic (no client-specific code after cleanup)

This is your complete platform deployment workflow! 🎉
