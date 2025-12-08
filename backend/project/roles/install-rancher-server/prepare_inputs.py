import tempfile, hvac
from repository import get_security, get_vms_by_group, get_vault_token


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

    admin_vms = get_vms_by_group("monitoring", Session)
    admin_vm = admin_vms[0]

    gitops_vms = get_vms_by_group("gitops",Session)
    gitops_vm = gitops_vms[0]

    registry_url = f"{prefix}registry.{security.base_domain}:8443"

    vault_ip = get_vms_by_group("vault", Session)[0].ip

    vault_token = get_vault_token(Session)
    print(vault_token)
    client = hvac.Client(url=f'https://{vault_ip}:8200', verify=False, token=vault_token) 

    # Check if Vault is initialized and unsealed
    if not client.is_authenticated():
        raise Exception("Vault authentication failed.")

    username = None
    password = None

    try:
        secret_response = client.secrets.kv.v2.read_secret_version(
            mount_point='harmonisation',
            path='rancher/credentials'
        )
        secret_data = secret_response['data']['data']
        username = secret_data.get('username')
        password = secret_data.get('password')

        print("Rancher Credentials:")
        print(f"Username: {username}")
        print(f"Password: {password}")

    except hvac.exceptions.InvalidPath:
        print("Error: Secret path 'gogs/credentials' does not exist in 'harmonisation'.")

    # Variables to pass to Jinja2 templates
    extra_vars = {"rancher_version": "v2.10-head", "rancher_port": "80","rancher_ssl_port":"443","rancher_admin_password": password,"kubeconfig":"/home/devops/.kube/config","rancher_server_ip":admin_vm.ip,"registry_url":registry_url,"prefix":prefix}

    # Dynamic inventory setup
    inventory = {
        "all": {
            "hosts": {
                "localhost": {
                    "ansible_host": "127.0.0.1",
                    "ansible_connection": "local",
                },
                "rancher-server": {
                    "ansible_host": admin_vm.ip,
                    "ansible_user": "devops"
                },
                "registry": {
                    "ansible_host": gitops_vm.ip,
                    "ansible_user": "devops"
                }
            }
        }
    }

    print(extra_vars)
    print(inventory)

    return extra_vars, inventory
