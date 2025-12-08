
#===============================================================================
# Vsphere Configuration
#===============================================================================
vsphere_server                    = "dcvcenter.wnet"
vsphere_user                      = "marabbah@.wnet"
vsphere_password                  = ""
vsphere_datacenter                = ""
vsphere_host                      = "Dev_Environnement/10.97.97.10"
vsphere_datastore                 = "VM_SAP_AUTRES_01_43"
vsphere_network_name              = "VLAN_236"
# vsphere_machine_type              = "otherLinux64Guest"
#===============================================================================
# Machines general Configuration
#===============================================================================

machine_prefix                    = "hamonisation"

#===============================================================================
# Machines general Network Configuration
#===============================================================================
machine_network_dns               = "10.97.242.3,10.97.242.4"
machine_network_gateway           = "10.97.235.65"
machine_network_mask              = "26"
machine_domain                    = "l.local"
#===============================================================================
# Machines
#===============================================================================



machines = [
{
  name           = "rkeapp1"
  group          = "RKEAPPS"
  vm_role        = "master,worker,cns"
  ip             = "10.97.235.80"
  status         = "to_create"
  zone_id        = "4"
  cpu            = "4"
  ram            = "16384"
  os_disk_size   = "80"
  data_disk_size = "100"
},
{
  name           = "rkeapp2"
  group          = "RKEAPPS"
  vm_role        = "master,worker,cns"
  ip             = "10.97.235.81"
  status         = "to_create"
  zone_id        = "4"
  cpu            = "4"
  ram            = "16384"
  os_disk_size   = "80"
  data_disk_size = "100"
},
{
  name           = "rkeapp3"
  group          = "RKEAPPS"
  vm_role        = "master,worker,cns"
  ip             = "10.97.235.82"
  status         = "to_create"
  zone_id        = "4"
  cpu            = "4"
  ram            = "16384"
  os_disk_size   = "80"
  data_disk_size = "100"
},
{
  name           = "rkemiddleware1"
  group          = "RKEMIDDLEWARE"
  vm_role        = "master,worker,cns"
  ip             = "10.97.235.83"
  status         = "to_create"
  zone_id        = "4"
  cpu            = "4"
  ram            = "16384"
  os_disk_size   = "80"
  data_disk_size = "100"
},
{
  name           = "rkemiddleware2"
  group          = "RKEMIDDLEWARE"
  vm_role        = "master,worker,cns"
  ip             = "10.97.235.84"
  status         = "to_create"
  zone_id        = "4"
  cpu            = "4"
  ram            = "16384"
  os_disk_size   = "80"
  data_disk_size = "100"
},
{
  name           = "rkemiddelware3"
  group          = "RKEMIDDLEWARE"
  vm_role        = "master,worker,cns"
  ip             = "10.97.235.85"
  status         = "to_create"
  zone_id        = "4"
  cpu            = "4"
  ram            = "16384"
  os_disk_size   = "80"
  data_disk_size = "100"
},
{
  name           = "lb1"
  group          = "LBLAN"
  vm_role        = "loadbalancer"
  ip             = "10.97.235.86"
  status         = "to_create"
  zone_id        = "4"
  cpu            = "4"
  ram            = "4096"
  os_disk_size   = "60"
  data_disk_size = "0"
},
{
  name           = "gitops"
  group          = "gitops"
  vm_role        = "git,docker-registry"
  ip             = "10.97.235.87"
  status         = "to_create"
  zone_id        = "4"
  cpu            = "4"
  ram            = "8192"
  os_disk_size   = "60"
  data_disk_size = "200"
},
{
  name           = "monitoring"
  group          = "monitoring"
  vm_role        = "admin,monitoring"
  ip             = "10.97.235.88"
  status         = "to_create"
  zone_id        = "4"
  cpu            = "4"
  ram            = "16384"
  os_disk_size   = "80"
  data_disk_size = "200"
},
{
  name           = "vault"
  group          = "vault"
  vm_role        = "vault"
  ip             = "10.97.235.89"
  status         = "to_create"
  zone_id        = "4"
  cpu            = "4"
  ram            = "16384"
  os_disk_size   = "80"
  data_disk_size = "200"
},
]
