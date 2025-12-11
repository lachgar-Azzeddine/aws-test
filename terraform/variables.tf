# =============================================================================
# TERRAFORM VARIABLES FOR HARMONISATION TESTING INFRASTRUCTURE
# =============================================================================

variable "aws_region" {
  description = "AWS region to deploy resources"
  type        = string
  default     = "eu-west-1"
}

variable "instance_type" {
  description = "EC2 instance type"
  type        = string
  default     = "t3.medium"
}

variable "key_name" {
  description = "Name of the SSH key pair in AWS"
  type        = string
}

variable "vpc_id" {
  description = "VPC ID where instances will be created"
  type        = string
}

variable "subnet_id" {
  description = "Subnet ID for the instances"
  type        = string
}

variable "environment" {
  description = "Environment name (prefix for resources)"
  type        = string
  default     = "harmo-test"
}

variable "devops_password" {
  description = "Password for devops user (will be hashed)"
  type        = string
  sensitive   = true
  default     = "devops"
}

variable "ssh_public_key" {
  description = "SSH public key content for devops user"
  type        = string
}

variable "base_domain" {
  description = "Base domain for services (e.g., example.com)"
  type        = string
  default     = "local"
}

# VM Configuration (target VMs - not including backend)
variable "vms" {
  description = "Map of VMs to create"
  type = map(object({
    role       = string
    group      = string
    roles_list = string
  }))
  default = {
    "vault" = {
      role       = "vault"
      group      = "vault"
      roles_list = "vault"
    }
    "gitops" = {
      role       = "gitops"
      group      = "gitops"
      roles_list = "git,docker-registry"
    }
    "rkeapp1" = {
      role       = "rke2"
      group      = "RKEAPPS"
      roles_list = "master,worker,cns"
    }
    "rkeapp2" = {
      role       = "rke2"
      group      = "RKEAPPS"
      roles_list = "master,worker,cns"
    }
    "rkeapp3" = {
      role       = "rke2"
      group      = "RKEAPPS"
      roles_list = "master,worker,cns"
    }
  }
}


# Disk sizes
variable "root_volume_size" {
  description = "Root volume size in GB"
  type        = number
  default     = 50
}

variable "data_volume_size" {
  description = "Data volume size in GB (for RKE nodes)"
  type        = number
  default     = 100
}
