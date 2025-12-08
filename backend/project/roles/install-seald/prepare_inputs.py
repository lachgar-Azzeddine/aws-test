import tempfile
from repository import get_security


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

    # Variables to pass to Jinja2 templates
    extra_vars = {"variable1": "value1", "variable2": "value2"}

    # Dynamic inventory setup
    inventory = {
        "all": {
            "hosts": {
                "host1": {
                    "ansible_host": "192.168.1.10",
                    "ansible_user": "admin",
                    "ansible_ssh_private_key_file": key_file_path,
                },
                "host2": {
                    "ansible_host": "192.168.1.11",
                    "ansible_user": "admin",
                    "ansible_ssh_private_key_file": key_file_path,
                },
                "localhost": {
                    "ansible_host": "127.0.0.1",
                    "ansible_connection": "local",
                },
            }
        }
    }

    return extra_vars, inventory
