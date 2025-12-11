# =============================================================================
# TERRAFORM OUTPUTS FOR HARMONISATION TESTING INFRASTRUCTURE
# =============================================================================

output "vm_details" {
  description = "Details of all created VMs"
  value = {
    for name, instance in aws_instance.harmo_vm : name => {
      hostname   = name
      public_ip  = instance.public_ip
      private_ip = instance.private_ip
      group      = instance.tags["Group"]
      roles      = instance.tags["Roles"]
    }
  }
}

output "vault_ip" {
  description = "Public IP of Vault VM"
  value       = aws_instance.harmo_vm["vault"].public_ip
}

output "gitops_ip" {
  description = "Public IP of GitOps VM"
  value       = aws_instance.harmo_vm["gitops"].public_ip
}

output "rke_ips" {
  description = "Public IPs of RKE2 VMs"
  value = {
    rkeapp1 = aws_instance.harmo_vm["rkeapp1"].public_ip
    rkeapp2 = aws_instance.harmo_vm["rkeapp2"].public_ip
    rkeapp3 = aws_instance.harmo_vm["rkeapp3"].public_ip
  }
}

output "all_private_ips" {
  description = "Private IPs of all VMs (for internal communication)"
  value = {
    for name, instance in aws_instance.harmo_vm : name => instance.private_ip
  }
}

# Output for initial_db.py configuration
output "initial_db_config" {
  description = "Configuration to paste into initial_db.py"
  value = <<-EOT

# =============================================================================
# COPY THIS TO initial_db.py - VM CONFIGURATION FROM TERRAFORM
# =============================================================================

# VM 1: Vault
vm1 = VirtualMachine(
    hostname="${aws_instance.harmo_vm["vault"].tags["Name"]}",
    roles="vault",
    group="vault",
    ip="${aws_instance.harmo_vm["vault"].private_ip}",
    nb_cpu=2,
    ram=4096,
    os_disk_size=${var.root_volume_size},
    data_disk_size=0,
    zone_id=zone1.id,
    status="created",
)
session.add(vm1)

# VM 2: GitOps
vm2 = VirtualMachine(
    hostname="${aws_instance.harmo_vm["gitops"].tags["Name"]}",
    roles="git,docker-registry",
    group="gitops",
    ip="${aws_instance.harmo_vm["gitops"].private_ip}",
    nb_cpu=2,
    ram=4096,
    os_disk_size=${var.root_volume_size},
    data_disk_size=0,
    zone_id=zone1.id,
    status="created",
)
session.add(vm2)

# VM 3: RKE App 1
vm3 = VirtualMachine(
    hostname="${aws_instance.harmo_vm["rkeapp1"].tags["Name"]}",
    roles="master,worker,cns",
    group="RKEAPPS",
    ip="${aws_instance.harmo_vm["rkeapp1"].private_ip}",
    nb_cpu=2,
    ram=4096,
    os_disk_size=${var.root_volume_size},
    data_disk_size=${var.data_volume_size},
    zone_id=zone1.id,
    status="created",
)
session.add(vm3)

# VM 4: RKE App 2
vm4 = VirtualMachine(
    hostname="${aws_instance.harmo_vm["rkeapp2"].tags["Name"]}",
    roles="master,worker,cns",
    group="RKEAPPS",
    ip="${aws_instance.harmo_vm["rkeapp2"].private_ip}",
    nb_cpu=2,
    ram=4096,
    os_disk_size=${var.root_volume_size},
    data_disk_size=${var.data_volume_size},
    zone_id=zone1.id,
    status="created",
)
session.add(vm4)

# VM 5: RKE App 3
vm5 = VirtualMachine(
    hostname="${aws_instance.harmo_vm["rkeapp3"].tags["Name"]}",
    roles="master,worker,cns",
    group="RKEAPPS",
    ip="${aws_instance.harmo_vm["rkeapp3"].private_ip}",
    nb_cpu=2,
    ram=4096,
    os_disk_size=${var.root_volume_size},
    data_disk_size=${var.data_volume_size},
    zone_id=zone1.id,
    status="created",
)
session.add(vm5)

EOT
}

# JSON output for automation
output "vm_config_json" {
  description = "VM configuration in JSON format for automation"
  value = jsonencode({
    vms = [
      {
        hostname       = "vault"
        ip             = aws_instance.harmo_vm["vault"].private_ip
        public_ip      = aws_instance.harmo_vm["vault"].public_ip
        group          = "vault"
        roles          = "vault"
        nb_cpu         = 2
        ram            = 4096
        os_disk_size   = var.root_volume_size
        data_disk_size = 0
      },
      {
        hostname       = "gitops"
        ip             = aws_instance.harmo_vm["gitops"].private_ip
        public_ip      = aws_instance.harmo_vm["gitops"].public_ip
        group          = "gitops"
        roles          = "git,docker-registry"
        nb_cpu         = 2
        ram            = 4096
        os_disk_size   = var.root_volume_size
        data_disk_size = 0
      },
      {
        hostname       = "rkeapp1"
        ip             = aws_instance.harmo_vm["rkeapp1"].private_ip
        public_ip      = aws_instance.harmo_vm["rkeapp1"].public_ip
        group          = "RKEAPPS"
        roles          = "master,worker,cns"
        nb_cpu         = 2
        ram            = 4096
        os_disk_size   = var.root_volume_size
        data_disk_size = var.data_volume_size
      },
      {
        hostname       = "rkeapp2"
        ip             = aws_instance.harmo_vm["rkeapp2"].private_ip
        public_ip      = aws_instance.harmo_vm["rkeapp2"].public_ip
        group          = "RKEAPPS"
        roles          = "master,worker,cns"
        nb_cpu         = 2
        ram            = 4096
        os_disk_size   = var.root_volume_size
        data_disk_size = var.data_volume_size
      },
      {
        hostname       = "rkeapp3"
        ip             = aws_instance.harmo_vm["rkeapp3"].private_ip
        public_ip      = aws_instance.harmo_vm["rkeapp3"].public_ip
        group          = "RKEAPPS"
        roles          = "master,worker,cns"
        nb_cpu         = 2
        ram            = 4096
        os_disk_size   = var.root_volume_size
        data_disk_size = var.data_volume_size
      }
    ]
    zone = {
      sub_network  = cidrsubnet(data.aws_subnet.selected.cidr_block, 0, 0)
      network_mask = split("/", data.aws_subnet.selected.cidr_block)[1]
      gateway      = cidrhost(data.aws_subnet.selected.cidr_block, 1)
    }
  })
}

# SSH connection commands
output "ssh_commands" {
  description = "SSH commands to connect to VMs"
  value = <<-EOT

# SSH Commands (using devops user):
ssh devops@${aws_instance.harmo_vm["vault"].public_ip}    # Vault
ssh devops@${aws_instance.harmo_vm["gitops"].public_ip}   # GitOps
ssh devops@${aws_instance.harmo_vm["rkeapp1"].public_ip}  # RKE App 1
ssh devops@${aws_instance.harmo_vm["rkeapp2"].public_ip}  # RKE App 2
ssh devops@${aws_instance.harmo_vm["rkeapp3"].public_ip}  # RKE App 3

EOT
}
