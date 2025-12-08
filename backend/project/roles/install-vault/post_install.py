import tempfile
from repository import (
    get_security,
    get_vms_by_group,
    add_vault_keys,
    add_vault_token,
    get_vault_token,
    get_databases,
    get_ldaps,
    get_sms_providers,
    clear_vault_table,
)
import hvac
from hvac.exceptions import InvalidPath, VaultError
import requests
import json
import time
import re, base64


def post_install(Session):
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

    vault_vms = get_vms_by_group("vault", Session)
    vault_vm = vault_vms[0]
    vault_ip = vault_vm.ip

    databases = get_databases(Session)

    prod_login = ""
    prod_password = ""
    sig_login = ""
    sig_password = ""
    flowable_login = ""
    flowable_password = ""
    gco_db_login = ""
    gco_db_password = ""
    gco_sig_login = ""
    gco_sig_password = ""
    promoteur_pp_user = ""
    promoteur_pp_pass = ""
    promoteur_iu_user = ""
    promoteur_iu_pass = ""
    keycloak_db_login = ""
    keycloak_db_password= ""

    for db in databases:
        if db.alias == "db_metiers":
            prod_login = db.login
            prod_password = db.password



    ldaps = get_ldaps(Session)


    # Vault server address
    VAULT_ADDR = f"https://{vault_ip}:8200"

    time.sleep(5)  # Wait for Vault to start

    # Initialize Vault
    url = f"{VAULT_ADDR}/v1/sys/init"
    payload = {"secret_shares": 5, "secret_threshold": 3}
    response = requests.put(url, json=payload, verify=False)
    if response.status_code == 200:
        data = response.json()
        keys = data["keys"]
        root_token = data["root_token"]
        print("Vault initialized successfully.")
        print("Unseal Keys:", keys)
        print("Root Token:", root_token)

        clear_vault_table(Session)
        # Send keys and token to database
        add_vault_keys(keys, Session)
        add_vault_token(root_token, Session)

        # Unseal Vault
        for key in keys[:3]:
            url = f"{VAULT_ADDR}/v1/sys/unseal"
            payload = {"key": key}
            response = requests.put(url, json=payload, verify=False)
            if response.status_code == 200:
                print("Unsealed with one key.")
            else:
                print("Error unsealing Vault:", response.text)
    else:
        print("Error initializing Vault:", response.text)

    vault_token = get_vault_token(Session)

    client = hvac.Client(
        url=f"https://{vault_ip}:8200", token=vault_token, verify=False
    )

    # Check if Vault is initialized and unsealed
    if not client.is_authenticated():
        print("Vault authentication failed. Please check your Vault token.")
        exit(1)

    kv_path = "harmonisation"

    mount_path = kv_path

    try:
        mounts = client.sys.list_mounted_secrets_engines()
        if f"{mount_path}/" not in mounts:
            print(f"Enabling KV v2 secrets engine at mount point: {mount_path}")
            client.sys.enable_secrets_engine(
                backend_type="kv", path=mount_path, options={"version": "2"}
            )
            print("KV engine enabled.")
        else:
            print(f"KV engine already enabled at '{mount_path}/'.")
    except VaultError as e:
        print(f"Failed to check/enable KV engine: {str(e)}")
        raise

    print(f"KV secrets engine enabled at path: {kv_path}")
    gogs_username = "devops"
    gogs_password = "devops"
    secret_path = "gogs/credentials"

    # Store Gogs credentials in Vault
    client.secrets.kv.v2.create_or_update_secret(
        mount_point=mount_path,
        path=secret_path,
        secret={"username": gogs_username, "password": gogs_password},
    )
    print(f"Gogs credentials successfully stored in Vault at '{secret_path}'.")

    apim_username = "admin"
    apim_password = "admin"
    secret_path = "gravitee/credentials"

    # Store Gogs credentials in Vault
    client.secrets.kv.v2.create_or_update_secret(
        mount_point=mount_path,
        path=secret_path,
        secret={"username": apim_username, "password": apim_password},
    )
    print(f"Gravitee credentials successfully stored in Vault at '{secret_path}'.")

    flowable_admin_user = "admin1"
    flowable_admin_password = "admin1"
    secret_path = "flowable_admin/credentials"

    client.secrets.kv.v2.create_or_update_secret(
        mount_point=mount_path,
        path=secret_path,
        secret={"username": flowable_admin_user, "password": flowable_admin_password},
    )
    print(f"Flowable credentials successfully stored in Vault at '{secret_path}'.")

    gravitee_user = "admin"
    gravitee_password = "admin"
    secret_path = "gravitee_lan/credentials"

    client.secrets.kv.v2.create_or_update_secret(
        mount_point=mount_path,
        path=secret_path,
        secret={"username": gravitee_user, "password": gravitee_password},
    )
    print(f"Gravitee LAN credentials successfully stored in Vault at '{secret_path}'.")

    secret_path = "gravitee_dmz/credentials"

    client.secrets.kv.v2.create_or_update_secret(
        mount_point=mount_path,
        path=secret_path,
        secret={"username": gravitee_user, "password": gravitee_password},
    )
    print(f"Gravitee DMZ credentials successfully stored in Vault at '{secret_path}'.")

    registry_user = "devops"
    registry_password = "devops"
    secret_path = "registry/credentials"

    client.secrets.kv.v2.create_or_update_secret(
        mount_point=mount_path,
        path=secret_path,
        secret={"username": registry_user, "password": registry_password},
    )
    print(f"Registry credentials successfully stored in Vault at '{secret_path}'.")

    rancher_user = "devops"
    rancher_password = "devops"
    secret_path = "rancher/credentials"

    client.secrets.kv.v2.create_or_update_secret(
        mount_point=mount_path,
        path=secret_path,
        secret={"username": rancher_user, "password": rancher_password},
    )
    print(f"Rancher credentials successfully stored in Vault at '{secret_path}'.")

    coroot_user = "admin"
    coroot_password = ""
    secret_path = "coroot/credentials"

    client.secrets.kv.v2.create_or_update_secret(
        mount_point=mount_path, path=secret_path, secret={"username": coroot_user}
    )
    print(f"Coroot credentials successfully stored in Vault at '{secret_path}'.")

    neuvector_user = "admin"
    neuvector_password = "admin"
    secret_path = "neuvector/credentials"

    client.secrets.kv.v2.create_or_update_secret(
        mount_point=mount_path,
        path=secret_path,
        secret={"username": neuvector_user, "password": neuvector_password},
    )
    print(f"Neuvector credentials successfully stored in Vault at '{secret_path}'.")

    minio_user = "devops"
    minio_password = "aq9rj9R1"
    secret_path = "minio/credentials"

    client.secrets.kv.v2.create_or_update_secret(
        mount_point=mount_path,
        path=secret_path,
        secret={"username": minio_user, "password": minio_password},
    )
    print(f"Minio credentials successfully stored in Vault at '{secret_path}'.")


    keycloak_user = "admin_user"
    keycloak_password = "Admin_Password"
    secret_path = "keycloak/credentials"

    client.secrets.kv.v2.create_or_update_secret(
        mount_point=mount_path,
        path=secret_path,
        secret={"username": keycloak_user, "password": keycloak_password},
    )
    print(f"Keycloak credentials successfully stored in Vault at '{secret_path}'.")

    secret_path = "prod/credentials"
    client.secrets.kv.v2.create_or_update_secret(
        mount_point=mount_path,
        path=secret_path,
        secret={
            "username": base64.b64decode(prod_login).decode("utf-8"),
            "password": base64.b64decode(prod_password).decode("utf-8"),
        },
    )
    print(
        f"Métiers database credentials successfully stored in Vault at '{secret_path}'."
    )
