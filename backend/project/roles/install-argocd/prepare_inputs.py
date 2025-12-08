import os
from repository import get_security, get_vms_by_group, get_vault_token


def get_gogs_ip(Session):
    """Get Gogs IP address based on environment.

    In test environment (Docker Compose + k3d), returns the Docker network gateway IP
    to ensure k3d clusters can reach Gogs.
    In production, returns the VM IP from database.
    """
    # Check if we're in test environment
    if os.environ.get('TEST_ENVIRONMENT') == 'true':
        try:
            import docker
            client = docker.from_env()
            network = client.networks.get('tests_default')
            gateway_ip = network.attrs['IPAM']['Config'][0]['Gateway']
            print(f"Using Docker gateway IP for Gogs: {gateway_ip}")
            return gateway_ip
        except Exception as e:
            print(f"Warning: Could not get Docker gateway IP: {e}")
            print("Falling back to database VM IP")
            # Fall through to database query
    # Production or fallback: get VM IP from database
    return get_vms_by_group("gitops", Session)[0].ip


def get_inputs(Session):
    security = get_security(Session)
    if security is None:
        print("Could not load the module spec for security")
        exit(1)

    prefix = "" if security.env_prefix == "" else security.env_prefix + "-"

    gogs_domain_name = f"{prefix}gogs.{security.base_domain}"
    registry_domain_name = f"{prefix}registry.{security.base_domain}:8443"
    argocd_domain_apps = f"{prefix}argocd-apps.{security.base_domain}"
    argocd_domain_mw = f"{prefix}argocd-mw.{security.base_domain}"
    argocd_domain_dmz = f"{prefix}argocd-dmz.{security.base_domain}"

    vault_vms = get_vms_by_group("vault",Session)
    vault_vm = vault_vms[0]
    vault_ip = vault_vm.ip

    gogs_ip = get_gogs_ip(Session)

    vault_token = get_vault_token(Session)


    kubeconfig_path = os.getenv("KUBECONFIG", "/home/devops/.kube/config")
    # Variables to pass to Jinja2 templates
    extra_vars = {"vault_ip":vault_ip, "vault_token": vault_token, "prefix": prefix , "argocd_domain_apps": argocd_domain_apps, "argocd_domain_mw": argocd_domain_mw, "argocd_domain_dmz": argocd_domain_dmz, "gogs_domain_name": gogs_domain_name, "registry": registry_domain_name, "gogs_ip": gogs_ip, "kubeconfig_path": kubeconfig_path}

    # Dynamic inventory setup
    inventory = {
        "all": {
            "hosts": {
                "localhost": {
                    "ansible_host": "127.0.0.1",
                    "ansible_connection": "local",
                },
                "vault_vm": {
                    "ansible_host": vault_ip,
                    "ansible_user": "devops"
                }
            }
        }
    }

    return extra_vars, inventory
