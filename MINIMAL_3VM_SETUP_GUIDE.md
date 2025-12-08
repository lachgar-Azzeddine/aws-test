# Minimal 3-VM Test Setup Guide

**Purpose:** Test the SRM-CS platform with only 4 AWS EC2 VMs (1 controller + 3 targets)

**Total VMs:** 4 × t3.medium (2 vCPU, 4GB RAM each)

---

## Architecture Overview

```
┌───────────────────────────────────────────────────────────┐
│ AWS EC2 Environment (4 VMs)                               │
├───────────────────────────────────────────────────────────┤
│                                                            │
│ VM1: Controller (10.0.1.10)                               │
│ ├── Backend (FastAPI + Ansible Runner)                   │
│ ├── PostgreSQL Database                                   │
│ └── Docker Compose                                        │
│                                                            │
│ ┌──────────────────────────────────────────────────────┐ │
│ │ Target VMs (3 VMs)                                   │ │
│ ├──────────────────────────────────────────────────────┤ │
│ │                                                       │ │
│ │ VM2: Infrastructure (10.0.1.11)                      │ │
│ │ ├── Docker Registry (port 5000)                      │ │
│ │ └── Gogs Git Server (port 3000)                      │ │
│ │                                                       │ │
│ │ VM3: RKE2 Master (10.0.1.12)                         │ │
│ │ ├── RKE2 Server (control plane)                      │ │
│ │ └── RKE2 Agent (also acts as worker)                 │ │
│ │                                                       │ │
│ │ VM4: RKE2 Worker (10.0.1.13)                         │ │
│ │ └── RKE2 Agent (worker node)                         │ │
│ │                                                       │ │
│ │ ┌────────────────────────────────────┐               │ │
│ │ │ On RKE2 Cluster:                   │               │ │
│ │ ├────────────────────────────────────┤               │ │
│ │ │ - Longhorn (persistent storage)    │               │ │
│ │ │ - ArgoCD (GitOps deployment)       │               │ │
│ │ │ - Test applications                │               │ │
│ │ └────────────────────────────────────┘               │ │
│ └──────────────────────────────────────────────────────┘ │
└───────────────────────────────────────────────────────────┘
```

---

## What This Tests

✅ **Ansible automation** - Backend orchestrates everything
✅ **Infrastructure provisioning** - Docker Registry + Gogs on bare metal
✅ **Kubernetes cluster** - RKE2 (1 master + 1 worker)
✅ **Storage layer** - Longhorn for persistent volumes
✅ **GitOps deployment** - ArgoCD for app management
✅ **Full workflow** - Push image → Registry → Deploy to K8s

❌ **NOT testing:**
- High availability (only 1 master)
- Keycloak authentication
- Multiple clusters (middleware, DMZ)
- Vault, HAProxy, Rancher
- Monitoring (NeuVector, Coroot)

---

## Prerequisites

### AWS EC2 VMs

**Launch 4 × t3.medium instances:**

| VM Name       | Private IP   | Role                  | OS             |
|---------------|--------------|-----------------------|----------------|
| controller    | 10.0.1.10    | Backend + Ansible     | Ubuntu 24.04   |
| infra-vm      | 10.0.1.11    | Registry + Gogs       | Ubuntu 24.04   |
| rke-master    | 10.0.1.12    | RKE2 Master           | Ubuntu 24.04   |
| rke-worker    | 10.0.1.13    | RKE2 Worker           | Ubuntu 24.04   |

**Note:** Adjust IPs to match your AWS VPC subnet.

### Security Group Rules

**Controller VM (10.0.1.10):**
- Allow SSH (22) from your IP
- Allow 8008 (API) from your IP
- Allow 5432 (PostgreSQL) from your IP (optional, for debugging)
- Allow outbound SSH (22) to target VMs

**Target VMs (10.0.1.11-13):**
- Allow SSH (22) from Controller VM (10.0.1.10)
- Allow all traffic between target VMs (10.0.1.11-13)
- Specific ports:
  - VM2: 5000 (Registry), 3000 (Gogs)
  - VM3/VM4: 6443 (Kubernetes API), 9345 (RKE2), 10250 (Kubelet)

### SSH Access

**On Controller VM**, generate SSH key and copy to all target VMs:

```bash
# On Controller VM (10.0.1.10)
ssh-keygen -t rsa -b 4096 -f ~/.ssh/id_rsa -N ""

# Copy to all 3 target VMs
ssh-copy-id ubuntu@10.0.1.11
ssh-copy-id ubuntu@10.0.1.12
ssh-copy-id ubuntu@10.0.1.13

# Test connectivity
ssh ubuntu@10.0.1.11 'echo "VM2 OK"'
ssh ubuntu@10.0.1.12 'echo "VM3 OK"'
ssh ubuntu@10.0.1.13 'echo "VM4 OK"'
```

---

## Setup Steps

### Step 1: Prepare Controller VM

**Install Docker + Docker Compose:**

```bash
# Update packages
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com | sudo sh
sudo usermod -aG docker $USER
newgrp docker

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
docker-compose --version
```

