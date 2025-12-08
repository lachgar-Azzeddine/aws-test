# Deployed Platform Architecture

This document provides a detailed overview of the architecture of the platform deployed by this project. The platform is a complex system composed of multiple layers, including infrastructure, middleware, and applications, all managed and deployed through a centralized automation engine.

## 1. Overall Architecture

The deployed architecture is a comprehensive, on-premises, microservices-based platform built on Kubernetes. It is designed to be highly available, secure, and scalable, providing a full stack of middleware and services to run modern applications.

The architecture is deployed on a hypervisor (VMware or Nutanix) and is segmented into multiple network zones for security and isolation. It leverages **Kubernetes (RKE2)** for container orchestration, **Rancher** for cluster management, and a wide range of popular open-source middleware to support the deployed applications. The entire platform is managed using a GitOps approach with **Argo CD** and **Gogs**.

The deployment process is fully automated and follows a specific sequence to ensure a consistent and reliable setup.

## 2. Deployment Process

The deployment process is orchestrated by a series of Ansible roles, executed in a specific order to build the platform from the ground up. The sequence is as follows:

1. **VM Provisioning**: The process starts by provisioning the necessary virtual machines on the configured hypervisor (VMware or Nutanix) for both the infrastructure and application layers (`provisionnement-vms-infra`, `provisionnement-vms-apps`).

2. **VM Preparation**: Once the VMs are created, they are prepared with the necessary base configuration, including user accounts, SSH access, and network settings (`prepare-vms`).

3. **Core Infrastructure Services Installation**: Essential services that live outside of Kubernetes are installed. This includes:
   - **Docker Registry** (`install-docker-registry`): A private registry to store all the container images required for the platform.
   - **HashiCorp Vault** (`install-vault`): For centralized secrets management.
   - **HAProxy Load Balancer** (`install-load-balancer`): To manage and distribute traffic to the various services.
   - **Gogs** (`install-gogs`): A self-hosted Git service that acts as the source of truth for the GitOps workflow.

4. **Kubernetes Cluster Installation**: Three separate Kubernetes clusters are installed and configured using **Rancher Kubernetes Engine 2 (RKE2)**:
   - `install-rke2-apps`: The cluster dedicated to running the main business applications.
   - `install-rke2-middleware`: The cluster for running all the supporting middleware.
   - `install-rke2-dmz`: The cluster deployed in the DMZ zone, running the Gravitee API Gateway for DMZ traffic.
   - **Rancher** (`install-rancher-server`) is also installed to provide a management plane for ALL three Kubernetes clusters (RKE2-APPS, RKE2-MIDDLEWARE, RKE2-DMZ).

5. **Kubernetes Cluster Foundation Setup**: With the clusters up and running, foundational components are deployed on both clusters to enable storage, security, and GitOps:
   - **Argo CD** (`install-argocd`): The GitOps continuous delivery tool that will manage all subsequent deployments on the clusters.
   - **Cert-manager** (`install-cert-manager`): For automated TLS certificate management within the clusters.
   - **Longhorn** (`install-longhorn`): A distributed block storage solution for persistent data.
   - **Vault Injector** (`setup-vault-injector`): To automatically inject secrets from Vault into application pods.

6. **Application Middleware Deployment (on Middleware Cluster)**: A suite of middleware is deployed on the `RKE2-MIDDLEWARE` cluster to support the applications:
   - **MinIO** (`install-minio`): An S3-compatible object storage service.
   - **Keycloak** (`install-keycloak`): For identity and access management (IAM).
   - **Apache Kafka** (`install-kafka`): A distributed streaming platform for messaging.
   - **n8n** (`install-n8n`): A workflow automation tool.
   - **Flowable** (`install-flowable`): A business process management (BPM) engine, deployed if the "eServices" product is selected.

7. **API Management Deployment**:
   - **Gravitee LAN** (`install-gravitee-lan`): An API management platform is deployed in the `RKE2-APPS` cluster to manage and secure internal APIs.
   - **Gravitee DMZ** (`install-gravitee-dmz`): An API management platform is deployed in the `RKE2-DMZ` cluster to manage and secure API traffic from external users and mobile applications.

8. **Security and Monitoring Deployment**:
   - **Neuvector** (`install-neuvector`): A container security platform.
   - **Coroot** (`install-monitoring`): A monitoring and observability tool to provide insights into the platform's health and performance.

9. **Application Deployment**: Finally, the business applications are deployed onto the `RKE2-APPS` cluster:
   - **eServices Microservices** (`install-eservices`)
   - **GCO** (`install-gco`)

## 3. Components Deployed

The platform is composed of several components, which can be categorized into the following layers:

### 3.1. Infrastructure Layer

- **Hypervisor:** The platform is deployed on either:
  - **VMware vSphere/ESXi**
  - **Nutanix AHV**
- **Virtual Machines:** Linux-based virtual machines are provisioned for different roles:
  - Kubernetes master and worker nodes (for both middleware and applications).
  - Infrastructure services nodes (e.g., for Docker Registry, Vault).
- **Networking:**
  - **VLANs:** The platform uses VLANs to segment the network into different zones (LAN Apps, LAN Infra, DMZ).
  - **Subnets and IP Addressing:** Each zone has its own subnet and IP address range.
  - **DNS:** The platform manages internal DNS records for the deployed services.
  - **Load Balancer:** A load balancer is deployed to distribute traffic to the Kubernetes cluster and other services.

### 3.2. Middleware Layer

