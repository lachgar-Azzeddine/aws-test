import tempfile
from repository import get_security, get_vms_by_group


def get_inputs(Session):
    security = get_security(Session)
    if security is None:
        print("Could not load the module spec for security")
        exit(1)
    # Define your SSH private key as a string
    ssh_key_string = security.ssh_pulic_key
    # Write the SSH key to a temporary file
    with tempfile.NamedTemporaryFile(delete=False, mode="w") as key_file:
        key_file.write(ssh_key_string)
        key_file_path = key_file.name

    prefix = "" if security.env_prefix == "" else security.env_prefix + "-"
    gogs_url = f"{prefix}gogs.{security.base_domain}"
    gogs_ip = get_vms_by_group("gitops",Session)[0].ip

    registry_url = f"{prefix}registry.{security.base_domain}:8443"

    # Variables to pass to Jinja2 templates
    extra_vars = {"variable1": "value1", "variable2": "value2", "gogs_url": gogs_url, "gogs_ip": gogs_ip, "registry_url": registry_url}

    # Dynamic inventory setup
    inventory = {
        "all": {
            "hosts": {
                "localhost": {
                    "ansible_host": "127.0.0.1",
                    "ansible_connection": "local",
                },
            }
        }
    }

    return extra_vars, inventory
