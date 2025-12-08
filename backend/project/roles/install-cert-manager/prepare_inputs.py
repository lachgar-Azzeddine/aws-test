import tempfile
import base64
from repository import get_security, get_vms_by_group



def get_inputs(Session):
    security = get_security(Session)
    if security is None:
        print("Could not load the module spec for security")
        exit(1)

    prefix = "" if security.env_prefix == "" else security.env_prefix + "-"
    gogs_ip = get_vms_by_group("gitops",Session)[0].ip
    gogs_url = f"{prefix}gogs.{security.base_domain}"
    gogs_url_ip = "https://"+gogs_ip+"/devops/harmonisation.git"
    
    registry_url = f"{prefix}registry.{security.base_domain}:8443"
    extra_vars = {
        "gogs_url": gogs_url, 
        "gogs_ip": gogs_ip,
        "registry_url": registry_url,
        "gogs_url_ip": gogs_url_ip,
        "base_domain": security.base_domain,
        "prefix": prefix
        }


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