The middleware layer provides the core services required for the applications to run. Most of these components are deployed on the Kubernetes cluster.

- **Container Orchestration:**
  - **Rancher Kubernetes Engine 2 (RKE2):** A certified Kubernetes distribution. Three separate RKE2 clusters are deployed:
    - **RKE2-APPS:** Cluster for running business applications (eServices, GCO).
    - **RKE2-MIDDLEWARE:** Cluster for running supporting middleware services.
    - **RKE2-DMZ:** Cluster in the DMZ zone running the Gravitee API Gateway.
  - **Rancher:** A management plane for all three Kubernetes clusters (RKE2-APPS, RKE2-MIDDLEWARE, RKE2-DMZ), providing unified cluster management, monitoring, and operations.
- **Storage:**
  - **Longhorn:** A distributed block storage system for Kubernetes, providing persistent storage for stateful applications.
  - **MinIO:** An S3-compatible object storage service, used for general-purpose storage and backups.
- **Security:**
  - **HashiCorp Vault:** For centralized secrets management. It stores credentials, certificates, and other sensitive data.
  - **Vault Injector:** A component that automatically injects secrets from Vault into Kubernetes pods.
  - **Cert-manager:** For automated management and issuance of TLS certificates within Kubernetes.
  - **Neuvector:** A container security platform providing vulnerability scanning, runtime protection, and network segmentation.
  - **Keycloak:** An identity and access management (IAM) solution for securing applications and services with single sign-on (SSO).
- **Messaging and Integration:**
  - **Apache Kafka:** A distributed streaming platform for building real-time data pipelines and streaming apps.
  - **n8n:** A workflow automation tool to connect different services and create complex workflows.
- **API Management:**
  - **Gravitee:** An API management platform to design, secure, and manage APIs. Two instances are deployed:
    - **Gravitee LAN:** Deployed in the RKE2-APPS cluster for managing internal API traffic.
    - **Gravitee DMZ:** Deployed in the RKE2-DMZ cluster (DMZ zone) to secure and manage API traffic from external users and mobile applications. API calls are then proxied to the RKE2-MIDDLEWARE cluster via the LB LAN.
- **CI/CD and GitOps:**
  - **Gogs:** A self-hosted Git service for storing application code and configuration.
  - **Argo CD:** A declarative, GitOps continuous delivery tool for Kubernetes. It ensures that the state of the applications in the cluster matches the configuration in the Git repository.
- **Container Registry:**
  - **Docker Registry:** A private registry for storing and distributing Docker images.
- **Monitoring and Logging:**
  - **Coroot:** A monitoring and observability tool to provide insights into the platform's health and performance. Coroot agents are deployed on all Kubernetes clusters (RKE2-APPS, RKE2-MIDDLEWARE, RKE2-DMZ) and on all load balancer VMs (LBLAN, LBDMZ, LBINTEGRATION) to provide comprehensive observability across the entire infrastructure.
- **Flowable:** A business process management (BPM) engine that is deployed when "eServices" is selected.

#### Application Registry

The platform maintains a centralized registry of all deployed applications and middleware services. This registry is automatically populated during architecture scaffolding and includes comprehensive metadata about each service:

**Infrastructure Applications** (deployed on all platforms regardless of selected products):

- **ArgoCD RKE2 LAN/DMZ** (`argocd`): GitOps continuous delivery for Kubernetes clusters
- **Rancher Server** (`rancher`): Kubernetes cluster management console
- **HashiCorp Vault** (`vault`): Centralized secrets management
- **Gogs** (`gogs`): Self-hosted Git source code repository
- **Docker Registry** (`registry`): Private container image registry
- **Coroot** (`coroot`): Monitoring and observability platform
- **Keycloak** (`keycloak`): Identity and access management (IAM)
- **MinIO** (`minio`): S3-compatible object storage (primary and backup instances)
- **AKHQ** (`kafka`): Kafka cluster web UI and management interface
- **n8n** (`n8n`): Workflow automation and integration platform
- **Gravitee API Gateway** (`gravitee`): API management platform (LAN and DMZ instances)

**Product-Specific Applications** (deployed only when the corresponding product is selected):

_For EService product:_

- **Flowable BPM** (`flowable`): Business process management engine
- **E-Services Portal** (`ael-client-ui`): Citizen-facing web portal

_For GCO product:_

- **GCO Portal** (`gco`): Operations Management portal

### 3.3. Application Layer

The platform can deploy a set of "products", which are the end-user applications:

- **EServices**
- **GCO**

#### Application Access Endpoints

All applications are accessible through standardized HTTPS URLs (except where noted) that follow the pattern: `https://{prefix}{application}.{base_domain}{path_suffix}`. The `{prefix}` is configured in security settings and represent the execution environment (ex: Dev, Test, QA, Prod), and `{base_domain}` is the platform's DNS domain.

