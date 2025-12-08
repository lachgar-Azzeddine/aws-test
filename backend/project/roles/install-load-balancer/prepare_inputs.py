import tempfile
import re

from repository import (
    get_security,
    get_smtp_servers,
    get_vms_by_group,
    get_databases,
    get_ldaps,
    get_payment_providers,
    get_sms_providers,
    query_products,
    get_arcgis_servers,
    get_server,
)


def get_inputs(Session):
    security = get_security(Session)

    prefix = "" if security.env_prefix == "" else security.env_prefix + "-"

    RKE_APPS_VMS = get_vms_by_group("RKEAPPS", Session)

    RKE_DMZ_VMS = get_vms_by_group("RKEDMZ", Session)

    RKE_MIDDLEWAWRE_VMS = get_vms_by_group("RKEMIDDLEWARE", Session)
    smtp_server_host = ""
    smtp_server_port = ""
    sms_ip = ""
    sms_port = ""
    payment_ip = ""
    payment_port = ""
    sig_db_host = ""
    sig_db_port = ""
    postgresql_db_host = ""
    informix_db_host = ""
    postgresql_db_port = ""
    informix_db_port = ""
    gco_db_host = ""
    gco_db_port = ""
    gco_sig_host = ""
    gco_sig_port = ""
    websocketGCO_ip = ""
    websocketGCO_port = ""

    sms_provider = []
    payment_provider = []

    LB_LAN_vms = get_vms_by_group("LBLAN", Session)
    LB_LAN_vm = LB_LAN_vms[0]
    LB_LAN_ip = LB_LAN_vm.ip
    LB_DMZ_vms = get_vms_by_group("LBDMZ", Session)
    LB_DMZ_vm = LB_DMZ_vms[0]
    LB_DMZ_ip = LB_DMZ_vm.ip
    LB_INTEGRATION_vms = get_vms_by_group("LBINTEGRATION", Session)
    LB_INTEGRATION_vm = LB_INTEGRATION_vms[0]
    LB_INTEGRATION_ip = LB_INTEGRATION_vm.ip

    smtp_servers = []



    databases = get_databases(Session)

    websocketGCO_ip = ""
    websocketGCO_port = ""

    ldaps = get_ldaps(Session)

    internal_ldap_host = ""
    internal_ldap_port = ""
    exteranl_ldap_host = ""
    exteranl_ldap_port = ""
    gco_ldap_host = ""
    gco_ldap_port = ""


    if re.search(r"ldap://([\d\.]+)", internal_ldap_host):
        internal_ldap_host = re.search(r"ldap://([\d\.]+)", internal_ldap_host).group(1)
    if re.search(r"ldap://([\d\.]+)", exteranl_ldap_host):
        exteranl_ldap_host = re.search(r"ldap://([\d\.]+)", exteranl_ldap_host).group(1)
    if re.search(r"ldap://([\d\.]+)", gco_ldap_host):
        gco_ldap_host = re.search(r"ldap://([\d\.]+)", gco_ldap_host).group(1)
    # print(ldap_3388_host)
    # print(ldap_3389_host)

    vault_vms = get_vms_by_group("vault", Session)
    vault_vm = vault_vms[0]
    vault_ip = vault_vm.ip

    monitoring_vms = get_vms_by_group("monitoring", Session)
    monitoring_vm = monitoring_vms[0]
    monitoring_ip = monitoring_vm.ip

    gitops_vms = get_vms_by_group("gitops", Session)
    gitops_vm = gitops_vms[0]
    gitops_ip = gitops_vm.ip
    # tmp variable for hdfs host - client-specific IP removed
    hdfs_host = ""  # Set this to your HDFS host IP
    if security is None:
        print("Could not load the module spec for security")
        exit(1)
    # Define your SSH private key as a string
    ssh_key_string = security.ssh_pulic_key
    pem_key_string = security.pem_certificate
    # Write the SSH key to a temporary file
    with tempfile.NamedTemporaryFile(delete=False, mode="w") as key_file:
        key_file.write(ssh_key_string)
        key_file_path = key_file.name
    with tempfile.NamedTemporaryFile(delete=False, mode="w") as key_file:
        key_file.write(pem_key_string)
        pem_key_file = key_file.name
    print(pem_key_file)
    # Variables to pass to Jinja2 templates
    # extra_vars =  {
    #     "cluster_name":cluster_name,
    #     "rke2_config_dir": "/etc/rancher/rke2",
    #     "kubeconfig_file": "/root/.kube/config.yaml",
    #     "install_script": "/home/devops/rke2-artifacts/install.sh",
    #     "token": "RKE-token",
    #     "kubeconfig_mode": "0644"}
    rke_apps_vm_list = [{"name": vm.hostname, "IP": vm.ip} for vm in RKE_APPS_VMS]
    rke_middleware_vm_list = [
        {"name": vm.hostname, "IP": vm.ip} for vm in RKE_MIDDLEWAWRE_VMS
    ]
    rke_dmz_vm_list = [
        {"name": vm.hostname, "IP": vm.ip} for vm in RKE_DMZ_VMS
    ]

    registry_url = f"{prefix}registry.{security.base_domain}:8443"

    arcgis_host = ""
    arcgis_port = ""
    url_gmao = ""
    host_gmao = ""
    port_gmao = ""
    url_gcbo = ""
    host_gcbo = ""
    port_gcbo = ""
    url_alfresco = ""
    host_alfresco = ""
    port_alfresco = ""



    extra_vars = {
        "rke_apps": rke_apps_vm_list,
        "rke_middleware": rke_middleware_vm_list,
        "rke_dmz": rke_dmz_vm_list,
        "lb_lan_ip": LB_LAN_ip,
        "gitops_ip": gitops_ip,
        "vault_ip": vault_ip,
        "monitoring_ip": monitoring_ip,
        "pem_file": pem_key_file,
        "registry_url": registry_url,
        "smtp_server_host": smtp_server_host,
        "smtp_server_port": smtp_server_port,
        "sig_db_host": sig_db_host,
        "sig_db_port": sig_db_port,
        "Informix_db_host": informix_db_host,
        "Informix_db_port": informix_db_port,
        "postgres_db_host": postgresql_db_host,
        "postgres_db_port": postgresql_db_port,
        "internal_ldap_host": internal_ldap_host,
        "internal_ldap_port": internal_ldap_port,
        "external_ldap_host": exteranl_ldap_host,
        "external_ldap_port": exteranl_ldap_port,
        "hdfs_host": hdfs_host,
        "sms_host": sms_ip,
        "sms_port": sms_port,
        "payment_host": payment_ip,
        "payment_port": payment_port,
        "gco_db_host": gco_db_host,
        "gco_db_port": gco_db_port,
        "gco_sig_host": gco_sig_host,
        "gco_sig_port": gco_sig_port,
        "arcgis_host": arcgis_host,
        "arcgis_port": arcgis_port,
        "websocketGCO_ip": websocketGCO_ip,
        "websocketGCO_port": websocketGCO_port,
        "prefix": prefix,
        "host_gmao": host_gmao,
        "port_gmao": port_gmao,
        "host_gcbo": host_gcbo,
        "port_gcbo": port_gcbo,
        "host_alfresco": host_alfresco,
        "port_alfresco": port_alfresco,
    }

    inventory = {
        "all": {
            "hosts": {
                "localhost": {
                    "ansible_host": "127.0.0.1",
                    "ansible_connection": "local",
                },
                "LB_DMZ": {
                    "ansible_host": LB_DMZ_ip,
                    "ansible_user": "devops"
                },
                "LB_LAN": {"ansible_host": LB_LAN_ip, "ansible_user": "devops"},
                "LB_INTEGRATION": {
                    "ansible_host": LB_INTEGRATION_ip,
                    "ansible_user": "devops",
                },
            }
        }
    }
    print(extra_vars)
    print(inventory)
    return extra_vars, inventory
