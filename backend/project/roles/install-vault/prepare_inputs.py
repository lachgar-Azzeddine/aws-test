import tempfile

from repository import (
    get_security,
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

    pem_content= security.pem_certificate
    prefix = "" if security.env_prefix == "" else security.env_prefix + "-"

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
    print("private key:\n"+private_key)
    # Extract the certificate
    certificate = pem_content[
        pem_content.find(certificate_start) : pem_content.find(certificate_end) + len(certificate_end)
    ]

    vault_vms = get_vms_by_group("vault",Session)
    vault_vm = vault_vms[0]
    vault_ip = vault_vm.ip

    gogs_ip = get_vms_by_group("gitops",Session)[0].ip

    prefix = "" if security.env_prefix == "" else security.env_prefix + "-"
    gogs_url = f"{prefix}gogs.{security.base_domain}"


    registry_url = f"{prefix}registry.{security.base_domain}:8443"

    extra_vars = {
        "gogs_url": gogs_url, 
        "gogs_ip": gogs_ip,
        "vault_ip": vault_ip,
        "registry_url": registry_url,
        "certificate": certificate,
        "private_key": private_key
    }

    inventory = {
        "all": {
            "hosts": {
                "localhost": {
                    "ansible_host": "127.0.0.1",
                    "ansible_connection": "local"
                },
                "vault_vm": {
                    "ansible_host": vault_ip,
                    "ansible_user": "devops"
                }
            }
        }
    }
    
    print(extra_vars)
    print(inventory)
    return extra_vars, inventory