| Application                                | Category  | URL Pattern                                      | Primary Users                         |
| ------------------------------------------ | --------- | ------------------------------------------------ | ------------------------------------- |
| **Infrastructure Applications**            |
| ArgoCD RKE2 LAN                            | argocd    | `https://{prefix}argocd-apps.{domain}`           | DevOps, Platform Admins               |
| ArgoCD RKE2 DMZ                            | argocd    | `https://{prefix}argocd-dmz.{domain}`            | DevOps, Platform Admins               |
| Rancher Server                             | rancher   | `https://{prefix}rancher.{domain}`               | Cluster Administrators (All Clusters) |
| HashiCorp Vault                            | vault     | `https://{prefix}vault.{domain}`                 | DevOps, Security Teams                |
| Gogs Git Server                            | gogs      | `https://{prefix}gogs.{domain}`                  | Development Teams                     |
| Docker Registry                            | registry  | `https://{prefix}registry.{domain}/v2/_catalog`  | CI/CD Systems                         |
| Coroot Monitoring                          | coroot    | `https://{prefix}coroot.{domain}`                | SRE, DevOps                           |
| Neuvector Security Platform                 | neuvector | `https://{prefix}neuvector-apps.{domain}`        | SRE, DevOps, Security Teams           |
| Keycloak IAM                               | keycloak  | `https://{prefix}keycloak.{domain}`              | All Users                             |
| MinIO Console                              | minio     | `https://{prefix}minio-ui.{domain}`              | Administrators, Developers            |
| MinIO Backup                               | minio     | `https://{prefix}minio-backup.{domain}`          | Backup Administrators                 |
| AKHQ Kafka UI                              | kafka     | `https://{prefix}akhq.{domain}`                  | Developers                            |
| n8n Workflow                               | n8n       | `https://{prefix}n8n.{domain}`                   | Business Analysts                     |
| Gravitee API Gateway LAN                   | gravitee  | `https://{prefix}apim.{domain}/console/`         | API Administrators                    |
| Gravitee API Gateway DMZ                   | gravitee  | `https://{prefix}gravitee-dmz.{domain}/console/` | API Administrators                    |
| **Product-Specific Applications**          |
| Flowable BPM (EService)                    | flowable  | `https://{prefix}flowable.{domain}/flowable-ui`  | Business Users                        |
| E-Services Front Office (EService)         | eservices | `https://{prefix}ael-client-ui.{domain}`         | Citizens, End Users                   |
| E-Services Front Office Interne (EService) | eservices | `https://{prefix}ael-client-ui-interne.{domain}` | Internal Users                        |
| E-Services Back Office (EService)          | eservices | `https://{prefix}ael-back-ui.{domain}`           | Backoffice Users                      |
| GCO Portal (GCO)                           | gco       | `https://{prefix}gco.{domain}/GCOWEB`            | Internal/Backoffice Users             |

**Access Control Notes:**

- **Administrative Access**: Applications like Rancher, Vault, ArgoCD, MinIO Backup, and Coroot require administrative privileges and are typically accessed only by DevOps and platform operations teams
- **Developer Access**: Applications like Gogs, Docker Registry and AKHQ are primarily used by development and DevOps teams
- **Business User Access**: Applications like Flowable are intended for business analysts and process managers
- **Citizen Access**: E-Services and GCO portals are public-facing applications accessed by end users/citizens and/or Backoffice users.
- **SSO Integration**: Most applications integrate with Keycloak for single sign-on (SSO) authentication

**URL Construction:**

- URLs are automatically generated from security configuration during architecture scaffolding
- The `{prefix}` allows for environment separation (e.g., `dev-`, `test-`, `prod-`)
- Console access paths are standardized (e.g., `/console/`, `/flowable-ui`)
- Some applications include catalog or index paths for convenience (e.g., `/v2/_catalog` for Docker Registry)

### 3.4. External Service Integrations

The platform is also designed to integrate with various external services, which are configured via the API:

- **Databases:**
  - PostgreSQL
  - Informix
- **Directory Services:**
  - LDAP / Active Directory
- **Cloud and SaaS Services:**
  - Google Services (Captcha, OAuth)
  - Facebook (OAuth)
  - Firebase Cloud Messaging (FCM)
  - Firebase Realtime Database
- **Payment and Publishing:**
  - Payment Providers
  - Publishing Providers
- **Communication:**
  - SMTP Servers (for email)
  - SMS Providers
- **GIS:**
  - ArcGIS Server
- **Document Management:**
  - Alfresco

## 4. Dependencies and Communication Flow

The components of the platform are highly interconnected. Here is an overview of the key dependencies and communication flows:

