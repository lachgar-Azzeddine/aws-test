# =============================================================================
# KODEKLOUD PLAYGROUND CONFIGURATION
# =============================================================================
# Instructions:
# 1. Open KodeKloud AWS Playground
# 2. Get your VPC ID: aws ec2 describe-vpcs --query 'Vpcs[0].VpcId' --output text
# 3. Get your Subnet ID: aws ec2 describe-subnets --query 'Subnets[0].SubnetId' --output text
# 4. Create SSH key: aws ec2 create-key-pair --key-name harmo-key --query 'KeyMaterial' --output text > harmo-key.pem
# 5. Update values below
# =============================================================================

# AWS Region - KodeKloud usually uses us-east-1
aws_region = "us-east-1"

# Availability Zone - t3.medium NOT supported in us-east-1e
# Choose from: us-east-1a, us-east-1b, us-east-1c, us-east-1d, us-east-1f
availability_zone = "us-east-1a"

# SSH Key pair name (create it first - see instructions above)
key_name = "harmo-key"

# VPC and Subnet - get from KodeKloud (run commands above)
vpc_id    = "vpc-xxxxxxxxx"    # REPLACE with your VPC ID
subnet_id = "subnet-xxxxxxxxx" # REPLACE with your Subnet ID

# Environment prefix
environment = "harmo-test"

# Instance type - t3.medium should work, use t2.micro if restricted
instance_type = "t3.medium"

# Disk sizes (smaller for playground)
root_volume_size = 30
data_volume_size = 50

# DevOps password
devops_password = "devops"

# SSH public key - will be generated in setup script
ssh_public_key = ""

# Base domain
base_domain = "local"
