import tempfile, hvac
from repository import get_security, get_vault_token
from repository import (
    get_virtual_machines,
    get_vms_by_group
)



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
    pem_content= security.pem_certificate

    private_key_start = "-----BEGIN PRIVATE KEY-----"
    private_key_end = "-----END PRIVATE KEY-----"
    certificate_start = "-----BEGIN CERTIFICATE-----"
    certificate_end = "-----END CERTIFICATE-----"
    key_file= "/tmp/minio-crts/domain.key"
    cert_file= "/tmp/minio-certs/domain.crt"
    # Extract the private key
    private_key = pem_content[
        pem_content.find(private_key_start) : pem_content.find(private_key_end) + len(private_key_end)
    ]
    # print("private key:\n"+private_key)
    # Extract the certificate
    certificate = pem_content[
        pem_content.find(certificate_start) : pem_content.find(certificate_end) + len(certificate_end)
    ]
    # print("certificate:\n"+certificate)
    all_VMs = get_virtual_machines(Session)
    # Define your SSH private key as a string

    vm_dict= {
        vm.id: {
            'name': vm.hostname,
            'group': vm.group,
            'IP' : vm.ip,
            'roles' : vm.roles,
        }
        for vm in all_VMs 
    }
    # Variables to pass to Jinja2 templates

    # Dynamic inventory setup
    inventory = {
        'localhost': {'hosts': {'localhost': {'ansible_connection': 'local'}}},
        'registry': {'hosts': {}},
        'docker': {'hosts': {}}
    }

    # Categorize VMs into groups based on their 'group' attribute

    for vm_name, details in vm_dict.items():
        if 'docker-registry' in details['roles'].lower():
            registry_hostname_string = details['name']
            inventory['registry']['hosts'][details['name']] = {
                'ansible_host': details['IP'],
                'ansible_user': 'devops'
            }
        elif 'rke' not in details['group'].lower():
            inventory['docker']['hosts'][details['name']] = {
                'ansible_host': details['IP'],
                'ansible_user': 'devops'
            }
    domain_string = security.base_domain
    registry_dns_string = prefix + "registry" + "." + domain_string

    # print(registry_dns_string) 
    # print(inventory)

    vault_ip = get_vms_by_group("vault", Session)[0].ip

    # vault_token = get_vault_token(Session)
    # print(vault_token)
    # client = hvac.Client(url=f'https://{vault_ip}:8200', verify=False, token=vault_token) 

    # # Check if Vault is initialized and unsealed
    # if not client.is_authenticated():
    #     raise Exception("Vault authentication failed.")

    username = "devops"
    password = "devops"

    # try:
    #     secret_response = client.secrets.kv.v2.read_secret_version(
    #         mount_point='harmonisation',
    #         path='registry/credentials'
    #     )
    #     secret_data = secret_response['data']['data']
    #     username = secret_data.get('username')
    #     password = secret_data.get('password')

    #     print("registry Credentials:")
    #     print(f"Username: {username}")
    #     print(f"Password: {password}")

    # except hvac.exceptions.InvalidPath:
    #     print("Error: Secret path 'registry/credentials' does not exist in 'harmonisation'.")
        
    extra_vars = {
    "rv_dregistry_container_exec": "docker",
    "rv_dregistry_install_dir": "~/.dockerregistry",
    "rv_dregistry_user": username,"rv_dregistry_pass":password,
    "rv_dregistry_install_dir":"/data/registry","ansible_user":"devops",
    "docker_registry_url":registry_dns_string,
    "private_key":private_key,
    "certificate": certificate}



    return extra_vars, inventory

