#===============================================================================
# Providers config
#===============================================================================
provider "vsphere" {
  vsphere_server       = var.vsphere_server
  user                 = var.vsphere_user
  password             = var.vsphere_password
  allow_unverified_ssl = true
}

#===============================================================================
# vSphere Data
#===============================================================================
data "vsphere_datacenter" "dc" {
  name = var.vsphere_datacenter
}

data "vsphere_datastore" "datastore" {
  name          = var.vsphere_datastore
  datacenter_id = data.vsphere_datacenter.dc.id
}

data "vsphere_network" "network" {
  name          = var.vsphere_network_name
  datacenter_id = data.vsphere_datacenter.dc.id
}

data "vsphere_host" "host" {
  name          = var.vsphere_host
  datacenter_id = data.vsphere_datacenter.dc.id
}

data "vsphere_resource_pool" "harmonisation_pool" {
  name          = "harmonisation_pool"
  datacenter_id = data.vsphere_datacenter.dc.id
}

# Define the templates
data "vsphere_virtual_machine" "rke" {
  name          = "/${var.vsphere_datacenter}/vm/rke-agents"
  datacenter_id = data.vsphere_datacenter.dc.id
}

data "vsphere_virtual_machine" "rhel9" {
  name          = "/${var.vsphere_datacenter}/vm/rhel9-agents"
  datacenter_id = data.vsphere_datacenter.dc.id
}

data "vsphere_virtual_machine" "rhel9_docker" {
  name          = "/${var.vsphere_datacenter}/vm/rhel9-docker-agents"
  datacenter_id = data.vsphere_datacenter.dc.id
}

locals {
  template_mapping = {
    "RKEAPPS"       = data.vsphere_virtual_machine.rke.id
    "RKEMIDDLEWARE" = data.vsphere_virtual_machine.rke.id
    "LBLAN"         = data.vsphere_virtual_machine.rhel9_docker.id
    "gitops"        = data.vsphere_virtual_machine.rhel9_docker.id
    "monitoring"    = data.vsphere_virtual_machine.rhel9_docker.id
    "vault"         = data.vsphere_virtual_machine.rhel9_docker.id
  }

}

resource "vsphere_virtual_machine" "machine" {
  count            = length(var.machines)
  name             = "${var.machine_prefix}-${var.machines[count.index].name}"
  resource_pool_id = data.vsphere_resource_pool.harmonisation_pool.id
  datastore_id     = data.vsphere_datastore.datastore.id
  guest_id         = "otherGuest"

  num_cpus = tonumber(var.machines[count.index].cpu)
  memory   = tonumber(var.machines[count.index].ram)

  network_interface {
    network_id   = data.vsphere_network.network.id
    adapter_type = "vmxnet3"
  }

  disk {
    label            = "disk0"
    size             = var.machines[count.index].os_disk_size
    eagerly_scrub    = false
    thin_provisioned = true
    unit_number      = 0
  }

  dynamic "disk" {
  for_each = tonumber(var.machines[count.index].data_disk_size) > 0 ? ["apply"] : []
  content {
    label            = "disk1"
    size             = var.machines[count.index].data_disk_size
    eagerly_scrub    = false
    thin_provisioned = true
    unit_number      = 1
  }
}

  clone {
    template_uuid = lookup(local.template_mapping, var.machines[count.index].group)
  }

  extra_config = {
  "guestinfo.userdata" = base64encode(templatefile("./cloud-init/userdata.yaml", {
    mount_point = (
      tonumber(var.machines[count.index].data_disk_size) > 0 ? (
        var.machines[count.index].group == "RKEAPPS" || 
        var.machines[count.index].group == "RKEMIDDLEWARE"
      ) ? "/var/lib/longhorn" : "/data"
      : ""
    )
    vm_name    = var.machines[count.index].name
  }))

  "guestinfo.userdata.encoding" = "base64"

  "guestinfo.metadata" = base64encode(templatefile("./cloud-init/metadata.yaml", {
    vm_ip      = var.machines[count.index].ip
    vm_name    = var.machines[count.index].name
  }))

  "guestinfo.metadata.encoding" = "base64"
}
}

