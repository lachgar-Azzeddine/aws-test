# KodeKloud Playground - Quick Start Guide

## Step 1: Open KodeKloud Playground

1. Go to KodeKloud
2. Start "AWS Playground" or "Terraform + AWS" lab
3. Wait for terminal to be ready

---

## Step 2: Get AWS Info (in KodeKloud terminal)

```bash
# Get VPC ID
aws ec2 describe-vpcs --query 'Vpcs[0].VpcId' --output text

# Get Subnet ID
aws ec2 describe-subnets --query 'Subnets[0].SubnetId' --output text

# Get Region
aws configure get region
```

**Write down these values!**

---

## Step 3: Create SSH Key (in KodeKloud terminal)

```bash
# Create key pair
aws ec2 create-key-pair --key-name harmo-key --query 'KeyMaterial' --output text > ~/.ssh/harmo-key.pem
chmod 600 ~/.ssh/harmo-key.pem

# Generate public key
ssh-keygen -y -f ~/.ssh/harmo-key.pem > ~/.ssh/harmo-key.pub
cat ~/.ssh/harmo-key.pub
```

**Copy the public key output!**

---

## Step 4: Upload Terraform Files

Upload these files to KodeKloud terminal:
- `main.tf`
- `variables.tf`
- `outputs.tf`
- `data.tf`
- `cloud-init.yaml`

Or clone from git if available.

---

## Step 5: Create terraform.tfvars (in KodeKloud terminal)

```bash
cat > terraform.tfvars << 'EOF'
aws_region    = "us-east-1"          # From step 2
key_name      = "harmo-key"
vpc_id        = "vpc-xxxxxxxxx"      # REPLACE - From step 2
subnet_id     = "subnet-xxxxxxxxx"   # REPLACE - From step 2
environment   = "harmo-test"
instance_type = "t3.medium"
root_volume_size = 30
data_volume_size = 50
devops_password = "devops"
base_domain     = "local"
ssh_public_key = "ssh-rsa AAAA..."   # REPLACE - From step 3
EOF
```

---

## Step 6: Run Terraform (in KodeKloud terminal)

```bash
# Initialize
terraform init

# Preview
terraform plan

# Create VMs (takes ~3-5 minutes)
terraform apply -auto-approve
```

---

## Step 7: Get VM IPs

```bash
# Show all IPs
terraform output vm_details

# Or formatted
terraform output -json vm_details | jq -r 'to_entries[] | "\(.key): \(.value.public_ip)"'
```

Example output:
```
vault: 54.123.45.67
gitops: 54.123.45.68
rkeapp1: 54.123.45.69
rkeapp2: 54.123.45.70
rkeapp3: 54.123.45.71
```

---

## Step 8: Test SSH Connection

```bash
# Test connection (password: devops)
ssh devops@54.123.45.67

# Or with key
ssh -i ~/.ssh/harmo-key.pem devops@54.123.45.67
```

---

## Step 9: Update initial_db.py (on your computer)

Edit `backend/initial_db.py` and fill in the IPs:

```python
# VM 1: Vault
vm1 = VirtualMachine(
    hostname="vault",
    roles="vault",
    group="vault",
    ip="54.123.45.67",  # <-- Vault public IP
    ...
)

# VM 2: GitOps
vm2 = VirtualMachine(
    hostname="gitops",
    roles="git,docker-registry",
    group="gitops",
    ip="54.123.45.68",  # <-- GitOps public IP
    ...
)

# etc...
```

---

## Step 10: Run Backend (on your computer)

```bash
cd backend
docker compose build
docker compose up -d

# Run installation
docker exec -it backend bash
python3 install.py
```

---

## Troubleshooting

### "Instance type not available"
Change `instance_type = "t2.micro"` in terraform.tfvars

### "Quota exceeded"
KodeKloud may limit instances. Try with only 3 VMs:
- Comment out rkeapp2 and rkeapp3 in main.tf

### "Cannot SSH"
Wait 2-3 minutes for cloud-init to finish:
```bash
ssh devops@<IP> "cloud-init status --wait"
```

### "Permission denied"
Use password authentication:
```bash
ssh devops@<IP>  # Password: devops
```

---

## Cleanup

```bash
terraform destroy -auto-approve
```

**Important**: Always destroy resources before playground expires!
