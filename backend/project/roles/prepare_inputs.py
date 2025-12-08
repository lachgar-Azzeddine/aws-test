import tempfile
from repository import get_vault_token, get_security, get_vms_by_group, get_databases, get_sms_providers, get_payment_providers, get_ldaps, get_smtp_servers
import re,hvac

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

    databases = get_databases(Session)
    
    proxy_url = f"{security.porxy_host}:{security.proxy_port}"

    load_balancer_ip_int = get_vms_by_group("LBINTEGRATION", Session)[0].ip

    load_balancer_ip_lan = get_vms_by_group("LBLAN", Session)[0].ip

    rke_mw_vm_ip = get_vms_by_group("RKEMIDDLEWARE", Session)[0].ip

    rke_apps_vm_ip = get_vms_by_group("RKEAPPS", Session)[0].ip

    admin_vm_ip = get_vms_by_group("monitoring", Session)[0].ip
    
    prod_name = ""
    prod_server = ""
    prod_host = ""
    prod_port = ""
    prod_login = ""
    prod_password = ""
    sig_name = ""
    sig_server = ""
    sig_host = ""
    sig_port = ""
    sig_login = ""
    sig_password = ""
    flowable_name = ""
    flowable_host = ""
    flowable_port = ""
    flowable_login = ""
    flowable_password = ""

    for db in databases:

        if db.type == "Postgresql":
            if db.alias == "db_workflow":
                flowable_name = db.name
                flowable_host = db.host
                flowable_port = db.port
                flowable_login = db.login
                flowable_password = db.password
        
        elif db.type == "Informix":

            if db.alias == "db_metiers":
                prod_name = db.name
                prod_server = db.servername
                prod_host = db.host
                prod_port = db.port
                prod_login = db.login
                prod_password = db.password

            elif db.alias == "db_sig":
                sig_name = db.name
                sig_server = db.servername
                sig_host = db.host
                sig_port = db.port
                sig_login = db.login
                sig_password = db.password

    sms_provider = get_sms_providers(Session)

    smtp_provider = get_smtp_servers(Session)[0]

    smtp_url = smtp_provider.host

    smtp_port = smtp_provider.port

    sms_url = sms_provider[0].url
    # Replace SMS IP with integration loadbalancer IP
    sms_url = re.sub(r'http://([\d\.]+):', f'http://{load_balancer_ip_int}:', sms_url)
    sms_login = sms_provider[0].login
    sms_password = sms_provider[0].password

    payment_provider = get_payment_providers(Session)

    payment_url = payment_provider[0].url

    # Replace Payment IP with integration loadbalancer IP
    payment_url = re.sub(r'http://([\d\.]+):', f'http://{load_balancer_ip_int}:', payment_url)

    ldaps = get_ldaps(Session)

    external_ldap = next(ldap for ldap in ldaps if ldap.ldap_type == "external_users")

    ldap_url = f"ldap://{load_balancer_ip_int}:{external_ldap.ldap_port}"

    ldap_user = external_ldap.bind_dn

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
            path='minio/credentials'
        )
        secret_data = secret_response['data']['data']
        username = secret_data.get('username')
        password = secret_data.get('password')

        print("minio Credentials:")
        print(f"Username: {username}")
        print(f"Password: {password}")

    except hvac.exceptions.InvalidPath:
        print("Error: Secret path 'minio/credentials' does not exist in 'harmonisation'.")


    ldap_password = external_ldap.bind_credentials

    # Variables to pass to Jinja2 templates
    extra_vars = {
        "gogs_url": gogs_url,
        "gogs_ip": gogs_ip, 
        "prod_name": prod_name,
        "prod_server": prod_server,
        "prod_host": prod_host,
        "prod_port": prod_port,
        "prod_login": prod_login,
        "prod_password": prod_password,
        "sig_name": sig_name,
        "sig_server": sig_server,
        "sig_host": sig_host,
        "sig_port": sig_port,
        "sig_login": sig_login,
        "sig_password": sig_password,
        "flowable_name": flowable_name,
        "flowable_host": flowable_host,
        "flowable_port": flowable_port,
        "flowable_login": flowable_login,
        "flowable_password": flowable_password,
        "proxy_url": proxy_url,
        "sms_url": sms_url,
        "sms_user": sms_login,
        "sms_password": sms_password,
        "base_domain": security.base_domain,
        "payment_api_url": payment_url,
        "ldap_url": ldap_url,
        "ldap_user": ldap_user,
        "ldap_password": ldap_password,
        "load_balancer_ip": load_balancer_ip_int,
        "lblan_ip": load_balancer_ip_lan,
        "smtp_host": smtp_url,
        "smtp_port": smtp_port,
        "rke_mw_vm_ip": rke_mw_vm_ip,
        "rke_apps_vm_ip": rke_apps_vm_ip,
        "admin_vm_ip": admin_vm_ip,
        "minio_access_key": username,
        "minio_secret_key": password,
        "prefix": prefix
    }

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
