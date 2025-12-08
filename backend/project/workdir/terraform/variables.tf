variable "vsphere_server" {
  description = "vSphere server"
  type        = string
}

variable "vsphere_user" {
  description = "vSphere username"
  type        = string
}

variable "vsphere_password" {
  description = "vSphere password"
  type        = string
}

variable "vsphere_datacenter" {
  description = "vSphere data center"
  type        = string
}

# variable "vsphere_cluster" {
#   description = "vSphere cluster"
#   type        = string
# }

variable "vsphere_datastore" {
  description = "vSphere datastore"
  type        = string
}

# variable "vsphere_vm_folder" {
#   description = "vSphere folder"
#   type        = string
# }



# variable "vsphere_machine_type" {
#   description = "vSphere machine type"
#   type        = string
# }

# variable "vsphere_machine_template" {
#   description = "vSphere machine template"
#   type        = string
# }


variable "vsphere_network_name" {
  description = "vSphere network name"
  type        = string
}


# variable "vsphere_resource_pool" {
#   description = "vsphere resource pool"
#   type        = string
# }


variable "vsphere_host" {
  description = "vsphere resource pool"
  type        = string
}



#===============================================================================
# Machines
#===============================================================================


variable "username" {
  description = "username machine"
  type        = string
  default = "root"
}


variable "password" {
  description = "password machine"
  type        = string
  default = "packer"
}


variable "machine_prefix" {
  description = "machine name prefix"
  type        = string
}

variable "machine_network_dns" {
  description = "machine network dns"
  type        = string
}

variable "machine_network_gateway" {
  description = "machine network gateway"
  type        = string
}

variable "machine_network_mask" {
  description = "machine network mask"
  type        = string
}

variable "machine_domain" {
  description = "machine domaine"
  type        = string
}

variable "machines" {
  description = "List of machine definitions"
  type = list(object({
    name           = string
    group          = string
    vm_role        = string
    ip             = string
    status         = string
    zone_id        = string
    cpu            = string
    ram            = string
    os_disk_size   = string
    data_disk_size = string
  }))
}

# variable "providers_path" {
#   description = "providers_path"
#   type        = string
# }

# variable "ova_path" {
#   description = "ova_path"
#   type        = string
# }