- **Argo CD -> Gogs:** Argo CD pulls the Kubernetes manifests and application configurations from the Gogs Git repository to deploy and manage applications. This is the core of the **GitOps** workflow.
- **Applications -> Keycloak:** Applications delegate authentication to Keycloak. Users log in through Keycloak to access the applications.
- **Applications -> Kafka:** Applications use Kafka to exchange messages in a decoupled, asynchronous manner.
- **Applications -> Databases:** Applications connect to the configured databases (PostgreSQL, Informix) for data persistence.
- **Applications -> Vault:** Applications retrieve secrets (e.g., database credentials, API keys) from Vault at runtime, injected by the Vault Injector.
- **Applications -> MinIO:** Applications use MinIO for storing and retrieving files and other object data.
- **Longhorn -> MinIO Backup:** Longhorn, deployed on both the `RKEAPPS` and `RKEMIDDLEWARE` clusters, periodically sends volume backups to the dedicated MinIO Backup instance running on the `monitoring` VM.
- **External Users -> Load Balancer DMZ -> Gravitee DMZ -> Applications:** External HTTPS traffic from users comes through the DMZ load balancer. Static content (HTML, JS, images) is routed directly to the LB LAN, while API calls are routed to the Gravitee API Gateway in the RKE2-DMZ cluster, which then proxies the requests to the appropriate backend application (RKEAPPS or RKEMIDDLEWARE clusters via LB LAN).
- **Mobile Applications -> Load Balancer DMZ -> Load Balancer LAN -> RKEMIDDLEWARE (Kafka):** Mobile applications connect to Kafka for notifications. The traffic flows through the DMZ load balancer, then to the LAN load balancer, and finally to the RKEMIDDLEWARE cluster on ports 32100 (bootstrap) and 31400-31402 (broker connections).
- **Kubernetes/Applications (Coroot Agents) -> Coroot Server:** Coroot agents collect metrics, logs, and traces from the Kubernetes cluster and the applications to provide observability.
- **Virtual Machines (Coroot Agents) -> Coroot Server:** Coroot agents collect metrics, logs, and traces from the Kubernetes cluster and the applications to provide observability.
- **ArgoCD DMZ -> Gogs:** ArgoCD instance in RKE2-DMZ cluster pulls Kubernetes manifests and configurations from Gogs for GitOps deployment.
- **RKEDMZ <-> Rancher:** The RKE2-DMZ cluster is now fully managed by Rancher Server. Rancher agents on RKEDMZ nodes communicate with Rancher Server (port 443) for cluster management operations.
- **RKE2-DMZ -> Vault:** Gravitee DMZ API Gateway and other pods in RKE2-DMZ cluster retrieve secrets (API keys, certificates, credentials) from HashiCorp Vault via LBLAN. The LBLAN HAProxy handles the port transformation (443→8200).
- **Coroot Agents (RKE2-DMZ) -> Coroot Server:** Coroot monitoring agents deployed in RKE2-DMZ cluster connect to the Coroot server at **LBLAN:8080**, which HAProxy routes to the monitoring VM on port 8080.
- **Coroot Agents (LBDMZ) -> Coroot Server:** Coroot monitoring agents deployed on LB DMZ VMs connect to the Coroot server at **LBLAN:8080**, which HAProxy routes to the monitoring VM on port 8080.

## 5. Virtual Machines and Networks

The virtual machine architecture is defined in the `scaffold_architecture` function within `repository.py`. The function provisions several VMs with specific roles and Ansible groups, distributed across different network zones. Communication between these components is strictly managed by a set of load balancers and a defined flow matrix, ensuring security and separation of concerns.

- **VM Sizing:** The number and size (CPU, RAM, disk) of the virtual machines are determined by the `scaffold_architecture` function in `repository.py`. This function calculates the required resources based on the number of concurrent users and the products selected for installation.
- **VM Roles & Ansible Groups:** VMs are grouped by roles and managed via Ansible groups (e.g., `RKEAPPS`, `RKEMIDDLEWARE`, `LBLAN`) which correspond to their function within the architecture.
- **Network Zones:** The architecture is segmented into network zones (e.g., `LAN_APPS`, `LAN_INFRA`, `DMZ`). Each zone has its own VLAN, subnet, gateway, and DNS servers, providing network isolation.

### Load Balancer Roles and Traffic Flow

The architecture utilizes three main HAProxy load balancers, each with a distinct role:

1. **`LBLAN` (LAN Load Balancer):** This is the central hub for all internal "east-west" traffic. It routes requests between the different internal components of the platform based on DNS hostnames. For example:
   - When an application on the `RKEAPPS` cluster needs to communicate with a middleware service like Keycloak on the `RKEMIDDLEWARE` cluster, the request is directed to the `LBLAN`, which forwards it to the correct backend.
   - User access to administrative dashboards (Rancher, Coroot, Gogs, Vault) is routed through the `LBLAN`.
   - Application HTTPS traffic is terminated at the `LBLAN` and forwarded to the `RKEAPPS` cluster.
   - Specialized traffic like Kafka messaging is also managed and routed through the `LBLAN` to the `RKEMIDDLEWARE` cluster.
   - Receives routed traffic from `LBDMZ` for further distribution to internal services.
   - Rancher management traffic from all clusters including RKE2-DMZ (port 443).

2. **`LBDMZ` (DMZ Load Balancer):** This load balancer is deployed in the DMZ zone and serves as the entry point for all external traffic. It implements intelligent routing based on content type:
   - **Static Content Routing:** When a user accesses web applications, static resources (HTML, JavaScript, images, CSS) are routed through `LBDMZ` -> `LBLAN` -> `RKEAPPS` cluster.
   - **API Call Routing:** API requests from external users and mobile applications are routed through `LBDMZ` -> `RKE2-DMZ` cluster (Gravitee DMZ), where Gravitee manages and secures the API calls, then proxies them to `LBLAN` -> `RKEAPPS` or `RKEMIDDLEWARE` clusters.
   - **Mobile Kafka Notifications:** Traffic from mobile applications to Kafka brokers flows through `LBDMZ` -> `LBLAN` -> `RKEMIDDLEWARE` cluster on ports 32100 (bootstrap) and 31400-31402 (brokers).

The LBLAN also routes technical traffic from RKE2-DMZ cluster to infrastructure services:

- **ArgoCD DMZ to Gogs** (port 443): GitOps operations
- **Gravitee DMZ to Vault** (port 443→8200): Secret retrieval (HAProxy transforms port)
- **Coroot agents to Monitoring VM** (port 8080): Observability data forwarding

3. **`LBINTEGRATION` (Integration Load Balancer):** This load balancer handles all "north-south" traffic, acting as a secure gateway for communication between the platform and external services.
   - When an application in the `RKEAPPS` cluster needs to connect to an external database, SMTP server, or LDAP directory, it sends the request to the `LBINTEGRATION` VM.
   - The `LBINTEGRATION` load balancer then forwards this traffic to the final destination outside the platform. This centralizes the management of external connections and simplifies firewall configurations.

