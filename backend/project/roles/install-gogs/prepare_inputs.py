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


    gitops_vms = get_vms_by_group("gitops",Session)
    gitops_vm = gitops_vms[0]

    prefix = "" if security.env_prefix == "" else security.env_prefix + "-"

    gogs_domain_name = f"{prefix}gogs.{security.base_domain}"

    registry_url = f"{prefix}registry.{security.base_domain}:8443"

    # Variables to pass to Jinja2 templates
    # extra_vars = {"domain_name": gogs_domain_name, "gitops_ip": gitops_vm.ip}

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
            path='gogs/credentials'
        )
        secret_data = secret_response['data']['data']
        username = secret_data.get('username')
        password = secret_data.get('password')

        print("gogs Credentials:")
        print(f"Username: {username}")
        print(f"Password: {password}")

    except hvac.exceptions.InvalidPath:
        print("Error: Secret path 'gogs/credentials' does not exist in 'harmonisation'.")

    if (username == None) or (password == None):
        raise ValueError("Gogs credentials not found or incomplete.")

    extra_vars = {"domain_name": gitops_vm.ip, "gitops_ip": gitops_vm.ip, "registry_url": registry_url, "admin_user": username, "admin_password": password}

    # Dynamic inventory setup
    inventory = {
        "all": {
            "hosts": {
                "gogs-target": {
                    "ansible_host": gitops_vm.ip,
                    "ansible_user": "devops",
                    "ansible_ssh_pass": "devops"
                },
                "localhost": {
                    "ansible_host": "127.0.0.1",
                    "ansible_connection": "local",
                }
            }
        }
    }

    return extra_vars, inventory
