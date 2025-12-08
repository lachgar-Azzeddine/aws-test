import ansible_runner
import os
import tempfile


def my_artifacts_handler(artifacts_dir):
    # Do something here
    print("\nArtifact dir : -------------------------------------------\n")
    print(artifacts_dir)


def my_status_handler(data, runner_config):
    # Do something here
    print("\nStatus handler : -------------------------------------------\n")
    print("runner_ident: " + data.runner_ident + "\n")
    print("status: " + data.status + "\n")


def my_event_handler(data):
    # Do something here
    print("\nEvent handler : -------------------------------------------\n")
    print("runner_ident: " + data.runner_ident + "\n")
    print("event: " + data.event + "\n")
    if hasattr(data, "event_data"):
        if hasattr(data.event_data, "role"):
            print("role: " + data.event_data.role + "\n")
        if hasattr(data.event_data, "task"):
            print("task: " + data.event_data.task + "\n")
    print("stdout: " + data.stdout + "\n")


# Define your SSH private key as a string
ssh_key_string = """
-----BEGIN RSA PRIVATE KEY-----
MIIEpAIBAAKCAQEArw2...
-----END RSA PRIVATE KEY-----
"""

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
            "localhost": {"ansible_host": "127.0.0.1", "ansible_connection": "local"},
        }
    }
}
# get current folder absolute path
current_wd = os.getcwd()
r = ansible_runner.run(
    private_data_dir=current_wd,
    role="testrole",
    artifacts_handler=my_artifacts_handler,
    status_handler=my_status_handler,
    event_handler=my_event_handler,
    extravars=extra_vars,  # Pass extra vars for templates
    inventory=inventory,  # Pass dynamic inventory
)
