import tempfile
import secrets
import string
from repository import get_security
import tempfile
from repository import (
    get_security,
    get_virtual_machines,
)


def generate_password(length=16):
    # Define the character set for the password
    characters = string.ascii_letters + string.digits
    # Generate a secure random password
    password = "".join(secrets.choice(characters) for _ in range(length))
    return password

def get_inputs(Session):
    security = get_security(Session)
    all_VMs = get_virtual_machines(Session)
    if security is None:
        print("Could not load the module spec for security")
        exit(1)
    # Define your SSH private key as a string
    ssh_public_key_string = security.ssh_pulic_key
    ssh_private_key_string = security.ssh_private_key
    domain = security.base_domain
    prefix = "" if security.env_prefix == "" else security.env_prefix + "-"
    gogs_domain = prefix + "gogs." + domain
    registry_domain = prefix + "registry." + domain
    http_proxy = security.porxy_host + ":" + security.proxy_port
    no_proxy = f"localhost,127.0.0.1,*.{domain}"
    use_proxy= security.use_proxy
    use_proxy = 0
    vm_dict = {
        vm.id: {"name": vm.hostname, "group": vm.group, "IP": vm.ip} for vm in all_VMs
    }

    output_file = "/home/devops/data/project/roles/prepare-vms/files/hosts"

    # Write the VM names and IPs to the file
    with open(output_file, "w") as f:
        f.write(
            "127.0.0.1   localhost\n::1         localhost\n4.251.124.139  harmonisation.docker\n"
        )
        for vm_info in vm_dict.values():
            if vm_info["group"] == "gitops":
                f.write(
                    vm_info["IP"]
                    + " "
                    + vm_info["name"]
                    + "."
                    + domain
                    + " "
                    + gogs_domain
                    + " "
                    + registry_domain
                    + "\n"
                )
            else:
                f.write(vm_info["IP"] + " " + vm_info["name"] + "." + domain + "" "\n")

    # Write the SSH key to a temporary file
    with tempfile.NamedTemporaryFile(delete=False, mode="w") as public_key_file:
        public_key_file.write(ssh_public_key_string)
        public_key_file_path = public_key_file.name
    with tempfile.NamedTemporaryFile(delete=False, mode="w") as private_key_file:
        private_key_file.write(ssh_private_key_string)
        private_key_file_path = private_key_file.name

    root_password = generate_password(16)
    # print(private_key_file_path)

    # Variables to pass to Jinja2 templates
    extra_vars = {
        "use_proxy": use_proxy,
        "no_proxy": no_proxy,
        "http_proxy": http_proxy,
        "docker_username": "devops",
        "docker_password": "devops",
        "root_password": root_password,
        "public_key_file_path": public_key_file_path,
        "private_key_file_path": private_key_file_path,
        "local_private_key": "~/.ssh/id_rsa",
        "local_public_key": "~/.ssh/id_rsa.pub",
        "authorized_keys_path": "~/.ssh/authorized_keys",
        "ssh_dir": "~/.ssh",
        "devops_username": "devops",
        "devops_home": "/home/devops",
        "prefix": prefix
    }
    inventory = {
        "localhost": {"hosts": {"localhost": {"ansible_connection": "local"}}},
        "RKE": {"hosts": {}},
        "registry": {"hosts": {}},
        "docker": {"hosts": {}},
    }

    # Categorize VMs into groups based on their 'group' attribute
    for vm_name, details in vm_dict.items():
        if "rke" in details["group"].lower():
            inventory["RKE"]["hosts"][details["name"]] = {
                "ansible_host": details["IP"],
                "ansible_user": "devops",
                "ansible_ssh_pass": "devops",
            }
        elif "gitops" in details["group"].lower():
            inventory["registry"]["hosts"][details["name"]] = {
                "ansible_host": details["IP"],
                "ansible_user": "devops",
                "ansible_ssh_pass": "devops",
            }
        else:
            inventory["docker"]["hosts"][details["name"]] = {
                "ansible_host": details["IP"],
                "ansible_user": "devops",
                "ansible_ssh_pass": "devops",
            }
    print(inventory)

    return extra_vars, inventory