### Virtual Machine Breakdown

The platform supports **dynamic VM scaling** based on the configured number of concurrent users (100, 500, 1000, or 10000 users). The VM specifications are stored in the `VMConfiguration` table and automatically applied during architecture scaffolding.

#### VM Configuration Model

The `VMConfiguration` model stores recommended VM specifications for different user counts:

- **User Count**: 100, 500, 1000, or 10000 concurrent users
- **VM Type**: Category of VM with CONTROL/WORKER split for Kubernetes clusters
- **Node Count**: Number of VMs to create for this type
- **CPU per Node**: CPU cores allocated per VM
- **RAM per Node**: RAM in MB per VM
- **OS Disk Size**: Operating system disk size in GB
- **Data Disk Size**: Data disk size in GB (0 for load balancers)
- **Roles**: Ansible roles for the VM

#### Kubernetes RKE2 Architecture Constraints

The platform implements **Kubernetes RKE2 best practices** with the following constraints:

1. **Control Plane Nodes** (Kubernetes Masters):
   - Maximum 3 master nodes per cluster (RKE2 requirement)
   - Combined roles: "master,worker,cns" (control plane + worker + storage)
   - VM Types: `RKEAPPS_CONTROL`, `RKEMIDDLEWARE_CONTROL`
   - Hostname pattern: `{vm_type}-master1`, `{vm_type}-master2`, `{vm_type}-master3`

2. **Worker Nodes**:
   - Unlimited worker nodes (scales with user count)
   - Worker-only role: "worker"
   - VM Types: `RKEAPPS_WORKER`, `RKEMIDDLEWARE_WORKER`
   - Hostname pattern: `{vm_type}-worker1`, `{vm_type}-worker2`, ..., `{vm_type}-workerN`

3. **Load Balancers**:
   - Always exactly 2 VMs for HA (fixed count)
   - Scale only CPU and RAM, not disk
   - Data disk always 0 GB
   - VM Types: `LBLAN`, `LBDMZ`, `LBINTEGRATION`

4. **RKE2-DMZ Cluster**:
   - Always exactly 3 VMs (fixed count, small cluster)
   - Combined roles: "master,worker,cns"
   - VM Type: `RKEDMZ`
   - Hostname pattern: `rkedmz1`, `rkedmz2`, `rkedmz3`

#### VM Type Categories

**Control Plane VMs** (3 nodes each, fixed):

- **RKEAPPS_CONTROL**: 3 nodes, "master,worker,cns" roles (for 100 users) / "master" role (for 500+ users)
- **RKEMIDDLEWARE_CONTROL**: 3 nodes, "master,worker,cns" roles (for 100 users) / "master" role (for 500+ users)
- **RKEDMZ**: 3 nodes, "master,worker,cns" roles

**Dedicated CNS Storage VMs** (for 500+ users):

- **RKEAPPS_CNS**: 3 nodes, "worker,cns" roles (dedicated Longhorn storage)
- **RKEMIDDLEWARE_CNS**: 3 nodes, "worker,cns" roles (dedicated Longhorn storage)

**Worker-Only VMs** (scales with load):

- **RKEAPPS_WORKER**: N nodes, "worker" role only
- **RKEMIDDLEWARE_WORKER**: N nodes, "worker" role only
- **RKEDMZ_WORKER**: 0 nodes (not needed, RKEDMZ is small cluster)

**Load Balancer VMs** (2 nodes each, fixed):

- **LBLAN**: 2 nodes, "loadbalancer" role
- **LBDMZ**: 2 nodes, "loadbalancer" role
- **LBINTEGRATION**: 2 nodes, "loadbalancer" role

**Infrastructure VMs** (1 node each, fixed):

- **GITOPS**: 1 node, "git,docker-registry" roles
- **MONITORING**: 1 node, "admin,monitoring" roles
- **VAULT**: 1 node, "vault" role

#### Dual Architecture Pattern

The platform uses a **dual architecture pattern** to optimize resource allocation based on user count:

**Small Deployments (100 Users): Combined Roles**

- Control plane nodes handle ALL roles: control + compute + storage
- No dedicated CNS or worker nodes needed
- Simpler architecture with fewer VMs

**Large Deployments (500+ Users): Separated Roles**

- Control plane nodes handle ONLY control plane duties
- Dedicated CNS nodes provide distributed storage (Longhorn)
- Dedicated worker nodes handle application workloads
- Better resource isolation and scalability

#### Dynamic VM Scaling

The platform dynamically adjusts VM specifications based on the `number_concurrent_users` configuration:

**For 100 Users (Combined Architecture):**

- **RKEAPPS_CONTROL**: 3 nodes, 4 CPU, 8GB RAM, 60GB OS, 100GB data, "master,worker,cns"
- **RKEAPPS_CNS**: 0 nodes
- **RKEAPPS_WORKER**: 0 nodes
- **RKEMIDDLEWARE_CONTROL**: 3 nodes, 4 CPU, 8GB RAM, 60GB OS, 100GB data, "master,worker,cns"
- **RKEMIDDLEWARE_CNS**: 0 nodes
- **RKEMIDDLEWARE_WORKER**: 0 nodes
- **RKEDMZ**: 3 nodes, 4 CPU, 4GB RAM, 60GB OS, 100GB data, "master,worker,cns"
- **LBLAN**: 2 nodes, 2 CPU, 2GB RAM, 60GB OS, 0GB data, "loadbalancer"
- **LBDMZ**: 2 nodes, 2 CPU, 2GB RAM, 60GB OS, 0GB data, "loadbalancer"
- **LBINTEGRATION**: 2 nodes, 2 CPU, 2GB RAM, 60GB OS, 0GB data, "loadbalancer"
- **GITOPS**: 1 node, 4 CPU, 8GB RAM, 60GB OS, 200GB data, "git,docker-registry"
- **MONITORING**: 1 node, 4 CPU, 16GB RAM, 80GB OS, 200GB data, "admin,monitoring"
- **VAULT**: 1 node, 4 CPU, 16GB RAM, 80GB OS, 200GB data, "vault"