**Clone the project:**

```bash
# Upload your testing folder to the controller VM
# Or clone from Git if you have it in a repo

cd /home/ubuntu
# Assuming you've uploaded the folder
ls runner-srm-cs-testing/
```

### Step 2: Configure the Database

**Create data directories:**

```bash
cd runner-srm-cs-testing
mkdir -p data/{.ssh,.kube,inventory,env,terraform/{apps,infra,dmz},postgres,db}
chmod 700 data/.ssh
```

**Copy SSH key to data directory:**

```bash
cp ~/.ssh/id_rsa data/.ssh/
cp ~/.ssh/id_rsa.pub data/.ssh/
chmod 600 data/.ssh/id_rsa
```

**Start the services:**

```bash
docker compose up -d
```

**Verify services are running:**

```bash
docker ps
# Should see: backend, postgres

docker logs backend
# Should see: "Uvicorn running on http://0.0.0.0:8008"
```

**Access the API documentation:**

Open browser: `http://<controller-public-ip>:8008/docs`

### Step 3: Populate Database with 3 VMs

**Connect to PostgreSQL:**

```bash
docker exec -it postgres psql -U harmonisation -d harmonisation
```

**Insert configuration:**

```sql
-- Configuration (user count doesn't matter for manual VM setup)
INSERT INTO configurations (id, number_concurrent_users) VALUES (1, 100);

-- Security (SSH keys and domain)
INSERT INTO security (
    id,
    use_proxy,
    ssh_pulic_key,
    ssh_private_key,
    ssh_private_key_pwd,
    base_domain,
    env_prefix,
    pem_certificate,
    configuration_id
) VALUES (
    1,
    FALSE,
    'ssh-rsa AAAAB3... your-public-key', -- Replace with actual public key
    '-----BEGIN OPENSSH PRIVATE KEY-----\n...', -- Replace with actual private key
    '',
    'test.local',
    'test',
    '-----BEGIN CERTIFICATE-----\n...\n-----END CERTIFICATE-----\n-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----',
    1
);

-- Network Zone (single zone for simplicity)
INSERT INTO zones (
    id,
    name,
    sub_network,
    network_mask,
    gateway,
    dns,
    domain,
    vlan_name,
    ip_pool_start,
    ip_pool_end,
    hypervisor_type
) VALUES (
    1,
    'TEST_ZONE',
    '10.0.1.0',
    24,
    '10.0.1.1',
    '8.8.8.8,8.8.4.4',
    'test.local',
    'default',
    '10.0.1.10',
    '10.0.1.20',
    'vmware'  -- Dummy value, not used for pre-existing VMs
);

-- VM1: Infrastructure (Docker Registry + Gogs)
INSERT INTO virtual_machines (
    hostname,
    ip,
    zone_id,
    "group",  -- "group" is a reserved keyword, use quotes
    roles,
    nb_cpu,
    ram,
    os_disk_size,
    data_disk_size,
    status
) VALUES (
    'infra-vm',
    '10.0.1.11',
    1,
    'infrastructure',
    'docker-registry,gogs',
    2,
    4096,
    30,
    0,
    'created'  -- Already exists, skip provisioning
);

-- VM2: RKE2 Master
INSERT INTO virtual_machines (
    hostname,
    ip,
    zone_id,
    "group",
    roles,
    nb_cpu,
    ram,
    os_disk_size,
    data_disk_size,
    status
) VALUES (
    'rke-master',
    '10.0.1.12',
    1,
    'RKEAPPS',
    'rke2-server',
    2,
    4096,
    30,
    0,
    'created'
);

-- VM3: RKE2 Worker
INSERT INTO virtual_machines (
    hostname,
    ip,
    zone_id,
    "group",
    roles,
    nb_cpu,
    ram,
    os_disk_size,
    data_disk_size,
    status
) VALUES (
    'rke-worker',
    '10.0.1.13',
    1,
    'RKEAPPS_WORKER',
    'rke2-agent',
    2,
    4096,
    30,
    0,
    'created'
);

-- Verify
SELECT hostname, ip, "group", roles, status FROM virtual_machines;

\q
```

### Step 4: Run Ansible Deployment

**Test connectivity first:**

```bash
docker exec -it backend bash

# Inside container
cd /home/devops
ansible all -i inventory/ -m ping
# Should get: pong from all 3 VMs
```

**Run individual roles (step by step):**

```bash
# Step 1: Prepare VMs (install Docker, packages, SSH keys)
docker exec backend python install.py --role prepare-vms

# Step 2: Install Docker Registry on VM1
docker exec backend python install.py --role install-docker-registry

# Step 3: Install Gogs on VM1
docker exec backend python install.py --role install-gogs

# Step 4: Install RKE2 cluster (VM2 master + VM3 worker)
docker exec backend python install.py --role install-rke2-apps

# Step 5: Install Longhorn storage
docker exec backend python install.py --role install-longhorn

# Step 6: Install ArgoCD
docker exec backend python install.py --role install-argocd
```

