import tempfile, hvac, base64
from urllib.parse import quote_plus
from repository import (
    get_security,
    get_vms_by_group,
    get_databases,
    get_vault_token,
    get_ldaps,
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

    pem_content = security.pem_certificate
    prefix = "" if security.env_prefix == "" else security.env_prefix + "-"

    private_key_start = "-----BEGIN PRIVATE KEY-----"
    private_key_end = "-----END PRIVATE KEY-----"
    certificate_start = "-----BEGIN CERTIFICATE-----"
    certificate_end = "-----END CERTIFICATE-----"
    key_file = "/tmp/minio-crts/domain.key"
    cert_file = "/tmp/minio-certs/domain.crt"
    # Extract the private key
    private_key = pem_content[
        pem_content.find(private_key_start) : pem_content.find(private_key_end)
        + len(private_key_end)
    ]
    print("private key:\n" + private_key)
    # Extract the certificate
    certificate = pem_content[
        pem_content.find(certificate_start) : pem_content.find(certificate_end)
        + len(certificate_end)
    ]
    encoded_cert = base64.b64encode(certificate.encode("utf-8")).decode("utf-8")
    encoded_key = base64.b64encode(private_key.encode("utf-8")).decode("utf-8")

    base_domain = security.base_domain

    prefix = "" if security.env_prefix == "" else security.env_prefix + "-"

    registry_url = f"{prefix}registry.{base_domain}:8443"

    gogs_ip = get_vms_by_group("gitops", Session)[0].ip

    gogs_url = f"{prefix}gogs.{base_domain}"

    LB_LAN_vms = get_vms_by_group("LBLAN", Session)
    LB_LAN_vm = LB_LAN_vms[0]
    LB_LAN_ip = LB_LAN_vm.ip

    LB_INT_vms = get_vms_by_group("LBINTEGRATION", Session)
    LB_INT_vm = LB_INT_vms[0]
    LB_INT_ip = LB_INT_vm.ip

    ldaps = get_ldaps(Session)

    external_ldap = next(ldap for ldap in ldaps if ldap.ldap_type == "external_users")

    internal_ldap = next(ldap for ldap in ldaps if ldap.ldap_type == "internal_users")

    ext_ldap_url = f"ldap://{LB_INT_ip}:{external_ldap.ldap_port}"

    int_ldap_url = f"ldap://{LB_INT_ip}:{internal_ldap.ldap_port}"

    ext_ldap_user = external_ldap.bind_dn

    ext_ldap_password = external_ldap.bind_credentials

    ext_ldap_user_dn = external_ldap.user_dn

    ext_ldap_user_attribute = external_ldap.user_ldap_attributes

    ext_ldap_search_scope = external_ldap.search_scope

    int_ldap_user_dn = internal_ldap.user_dn

    int_ldap_user_attribute = internal_ldap.user_ldap_attributes

    int_ldap_search_scope = internal_ldap.search_scope

    int_ldap_user = internal_ldap.bind_dn

    int_ldap_password = internal_ldap.bind_credentials

    databases = get_databases(Session)

    for db in databases:
        if db.type == "Postgresql":
            if db.alias == "db_keycloak":
                keycloak_db = db

    plain_user = base64.b64decode(keycloak_db.login.encode("utf-8")).decode("utf-8")
    plain_password = base64.b64decode(keycloak_db.password.encode("utf-8")).decode(
        "utf-8"
    )
    safe_user = quote_plus(plain_user)
    safe_password = quote_plus(plain_password)

    full_db_url = (
        f"jdbc:postgresql://{keycloak_db.host}:{keycloak_db.port}/{keycloak_db.name}"
        f"?sslmode=disable&connectTimeout=30&password={safe_password}"
    )

    # db_url = f"jdbc:postgresql://{keycloak_db.host}:{keycloak_db.port}/{keycloak_db.name}?sslmode=disable&connectTimeout=30"

    vault_ip = get_vms_by_group("vault", Session)[0].ip

    vault_token = get_vault_token(Session)
    print(vault_token)
    client = hvac.Client(
        url=f"https://{vault_ip}:8200", verify=False, token=vault_token
    )

    # Check if Vault is initialized and unsealed
    if not client.is_authenticated():
        raise Exception("Vault authentication failed.")

    username = None
    password = None

    try:
        secret_response = client.secrets.kv.v2.read_secret_version(
            mount_point="harmonisation", path="keycloak/credentials"
        )
        secret_data = secret_response["data"]["data"]
        username = secret_data.get("username")
        password = secret_data.get("password")

        print("keycloak Credentials:")
        print(f"Username: {username}")
        print(f"Password: {password}")

    except hvac.exceptions.InvalidPath:
        print(
            "Error: Secret path 'keycloak/credentials' does not exist in 'harmonisation'."
        )

    # Variables to pass to Jinja2 templates
    extra_vars = {
        "base_domain": base_domain,
        "registry_url": registry_url,
        "gogs_ip": gogs_ip,
        "gogs_url": gogs_url,
        "kc_user": base64.b64encode(username.encode("utf-8")).decode("utf-8"),
        "kc_pw": base64.b64encode(password.encode("utf-8")).decode("utf-8"),
        "db_url": base64.b64encode(full_db_url.encode("utf-8")).decode("utf-8"),
        "db_username": keycloak_db.login,
        "lblan_ip": LB_LAN_ip,
        "lbint_ip": LB_INT_ip,
        "ext_ldap_url": ext_ldap_url,
        "int_ldap_url": int_ldap_url,
        "ext_ldap_user": ext_ldap_user,
        "ext_ldap_password": base64.b64decode(ext_ldap_password.encode("utf-8")).decode(
            "utf-8"
        ),
        "int_ldap_user": int_ldap_user,
        "int_ldap_password": base64.b64decode(int_ldap_password.encode("utf-8")).decode(
            "utf-8"
        ),
        "ext_ldap_user_dn": ext_ldap_user_dn,
        "ext_ldap_user_attribute": ext_ldap_user_attribute,
        "ext_ldap_search_scope": ext_ldap_search_scope,
        "int_ldap_user_dn": int_ldap_user_dn,
        "int_ldap_user_attribute": int_ldap_user_attribute,
        "int_ldap_search_scope": int_ldap_search_scope,
        "prefix": prefix,
        "encoded_cert": encoded_cert,
        "encoded_key": encoded_key,
    }

    # Dynamic inventory setup
    inventory = {
        "all": {
            "hosts": {
                "localhost": {
                    "ansible_host": "127.0.0.1",
                    "ansible_connection": "local",
                }
            }
        }
    }

    return extra_vars, inventory