**For 500 Users (Separated Architecture):**

- **RKEAPPS_CONTROL**: 3 nodes, 4 CPU, 8GB RAM, 60GB OS, 0GB data, "master"
- **RKEAPPS_CNS**: 3 nodes, 4 CPU, 8GB RAM, 80GB OS, 100GB data, "worker,cns"
- **RKEAPPS_WORKER**: 1 node, 4 CPU, 8GB RAM, 80GB OS, 0GB data, "worker"
- **RKEMIDDLEWARE_CONTROL**: 3 nodes, 4 CPU, 8GB RAM, 60GB OS, 0GB data, "master"
- **RKEMIDDLEWARE_CNS**: 3 nodes, 4 CPU, 8GB RAM, 80GB OS, 100GB data, "worker,cns"
- **RKEMIDDLEWARE_WORKER**: 1 node, 4 CPU, 8GB RAM, 80GB OS, 0GB data, "worker"
- **RKEDMZ**: 3 nodes, 4 CPU, 8GB RAM, 60GB OS, 100GB data, "master,worker,cns"
- **LBLAN**: 2 nodes, 4 CPU, 4GB RAM, 60GB OS, 0GB data, "loadbalancer"
- **LBDMZ**: 2 nodes, 4 CPU, 4GB RAM, 60GB OS, 0GB data, "loadbalancer"
- **LBINTEGRATION**: 2 nodes, 2 CPU, 2GB RAM, 60GB OS, 0GB data, "loadbalancer"
- **GITOPS**: 1 node, 4 CPU, 8GB RAM, 60GB OS, 200GB data, "git,docker-registry"
- **MONITORING**: 1 node, 4 CPU, 16GB RAM, 80GB OS, 200GB data, "admin,monitoring"
- **VAULT**: 1 node, 4 CPU, 16GB RAM, 80GB OS, 200GB data, "vault"

**For 1000 Users (Separated Architecture):**

- **RKEAPPS_CONTROL**: 3 nodes, 4 CPU, 8GB RAM, 60GB OS, 0GB data, "master"
- **RKEAPPS_CNS**: 3 nodes, 4 CPU, 8GB RAM, 80GB OS, 200GB data, "worker,cns"
- **RKEAPPS_WORKER**: 5 nodes, 8 CPU, 16GB RAM, 80GB OS, 0GB data, "worker"
- **RKEMIDDLEWARE_CONTROL**: 3 nodes, 4 CPU, 8GB RAM, 60GB OS, 0GB data, "master"
- **RKEMIDDLEWARE_CNS**: 3 nodes, 4 CPU, 8GB RAM, 80GB OS, 200GB data, "worker,cns"
- **RKEMIDDLEWARE_WORKER**: 4 nodes, 8 CPU, 16GB RAM, 80GB OS, 0GB data, "worker"
- **RKEDMZ**: 3 nodes, 6 CPU, 8GB RAM, 80GB OS, 150GB data, "master,worker,cns"
- **LBLAN**: 2 nodes, 4 CPU, 4GB RAM, 60GB OS, 0GB data, "loadbalancer"
- **LBDMZ**: 2 nodes, 4 CPU, 4GB RAM, 60GB OS, 0GB data, "loadbalancer"
- **LBINTEGRATION**: 2 nodes, 4 CPU, 4GB RAM, 60GB OS, 0GB data, "loadbalancer"
- **GITOPS**: 1 node, 4 CPU, 8GB RAM, 60GB OS, 200GB data, "git,docker-registry"
- **MONITORING**: 1 node, 6 CPU, 20GB RAM, 80GB OS, 200GB data, "admin,monitoring"
- **VAULT**: 1 node, 4 CPU, 16GB RAM, 80GB OS, 200GB data, "vault"

**For 10000 Users (Separated Architecture):**

- **RKEAPPS_CONTROL**: 3 nodes, 4 CPU, 8GB RAM, 80GB OS, 0GB data, "master"
- **RKEAPPS_CNS**: 3 nodes, 4 CPU, 8GB RAM, 80GB OS, 400GB data, "worker,cns"
- **RKEAPPS_WORKER**: 6 nodes, 8 CPU, 16GB RAM, 80GB OS, 0GB data, "worker"
- **RKEMIDDLEWARE_CONTROL**: 3 nodes, 4 CPU, 8GB RAM, 80GB OS, 0GB data, "master"
- **RKEMIDDLEWARE_CNS**: 3 nodes, 4 CPU, 8GB RAM, 80GB OS, 500GB data, "worker,cns"
- **RKEMIDDLEWARE_WORKER**: 12 nodes, 8 CPU, 16GB RAM, 80GB OS, 0GB data, "worker"
- **RKEDMZ**: 3 nodes, 8 CPU, 16GB RAM, 80GB OS, 200GB data, "master,worker,cns"
- **LBLAN**: 2 nodes, 8 CPU, 8GB RAM, 80GB OS, 0GB data, "loadbalancer"
- **LBDMZ**: 2 nodes, 8 CPU, 8GB RAM, 80GB OS, 0GB data, "loadbalancer"
- **LBINTEGRATION**: 2 nodes, 4 CPU, 8GB RAM, 60GB OS, 0GB data, "loadbalancer"
- **GITOPS**: 1 node, 8 CPU, 16GB RAM, 80GB OS, 500GB data, "git,docker-registry"
- **MONITORING**: 1 node, 8 CPU, 32GB RAM, 100GB OS, 500GB data, "admin,monitoring"
- **VAULT**: 1 node, 4 CPU, 16GB RAM, 80GB OS, 500GB data, "vault"