**Or run all roles at once:**

```bash
docker exec backend python install.py --role all
```

**Monitor logs:**

```bash
docker logs backend -f
```

**Check role status via API:**

```bash
curl http://localhost:8008/ansible-roles
```

### Step 5: Verify Installation

**Check Docker Registry (VM2):**

```bash
ssh ubuntu@10.0.1.11
curl http://localhost:5000/v2/_catalog
# Should return: {"repositories":[]}
```

**Check Gogs (VM2):**

```bash
curl http://10.0.1.11:3000
# Should return: HTML page
```

**Check RKE2 Cluster:**

```bash
# On Controller, copy kubeconfig from master
scp ubuntu@10.0.1.12:/etc/rancher/rke2/rke2.yaml ~/.kube/config

# Edit config to use master IP
sed -i 's/127.0.0.1/10.0.1.12/g' ~/.kube/config

# Install kubectl
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
sudo install kubectl /usr/local/bin/

# Test
kubectl get nodes
# Should show: rke-master (Ready), rke-worker (Ready)

kubectl get pods -A
# Should show: Longhorn, ArgoCD pods running
```

**Access ArgoCD:**

```bash
# Get initial admin password
kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath="{.data.password}" | base64 -d

# Port-forward ArgoCD UI
kubectl port-forward svc/argocd-server -n argocd 8080:443

# Access: https://localhost:8080
# Username: admin
# Password: <from above command>
```

---

## Troubleshooting

### SSH Connection Fails

```bash
# Check SSH key is in data/.ssh/
docker exec backend ls -la /home/devops/.ssh/

# Test SSH from container
docker exec -it backend bash
ssh -i /home/devops/.ssh/id_rsa ubuntu@10.0.1.11
```

### Ansible Role Fails

```bash
# Check task logs
curl http://localhost:8008/task-logs

# Or query database
docker exec -it postgres psql -U harmonisation -d harmonisation
SELECT * FROM task_logs ORDER BY id DESC LIMIT 20;
```

### RKE2 Installation Fails

```bash
# On master VM, check RKE2 logs
ssh ubuntu@10.0.1.12
sudo journalctl -u rke2-server -f

# On worker VM
ssh ubuntu@10.0.1.13
sudo journalctl -u rke2-agent -f
```

### Longhorn Pods Not Starting

```bash
# Check if iscsid is installed on all nodes
ssh ubuntu@10.0.1.12 'sudo systemctl status iscsid'
ssh ubuntu@10.0.1.13 'sudo systemctl status iscsid'

# Install if missing
ssh ubuntu@10.0.1.12 'sudo apt install open-iscsi -y && sudo systemctl enable iscsid && sudo systemctl start iscsid'
ssh ubuntu@10.0.1.13 'sudo apt install open-iscsi -y && sudo systemctl enable iscsid && sudo systemctl start iscsid'
```

---

## What's Different from Production?

| Component                  | Production Setup             | Minimal Test Setup     |
|----------------------------|------------------------------|------------------------|
| Total VMs                  | 25-35 VMs                    | **3 VMs**              |
| RKE2 Clusters              | 3 clusters (apps, middleware, DMZ) | **1 cluster**   |
| RKE2 Control Plane         | 3 masters (HA)               | **1 master**           |
| RKE2 Workers               | 5-10 per cluster             | **1 worker**           |
| Vault                      | 2 VMs (HA)                   | **Skipped**            |
| Docker Registry            | Dedicated VM                 | **Shared with Gogs**   |
| Gogs                       | Dedicated VM                 | **Shared with Registry** |
| HAProxy                    | 2 VMs (HA)                   | **Skipped**            |
| Keycloak                   | On middleware cluster        | **Skipped**            |
| Kafka                      | On middleware cluster        | **Skipped**            |
| MinIO                      | On middleware cluster        | **Skipped**            |
| Gravitee API Gateway       | LAN + DMZ                    | **Skipped**            |
| Monitoring (NeuVector)     | Dedicated                    | **Skipped**            |
| VM Provisioning (Terraform)| Automated                    | **Manual (pre-existing)** |

---

## Next Steps

Once you verify the basic setup works:

1. **Test application deployment** - Deploy a simple app via ArgoCD
2. **Test Docker Registry** - Push/pull images
3. **Test Gogs** - Create repositories
4. **Add more roles** - Gradually add cert-manager, vault, etc.
5. **Scale up** - Add more worker nodes

---

## Cost Estimate (AWS)

**4 × t3.medium (on-demand):**
- $0.0416/hour × 4 = $0.1664/hour
- **~$120/month** (if running 24/7)

**Recommendation:** Use EC2 spot instances to save ~70% ($35/month)

---

## Files Modified for This Setup

1. **`install.py`** - Reduced role list from 32 to 6 roles
2. **`docker-compose.yml`** - Removed frontend, nginx, corteza
3. **Database** - Manual VM insertion (no scaffolding)

---

**Ready to test!** Start with `docker compose up -d` and follow the steps above. 🚀
