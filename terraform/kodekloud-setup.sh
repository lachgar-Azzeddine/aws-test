#!/bin/bash
# =============================================================================
# KODEKLOUD PLAYGROUND SETUP SCRIPT
# =============================================================================
# Run this script inside KodeKloud AWS Playground terminal
# It will:
#   1. Get VPC/Subnet IDs
#   2. Create SSH key pair
#   3. Generate terraform.tfvars
#   4. Run Terraform to create VMs
# =============================================================================

set -e

echo "=========================================="
echo "  KodeKloud Harmonisation Setup"
echo "=========================================="

# Check AWS credentials
echo "[1/6] Checking AWS credentials..."
aws sts get-caller-identity > /dev/null 2>&1 || {
    echo "ERROR: AWS credentials not configured!"
    exit 1
}
echo "✓ AWS credentials OK"

# Get region
AWS_REGION=$(aws configure get region || echo "us-east-1")
echo "  Region: $AWS_REGION"

# Get VPC ID
echo ""
echo "[2/6] Getting VPC ID..."
VPC_ID=$(aws ec2 describe-vpcs --query 'Vpcs[0].VpcId' --output text)
echo "✓ VPC ID: $VPC_ID"

# Get Subnet ID
echo ""
echo "[3/6] Getting Subnet ID..."
SUBNET_ID=$(aws ec2 describe-subnets --query 'Subnets[0].SubnetId' --output text)
echo "✓ Subnet ID: $SUBNET_ID"

# Create SSH key pair
echo ""
echo "[4/6] Creating SSH key pair..."
KEY_NAME="harmo-key"
KEY_FILE="$HOME/.ssh/${KEY_NAME}.pem"

# Delete existing key if present
aws ec2 delete-key-pair --key-name $KEY_NAME 2>/dev/null || true
rm -f $KEY_FILE

# Create new key
mkdir -p $HOME/.ssh
aws ec2 create-key-pair --key-name $KEY_NAME --query 'KeyMaterial' --output text > $KEY_FILE
chmod 600 $KEY_FILE

# Generate public key from private key
ssh-keygen -y -f $KEY_FILE > ${KEY_FILE%.pem}.pub
SSH_PUBLIC_KEY=$(cat ${KEY_FILE%.pem}.pub)

echo "✓ SSH key created: $KEY_FILE"

# Generate terraform.tfvars
echo ""
echo "[5/6] Generating terraform.tfvars..."
cat > terraform.tfvars << EOF
# Auto-generated for KodeKloud Playground
# Generated at: $(date)

aws_region    = "$AWS_REGION"
key_name      = "$KEY_NAME"
vpc_id        = "$VPC_ID"
subnet_id     = "$SUBNET_ID"
environment   = "harmo-test"

# Use t2.micro if t3.medium is restricted
instance_type = "t3.medium"

# Smaller disks for playground
root_volume_size = 30
data_volume_size = 50

devops_password = "devops"
base_domain     = "local"

ssh_public_key = "$SSH_PUBLIC_KEY"
EOF

echo "✓ terraform.tfvars created"

# Initialize and apply Terraform
echo ""
echo "[6/6] Running Terraform..."
echo ""

# Check if terraform is installed
if ! command -v terraform &> /dev/null; then
    echo "Installing Terraform..."
    sudo yum install -y yum-utils || sudo apt-get update
    sudo yum-config-manager --add-repo https://rpm.releases.hashicorp.com/AmazonLinux/hashicorp.repo 2>/dev/null || \
    wget -O- https://apt.releases.hashicorp.com/gpg | sudo gpg --dearmor -o /usr/share/keyrings/hashicorp-archive-keyring.gpg
    echo "deb [signed-by=/usr/share/keyrings/hashicorp-archive-keyring.gpg] https://apt.releases.hashicorp.com $(lsb_release -cs) main" | sudo tee /etc/apt/sources.list.d/hashicorp.list
    sudo apt update && sudo apt install terraform -y 2>/dev/null || sudo yum install terraform -y
fi

terraform init
terraform apply -auto-approve

echo ""
echo "=========================================="
echo "  SETUP COMPLETE!"
echo "=========================================="
echo ""
echo "VM Public IPs:"
terraform output -json vm_details | jq -r 'to_entries[] | "  \(.key): \(.value.public_ip)"'
echo ""
echo "SSH Command:"
echo "  ssh -i $KEY_FILE devops@<PUBLIC_IP>"
echo ""
echo "Next Steps:"
echo "  1. Copy the IPs above"
echo "  2. Update backend/initial_db.py with the IPs"
echo "  3. On your computer: docker compose up -d"
echo "  4. Run: docker exec -it backend python3 install.py"
echo ""