#### Data Disk Strategy

Only certain VM types receive data disks:

- **With Data Disks**: RKEAPPS_CONTROL, RKEAPPS_WORKER, RKEMIDDLEWARE_CONTROL, RKEMIDDLEWARE_WORKER, RKEDMZ, GITOPS, MONITORING, VAULT
- **Without Data Disks**: LBLAN, LBDMZ, LBINTEGRATION (load balancers)

Data disks are used for persistent storage (Kubernetes volumes, application data, backups). Load balancers do not require data disks as they only handle traffic routing.

#### Zone Mapping

VM types are automatically mapped to network zones:

- **LAN Zone (id=1)**: RKEAPPS_CONTROL, RKEAPPS_WORKER, RKEMIDDLEWARE_CONTROL, RKEMIDDLEWARE_WORKER, LBLAN, LBINTEGRATION
- **INFRA Zone (id=2)**: GITOPS, MONITORING, VAULT
- **DMZ Zone (id=3)**: RKEDMZ, LBDMZ

#### Dynamic Hostname Generation

VM hostnames are generated dynamically based on VM type, node index, and the `env_prefix` from security configuration. The `env_prefix` allows for environment separation (e.g., "dev", "test", "prod").

**Hostname Pattern:** `{env_prefix}-{vm_type_prefix}{node_number}`

**Without prefix (env_prefix=""):**

**Control Plane VMs:**

- **RKEAPPS_CONTROL**: rkeapp-master1, rkeapp-master2, rkeapp-master3
- **RKEMIDDLEWARE_CONTROL**: rkemiddleware-master1, rkemiddleware-master2, rkemiddleware-master3
- **RKEDMZ**: rkedmz1, rkedmz2, rkedmz3

**CNS VMs:**

- **RKEAPPS_CNS**: rkeapp-cns1, rkeapp-cns2, rkeapp-cns3
- **RKEMIDDLEWARE_CNS**: rkemiddleware-cns1, rkemiddleware-cns2, rkemiddleware-cns3

**Worker VMs:**

- **RKEAPPS_WORKER**: rkeapp-worker1, rkeapp-worker2, ..., rkeapp-workerN
- **RKEMIDDLEWARE_WORKER**: rkemiddleware-worker1, rkemiddleware-worker2, ..., rkemiddleware-workerN

**Load Balancer VMs:**

- **LBLAN**: lblan1, lblan2
- **LBDMZ**: lbdmz1, lbdmz2
- **LBINTEGRATION**: lbintegration1, lbintegration2

**Infrastructure VMs:**

- **GITOPS**: gitops
- **MONITORING**: monitoring
- **VAULT**: vault

**With prefix (env_prefix="dev"):**

**Control Plane VMs:**

- **RKEAPPS_CONTROL**: dev-rkeapp-master1, dev-rkeapp-master2, dev-rkeapp-master3
- **RKEMIDDLEWARE_CONTROL**: dev-rkemiddleware-master1, dev-rkemiddleware-master2, dev-rkemiddleware-master3
- **RKEDMZ**: dev-rkedmz1, dev-rkedmz2, dev-rkedmz3

**CNS VMs:**

- **RKEAPPS_CNS**: dev-rkeapp-cns1, dev-rkeapp-cns2, dev-rkeapp-cns3
- **RKEMIDDLEWARE_CNS**: dev-rkemiddleware-cns1, dev-rkemiddleware-cns2, dev-rkemiddleware-cns3

**Worker VMs:**

- **RKEAPPS_WORKER**: dev-rkeapp-worker1, dev-rkeapp-worker2, ..., dev-rkeapp-workerN
- **RKEMIDDLEWARE_WORKER**: dev-rkemiddleware-worker1, dev-rkemiddleware-worker2, ..., dev-rkemiddleware-workerN

**Load Balancer VMs:**

- **LBLAN**: dev-lblan1, dev-lblan2
- **LBDMZ**: dev-lbdmz1, dev-lbdmz2
- **LBINTEGRATION**: dev-lbintegration1, dev-lbintegration2

**Infrastructure VMs:**

- **GITOPS**: dev-gitops
- **MONITORING**: dev-monitoring
- **VAULT**: dev-vault

This naming convention ensures consistency between VM hostnames and DNS records, both using the same `env_prefix` for environment identification.

### Flow Matrix

The following table details the primary communication flows between the different Ansible groups, as managed by the load balancers.

