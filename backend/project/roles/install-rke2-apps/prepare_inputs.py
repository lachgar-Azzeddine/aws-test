import tempfile
from repository import (
    get_security,
    get_vms_by_group,
)


def get_inputs(Session):
    security = get_security(Session)
    cluster_name = "RKE2-APPS"
    all_VMs = get_vms_by_group("RKEAPPS", Session)
    if security is None:
        print("Could not load the module spec for security")
        exit(1)
    # Define your SSH private key as a string
    ssh_key_string = security.ssh_pulic_key
    # Write the SSH key to a temporary file
    with tempfile.NamedTemporaryFile(delete=False, mode="w") as key_file:
        key_file.write(ssh_key_string)

    prefix = "" if security.env_prefix == "" else security.env_prefix + "-"

    registry_url = f"{prefix}registry.{security.base_domain}:8443"

    # Variables to pass to Jinja2 templates
    extra_vars = {
        "cluster_name": cluster_name,
        "rke2_config_dir": "/etc/rancher/rke2",
        "kubeconfig_file": "/home/devops/.kube/config.yaml",
        "install_script": "/home/devops/rke2-artifacts/install.sh",
        "token": "RKE-token",
        "kubeconfig_mode": "0644",
        "registry_url": registry_url,
        "prefix": prefix
    }

    is_first_master = True

    vm_dict = {
        vm.id: {
            "name": vm.hostname,
            "Group": vm.group,
            "IP": vm.ip,
            "roles": vm.roles,
            "zone_ID": vm.zone_id,
            "status": vm.status,
        }
        for vm in all_VMs
        if vm.status == "created"
    }
    inventory = {
        "localhost": {"hosts": {"localhost": {"ansible_connection": "local"}}},
        "initial_master": {"hosts": {}},
        "masters": {"hosts": {}},
        "workers": {"hosts": {}},
        "cns": {"hosts": {}},
    }

    for vm_name, details in vm_dict.items():
        roles = details["roles"]

        # Check if 'master' is in roles
        if "master" in roles:
            if is_first_master:
                inventory["initial_master"]["hosts"][details["name"]] = {
                    "ansible_host": details["IP"],
                    "ansible_user": "devops",
                }
                is_first_master = False
            else:
                inventory["masters"]["hosts"][details["name"]] = {
                    "ansible_host": details["IP"],
                    "ansible_user": "devops",
                }
        # Only add to workers if 'master' is not in roles but 'worker' is
        elif "worker" in roles:
            inventory["workers"]["hosts"][details["name"]] = {
                "ansible_host": details["IP"],
                "ansible_user": "devops",
            }
        if "cns" in roles:
            inventory["cns"]["hosts"][details["name"]] = {
                "ansible_host": details["IP"],
                "ansible_user": "devops",
            }

    # print(extra_vars)
    # print('hello\nworld')

    # for vm in all_VMs:
    #     vm_dict[vm.id] = {
    #         'name': vm.hostname,
    #         'Group' : vm.group,
    #         'IP' : vm.ip,
    #         'zone_ID' : vm.zone_id,
    #         'status' : vm.status
    #     }
    print(inventory)
    # print(vm_dict)
    # print(f"ID: {vm.id}, Name: {vm.hostname}, Group: {vm.group}, IP: {vm.ip}, zode_id: {vm.zone_id},status: {vm.status}")
    return extra_vars, inventory
