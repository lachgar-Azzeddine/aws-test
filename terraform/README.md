# Terraform Infrastructure for Harmonisation Testing

This Terraform configuration creates 5 EC2 instances on AWS, pre-configured and ready for the `prepare-vms` Ansible role.

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        AWS VPC                                   │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │                     Subnet                               │    │
│  │                                                          │    │
│  │   ┌─────────┐  ┌─────────┐  ┌─────────┐                 │    │
│  │   │ vault   │  │ gitops  │  │rkeapp1  │                 │    │
│  │   │ t3.med  │  │ t3.med  │  │ t3.med  │                 │    │
│  │   │ Vault   │  │ Gogs    │  │ RKE2    │                 │    │
│  │   │         │  │ Registry│  │ master  │                 │    │
│  │   └─────────┘  └─────────┘  └─────────┘                 │    │
│  │                                                          │    │
│  │   ┌─────────┐  ┌─────────┐                              │    │
│  │   │rkeapp2  │  │rkeapp3  │                              │    │
│  │   │ t3.med  │  │ t3.med  │                              │    │
│  │   │ RKE2    │  │ RKE2    │                              │    │
│  │   │ master  │  │ master  │                              │    │
│  │   └─────────┘  └─────────┘                              │    │
│  │                                                          │    │
│  └─────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────┘
```

## VMs Created

| VM Name  | Group    | Roles                | Purpose                    |
|----------|----------|----------------------|----------------------------|
| vault    | vault    | vault                | HashiCorp Vault (secrets)  |
| gitops   | gitops   | git,docker-registry  | Gogs + Docker Registry     |
| rkeapp1  | RKEAPPS  | master,worker,cns    | RKE2 K8s node             |
| rkeapp2  | RKEAPPS  | master,worker,cns    | RKE2 K8s node             |
| rkeapp3  | RKEAPPS  | master,worker,cns    | RKE2 K8s node             |

## Pre-configured Features

Each VM is automatically configured with:

- **Ubuntu 22.04 LTS**
- **devops user** with password `devops` (configurable)
- **SSH password authentication enabled**
- **SSH public key** added to authorized_keys
- **Docker** installed and running
- **Kernel modules** for Kubernetes (overlay, br_netfilter)
- **Sysctl settings** for networking
- **iSCSI** enabled (for Longhorn)
- **Swap disabled**
- **Data disk** mounted at `/data` (RKE nodes only)

## Prerequisites

1. **AWS CLI** configured with credentials
2. **Terraform** >= 1.0 installed
3. **SSH key pair** in AWS (or create one)
4. **VPC and Subnet** (can use default VPC)

## Quick Start

### 1. Configure Variables

```bash
cd terraform
cp terraform.tfvars.example terraform.tfvars
```

Edit `terraform.tfvars`:

```hcl
aws_region = "eu-west-1"
key_name   = "your-aws-key-pair"
vpc_id     = "vpc-xxxxxxxxx"
subnet_id  = "subnet-xxxxxxxxx"

# Your SSH public key (paste content)
ssh_public_key = "ssh-rsa AAAAB3NzaC1yc2E..."

base_domain = "example.com"
```

### 2. Deploy Infrastructure

```bash
# Initialize Terraform
terraform init

# Preview changes
terraform plan

# Create infrastructure
terraform apply
```

### 3. Generate Database Configuration

```bash
# Export Terraform output and generate initial_db.py
export SSH_PUBLIC_KEY=$(cat ~/.ssh/id_rsa.pub)
export SSH_PRIVATE_KEY=$(cat ~/.ssh/id_rsa)
export BASE_DOMAIN="example.com"

terraform output -json > tf_output.json
python generate_db_config.py tf_output.json
```

This creates `../backend/initial_db.py` with your VM IPs pre-filled.

### 4. View VM Details

```bash
# Show all VM IPs
terraform output vm_details

# Show SSH commands
terraform output ssh_commands

# Show configuration for initial_db.py
terraform output initial_db_config
```

### 5. Test SSH Connection

```bash
# Using password (default: devops)
ssh devops@<public_ip>

# Using SSH key
ssh -i ~/.ssh/id_rsa devops@<public_ip>
```

## Deployment Workflow

```
┌─────────────────────────────────────────────────────────────────┐
│                    DEPLOYMENT WORKFLOW                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  1. terraform apply          ───► Create 5 EC2 instances        │
│                                                                 │
│  2. cloud-init runs          ───► Configure VMs:                │
│                                   - devops user                 │
│                                   - Docker                      │
│                                   - SSH keys                    │
│                                                                 │
│  3. generate_db_config.py    ───► Create initial_db.py          │
│                                   with VM IPs                   │
│                                                                 │
│  4. docker compose up        ───► Start backend                 │
│                                   (auto-creates DB)             │
│                                                                 │
│  5. prepare-vms role         ───► Final VM preparation          │
│                                                                 │
│  6. install-vault role       ───► Deploy Vault                  │
│                                                                 │
│  7. install-docker-registry  ───► Deploy Registry               │
│                                                                 │
│  8. install-gogs role        ───► Deploy Gogs                   │
│                                                                 │
│  9. install-rke2-apps role   ───► Deploy RKE2 cluster           │
│                                                                 │
│  10. install-longhorn role   ───► Deploy Longhorn storage       │
│                                                                 │
│  11. install-argocd role     ───► Deploy ArgoCD                 │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## Customization

### Change Instance Type

```hcl
instance_type = "t3.large"  # 2 vCPU, 8 GB RAM
```

### Change Disk Sizes

```hcl
root_volume_size = 100  # GB
data_volume_size = 200  # GB (RKE nodes only)
```

### Add More RKE Nodes

Edit `variables.tf`:

```hcl
variable "vms" {
  default = {
    # ... existing VMs ...
    "rkeapp4" = {
      role       = "rke2"
      group      = "RKEAPPS"
      roles_list = "worker,cns"
    }
  }
}
```

## Cleanup

```bash
# Destroy all resources
terraform destroy
```

## Troubleshooting

### SSH Connection Refused

Wait 2-3 minutes for cloud-init to complete:
```bash
ssh devops@<ip> "cloud-init status --wait"
```

### Docker Not Running

```bash
ssh devops@<ip> "sudo systemctl status docker"
```

### Check Cloud-Init Logs

```bash
ssh devops@<ip> "sudo cat /var/log/cloud-init-output.log"
```

## Cost Estimate

| Resource          | Type       | Hourly Cost (eu-west-1) |
|-------------------|------------|-------------------------|
| EC2 (5x t3.medium)| Compute    | ~$0.21/hr              |
| EBS (5x 50GB gp3) | Storage    | ~$0.02/hr              |
| EBS (3x 100GB gp3)| Storage    | ~$0.02/hr              |
| **Total**         |            | **~$0.25/hr**          |

**Monthly estimate**: ~$180/month (if running 24/7)

## Security Notes

1. **Security Group** allows SSH from anywhere (`0.0.0.0/0`) - restrict in production
2. **Password authentication** is enabled - use SSH keys in production
3. **Default password** `devops` should be changed in production