| Source Group                         | Destination Group      | Destination Port      | Protocol  | Description                                                                                                            |
| :----------------------------------- | :--------------------- | :-------------------- | :-------- | :--------------------------------------------------------------------------------------------------------------------- |
| External User                        | `LBDMZ`                | 443                   | TCP/HTTPS | Main application traffic from external users, routed to `RKEAPPS` cluster (static content) or `RKEDMZ` cluster (APIs). |
| Mobile Application                   | `LBDMZ`                | 32100, 31400-31402    | TCP       | Mobile app traffic to Kafka brokers, routed to `RKEMIDDLEWARE` cluster via `LBLAN`.                                    |
| Internal User                        | `LBLAN`                | 443                   | TCP/HTTPS | Main application traffic (e.g., eServices, GCO), routed to `RKEAPPS` cluster.                                          |
| Admin User                           | `LBLAN`                | 443                   | TCP/HTTPS | Middleware UI/API access (Keycloak, MinIO, n8n, Flowable), routed to `RKEMIDDLEWARE` cluster.                          |
| Admin User                           | `LBLAN`                | 443                   | TCP/HTTPS | Rancher management UI, routed to `monitoring` group (backend port 443).                                                |
| Admin User                           | `LBLAN`                | 443                   | TCP/HTTPS | Gogs Git server UI/API, routed to `gitops` group (backend port 443).                                                   |
| `RKEAPPS` / `RKEMIDDLEWARE` (ArgoCD) | `LBLAN`                | 443                   | TCP/HTTPS | GitOps traffic from ArgoCD to Gogs, routed to `gitops` group.                                                          |
| Admin User                           | `LBLAN`                | 443                   | TCP/HTTPS | Coroot monitoring dashboard, routed to `monitoring` group (backend port 8080).                                         |
| Admin User                           | `LBLAN`                | 443                   | TCP/HTTPS | MinIO Backup UI, routed to `monitoring` group (backend port 9001).                                                     |
| K8s Nodes / CI/CD                    | `LBLAN`                | 443                   | TCP/HTTPS | Container image pulls/pushes via hostname, routed to `gitops` group (backend port 8443).                               |
| `RKEDMZ` (Gravitee DMZ)              | `LBLAN`                | 443                   | TCP/HTTPS | API proxy traffic from Gravitee DMZ to backend services in `RKEAPPS` or `RKEMIDDLEWARE` clusters.                      |
| `LBDMZ`                              | `LBLAN`                | 443                   | TCP/HTTPS | Static content routing from `LBDMZ` to `LBLAN` for delivery to `RKEAPPS` cluster.                                      |
| `RKEDMZ` (ArgoCD)                    | `gitops`               | 443                   | TCP/HTTPS | GitOps traffic: ArgoCD DMZ pulling configurations from Gogs.                                                           |
| `RKEDMZ`                             | `gitops`               | 8443                  | TCP/HTTPS | Docker Registry access: RKEDMZ pulling container images from private registry.                                         |
| `RKEDMZ` (Gravitee DMZ)              | `vault`                | 443                   | TCP/HTTPS | Secret retrieval: Gravitee DMZ accessing Vault via LBLAN (443→8200).                                                   |
| `RKEDMZ` (Coroot Agents)             | `monitoring`           | 8080                  | TCP       | Monitoring: Coroot agents in RKE2-DMZ forwarding metrics directly to Coroot server on monitoring VM.                   |
| `LBDMZ` (Coroot Agents)              | `monitoring`           | 8080                  | TCP       | Monitoring: Coroot agents on LB DMZ forwarding metrics directly to Coroot server on monitoring VM.                     |
| `RKEAPPS` / `RKEMIDDLEWARE`          | `vault`                | 8200                  | TCP/HTTPS | **Direct Connection:** Secret retrieval from HashiCorp Vault.                                                          |
| `RKEAPPS` / `RKEMIDDLEWARE`          | `monitoring`           | 9000                  | TCP/S3    | **Direct Connection:** Longhorn sending backups to the MinIO Backup S3 endpoint.                                       |
| `RKEAPPS`                            | `LBLAN`                | 32100                 | TCP       | Kafka initial bootstrap connection, routed to `RKEMIDDLEWARE` cluster.                                                 |
| `RKEAPPS`                            | `LBLAN`                | 31400-31402           | TCP       | Kafka broker connections, routed to `RKEMIDDLEWARE` cluster.                                                           |
| `RKEAPPS` / `RKEMIDDLEWARE`          | `LBINTEGRATION`        | `(variable)`          | TCP       | SMTP traffic to external mail server.                                                                                  |
| `RKEAPPS` / `RKEMIDDLEWARE`          | `LBINTEGRATION`        | `(variable)`          | TCP       | Connection to external databases (PostgreSQL, Informix, SIG).                                                          |
| `RKEAPPS` / `RKEMIDDLEWARE`          | `LBINTEGRATION`        | `(variable)`          | TCP       | Connection to external LDAP / Active Directory services.                                                               |
| `RKEAPPS`                            | `LBINTEGRATION`        | `(variable)`          | TCP       | Connection to external providers (SMS, Payment).                                                                       |
| `RKEAPPS`                            | `LBINTEGRATION`        | `(variable)` or fixed | TCP/HTTPS | Connection to external application services (ArcGIS, Alfresco, Gmao, etc.).                                            |
| RKEDMZ (Rancher Agents)              | `monitoring` (Rancher) | 443                   | TCP/HTTPS | Rancher agent communication from RKE2-DMZ cluster to Rancher Server.                                                   |

This detailed architecture allows for a robust, scalable, and manageable deployment of a complex application ecosystem. The use of automation, containerization, and modern middleware practices ensures a high degree of consistency and reliability.
