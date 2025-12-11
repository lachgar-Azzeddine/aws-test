# =============================================================================
# TERRAFORM MAIN CONFIGURATION FOR HARMONISATION TESTING INFRASTRUCTURE
# =============================================================================
# Creates 5 EC2 instances pre-configured for prepare-vms role:
#   - vault (1x)
#   - gitops (1x)
#   - rkeapp1, rkeapp2, rkeapp3 (3x RKE2 nodes)
# =============================================================================

terraform {
  required_version = ">= 1.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

# =============================================================================
# AMI CONFIGURATION - Hardcoded for KodeKloud compatibility
# =============================================================================
# KodeKloud restricts DescribeImages, so we use hardcoded AMI IDs
# Ubuntu 22.04 LTS AMI IDs by region (update if needed)
# =============================================================================

locals {
  ubuntu_ami = {
    "us-east-1" = "ami-0c7217cdde317cfec"  # Ubuntu 22.04 LTS
    "us-east-2" = "ami-05fb0b8c1424f266b"
    "us-west-1" = "ami-0ce2cb35386fc22e9"
    "us-west-2" = "ami-008fe2fc65df48dac"
    "eu-west-1" = "ami-0905a3c97561e0b69"
    "eu-west-2" = "ami-0e5f882be1900e43b"
  }

  # Use the AMI for the selected region, or allow override via variable
  ami_id = var.ami_id != "" ? var.ami_id : local.ubuntu_ami[var.aws_region]
}

# =============================================================================
# SECURITY GROUP
# =============================================================================

resource "aws_security_group" "harmo_sg" {
  name        = "${var.environment}-sg"
  description = "Security group for Harmonisation testing"
  vpc_id      = var.vpc_id

  # SSH
  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
    description = "SSH access"
  }

  # HTTP/HTTPS
  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
    description = "HTTP"
  }

  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
    description = "HTTPS"
  }

  # Kubernetes API
  ingress {
    from_port   = 6443
    to_port     = 6443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
    description = "Kubernetes API"
  }

  # RKE2 ports
  ingress {
    from_port   = 9345
    to_port     = 9345
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
    description = "RKE2 supervisor API"
  }

  # etcd
  ingress {
    from_port   = 2379
    to_port     = 2380
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
    description = "etcd"
  }

  # Vault
  ingress {
    from_port   = 8200
    to_port     = 8200
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
    description = "Vault"
  }

  # Docker Registry
  ingress {
    from_port   = 8443
    to_port     = 8443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
    description = "Docker Registry"
  }

  # Gogs
  ingress {
    from_port   = 3000
    to_port     = 3000
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
    description = "Gogs"
  }

  # NodePort range
  ingress {
    from_port   = 30000
    to_port     = 32767
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
    description = "NodePort services"
  }

  # Allow all internal traffic between instances
  ingress {
    from_port = 0
    to_port   = 0
    protocol  = "-1"
    self      = true
    description = "Internal traffic"
  }

  # Egress - allow all
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
    description = "Allow all outbound"
  }

  tags = {
    Name        = "${var.environment}-sg"
    Environment = var.environment
  }
}

# =============================================================================
# EC2 INSTANCES
# =============================================================================

resource "aws_instance" "harmo_vm" {
  for_each = var.vms

  ami                         = local.ami_id
  instance_type               = var.instance_type
  key_name                    = var.key_name
  subnet_id                   = var.subnet_id
  vpc_security_group_ids      = [aws_security_group.harmo_sg.id]
  associate_public_ip_address = true

  root_block_device {
    volume_size           = var.root_volume_size
    volume_type           = "gp3"
    delete_on_termination = true
    encrypted             = true
  }

  # Data volume for RKE nodes (Longhorn storage)
  dynamic "ebs_block_device" {
    for_each = each.value.group == "RKEAPPS" ? [1] : []
    content {
      device_name           = "/dev/sdb"
      volume_size           = var.data_volume_size
      volume_type           = "gp3"
      delete_on_termination = true
      encrypted             = true
    }
  }

  user_data = base64encode(templatefile("${path.module}/cloud-init.yaml", {
    hostname        = each.key
    devops_password = var.devops_password
    ssh_public_key  = var.ssh_public_key
    base_domain     = var.base_domain
    is_rke_node     = each.value.group == "RKEAPPS"
  }))

  tags = {
    Name        = "${var.environment}-${each.key}"
    Environment = var.environment
    Role        = each.value.role
    Group       = each.value.group
    Roles       = each.value.roles_list
  }

  # Wait for instance to be ready
  lifecycle {
    create_before_destroy = true
  }
}

# =============================================================================
# NOTE: VMs will be ready ~2-3 minutes after terraform apply
# Cloud-init installs Docker, creates devops user, etc.
# Test with: ssh devops@<IP> "cloud-init status"
# =============================================================================
