# SRM-CS Platform "HARMONISATION" Architecture

!!! info "About This Documentation"
This document provides a detailed overview of the architecture of the platform deployed by the SRM-CS automation project. The platform is a complex system composed of multiple layers, including infrastructure, middleware, and applications, all managed and deployed through a centralized automation engine.

## Overall Architecture

The deployed architecture is a comprehensive, on-premises, microservices-based platform built on Kubernetes. It is designed to be highly available, secure, and scalable, providing a full stack of middleware and services to run modern applications.

The architecture is deployed on a hypervisor (VMware or Nutanix) and is segmented into multiple network zones for security and isolation. It leverages **Kubernetes (RKE2)** for container orchestration, **Rancher** for cluster management, and a wide range of popular open-source middleware to support the deployed applications. The entire platform is managed using a GitOps approach with **Argo CD** and **Gogs**.

The deployment process is fully automated and follows a specific sequence to ensure a consistent and reliable setup.

### Key Architectural Principles

- **Microservices-Based**: Applications are decomposed into independently deployable services
- **High Availability**: Redundant components and multi-node clusters ensure uptime
- **Security Isolation**: Network segmentation via VLANs (LAN, INFRA, DMZ zones)
- **GitOps Workflow**: All configuration managed as code in Git repositories
- **Scalability**: Dynamic VM scaling based on concurrent user count (100, 500, 1000, 10000)
- **Automation First**: Fully automated deployment with Ansible Runner

### Architecture Layers

The platform consists of three main layers:

#### 1. Infrastructure Layer

- Hypervisor (VMware vSphere/ESXi or Nutanix AHV)
- Virtual machines provisioned for different roles
- Network segmentation (VLANs, subnets, DNS)
- HAProxy load balancers for traffic distribution

#### 2. Middleware Layer

- **Container Orchestration**: Three RKE2 Kubernetes clusters (APPS, MIDDLEWARE, DMZ)
- **Cluster Management**: Rancher for unified management
- **Storage**: Longhorn (distributed block storage) + MinIO (S3-compatible object storage)
- **Security**: HashiCorp Vault, Cert-manager, Neuvector, Keycloak
- **Messaging**: Apache Kafka
- **API Management**: Gravitee (LAN and DMZ instances)
- **CI/CD**: Gogs + Argo CD for GitOps
- **Monitoring**: Coroot for observability
- **Workflow Automation**: n8n
- **BPM Engine**: Flowable (when eServices product is selected)

#### 3. Application Layer

End-user applications deployed on the platform:

- **EServices**: Citizen-facing e-government services platform
- **GCO**: Operations management portal

### Network Zones

The architecture is segmented into three network zones:

| Zone      | Purpose                                     | Key Components                                               |
| --------- | ------------------------------------------- | ------------------------------------------------------------ |
| **LAN**   | Internal application and middleware hosting | RKEAPPS cluster, RKEMIDDLEWARE cluster, LBLAN, LBINTEGRATION |
| **INFRA** | Core infrastructure services                | Gogs, Docker Registry, HashiCorp Vault, Monitoring           |
| **DMZ**   | External-facing services                    | RKEDMZ cluster, Gravitee DMZ, LBDMZ                          |

Each zone has its own VLAN, subnet, gateway, and DNS configuration for complete isolation.

### Three Kubernetes Clusters

The platform deploys three separate RKE2 Kubernetes clusters:

1. **RKE2-APPS**: Runs business applications (eServices, GCO)
2. **RKE2-MIDDLEWARE**: Runs supporting middleware services (Keycloak, Kafka, MinIO, n8n, Flowable)
3. **RKE2-DMZ**: Runs API Gateway (Gravitee DMZ) in the DMZ zone for external traffic

All three clusters are managed by a single **Rancher** instance for unified operations.

---

!!! tip "Next Steps"
Continue to the [Deployment Process](deployment-process.md) to understand how the platform is built from the ground up.
