import base64
import os
import socket
import subprocess
import datetime
import re
from sqlalchemy import (
    create_engine,
)
from sqlalchemy.orm import sessionmaker, joinedload
import requests
from paramiko import RSAKey, ssh_exception, client, AutoAddPolicy
from io import StringIO


import psycopg2
from cryptography import x509
from cryptography.hazmat.backends import default_backend
from cryptography.fernet import Fernet
from ldap3 import Server, Connection
from models import (
    # Client-specific service models removed:
    # SignatureService, Facebook, Google, Fcm, FirebaseDb,
    # AlfrescoServer, ArcgisServer, AuthServer, GCBOServer, GMAOServer,
    # PaymentProvider, PublishingProvider
    AnsibleRole,
    Application,
    Configuration,
    Database,
    Dns,
    FlowMatrix,
    Ldap,
    Monitoring,
    NutanixAHV,
    # Product removed - no longer using product-based system
    Security,
    SMSProvider,
    SMTPServer,
    TaskLog,
    VirtualMachine,
    VMwareEsxi,
    Zone,
    VaultCredentials,
    VMConfiguration,
)
import logging

# TODO to be placed somewhere safer (ex: env variable)
ENCRYPTION_KEY = "uOdT_oGBMvG8N7_rpBg1UVlwVK7BD6igm0l4IqJD8cA="
fernet = Fernet(ENCRYPTION_KEY)

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


# function that check if the database file exists
def database_exists(db_path):
    return os.path.exists(db_path)


def get_session():
    """
    Get database session. Calls initialize_database() to ensure tables and VMs exist.
    """
    from initial_db import initialize_database
    return initialize_database()


def encrypt_password(plain_password: str):
    encoded_pwd = plain_password.encode()
    encrypted_pwd_bytes = fernet.encrypt(encoded_pwd)
    return encrypted_pwd_bytes.decode()


def decrypt_password(encrypted_password: str):
    encrypted_pwd_bytes = encrypted_password.encode()
    decrypted_pwd_bytes = fernet.decrypt(encrypted_pwd_bytes)
    return decrypted_pwd_bytes.decode()


# Product-related functions removed - no longer using product-based system
# query_products, get_products_to_install, prepare_install_products, set_installed_products deleted


# Application CRUD functions
def add_application(url, category, name, configuration_id, Session):
    """Add a new application"""
    if Session is None:
        print("Session is not initialized")
        return
    session = Session()
    configuration = session.query(Configuration).get(configuration_id)
    if configuration is None:
        print("Configuration not found")
        session.close()
        return

    # product_id parameter removed - no longer using product-based system
    application = Application(
        url=url,
        category=category,
        name=name,
        configuration=configuration,
    )
    configuration.applications.append(application)
    session.commit()
    session.refresh(application)
    session.close()
    return application


def get_applications(Session):
    """Get all applications"""
    if Session is None:
        print("Session is not initialized")
        return []
    session = Session()
    applications = session.query(Application).all()
    session.close()
    return applications


def get_application_by_id(id, Session):
    """Get application by ID"""
    if Session is None:
        print("Session is not initialized")
        return None
    session = Session()
    application = session.query(Application).get(id)
    session.close()
    return application


def get_applications_by_category(category, Session):
    """Get applications by category"""
    if Session is None:
        print("Session is not initialized")
        return []
    session = Session()
    applications = (
        session.query(Application).filter(Application.category == category).all()
    )
    session.close()
    return applications


# get_applications_by_product removed - no longer using product-based system

def update_application(id, url, category, name, Session):
    """Update an existing application"""
    if Session is None:
        print("Session is not initialized")
        return
    session = Session()
    application = session.query(Application).get(id)
    if application is None:
        print("Application not found")
        session.close()
        return

    application.url = url
    application.category = category
    application.name = name

    # product_id parameter removed - no longer using product-based system
    session.commit()
    session.refresh(application)
    session.close()
    return application


def delete_application(id, Session):
    """Delete an application"""
    if Session is None:
        print("Session is not initialized")
        return
    session = Session()
    application = session.query(Application).get(id)
    if application is None:
        print("Application not found")
        session.close()
        return
    session.delete(application)
    session.commit()
    session.close()


def delete_applications_by_configuration(configuration_id, Session):
    """Delete all applications for a configuration"""
    if Session is None:
        print("Session is not initialized")
        return
    session = Session()
    session.query(Application).filter(
        Application.configuration_id == configuration_id
    ).delete()
    session.commit()
    session.close()


def getConfiguration(Session):
    if Session is None:
        print("Session is not initialized")
        return None
    session = Session()
    # Get configuration with id 1
    configuration = session.query(Configuration).get(1)
    return configuration


def getAllConfiguration(Session):
    if Session is None:
        print("Session is not initialized")
        return None
    session = Session()
    # Get configuration with id 1
    configuration = session.query(Configuration).all()
    return configuration


def update_number_concurent_users(number, Session):
    if Session is None:
        print("Session is not initialized")
        return
    session = Session()
    configuration = session.query(Configuration).get(1)
    if configuration is None:
        print("Configuration not found")
        session.close()
        return
    configuration.number_concurrent_users = number
    session.commit()
    session.close()
    return configuration


def update_current_step(number, Session):
    if Session is None:
        print("Session is not initialized")
        return
    session = Session()
    configuration = session.query(Configuration).get(1)
    if configuration is None:
        print("Configuration not found")
        session.close()
        return
    configuration.current_step = number
    session.commit()
    session.close()
    return configuration


# function that add a new VMware Esxi configuration
def add_vmware_esxi_configuration(
    alias,
    login,
    password,
    api_url,
    api_timeout,
    allow_unverified_ssl,
    datacenter_name,
    datacenter_id,
    target_name,
    target_id,
    target_type,
    datastore_name,
    datastore_id,
    pool_ressource_name,
    pool_ressource_id,
    is_connected,
    Session,
):
    session = Session()
    configuration = session.query(Configuration).get(1)
    if configuration is None:
        print("Configuration not found")
        session.close()
        return
    vmware = VMwareEsxi(
        alias=alias,
        login=login,
        password=encrypt_password(password),
        api_url=api_url,
        api_timeout=api_timeout,
        allow_unverified_ssl=allow_unverified_ssl,
        datacenter_name=datacenter_name,
        datacenter_id=datacenter_id,
        target_name=target_name,
        target_id=target_id,
        target_type=target_type,
        datastore_name=datastore_name,
        datastore_id=datastore_id,
        pool_ressource_name=pool_ressource_name,
        pool_ressource_id=pool_ressource_id,
        is_connected=is_connected,
        configuration=configuration,
    )
    configuration.vmwares.append(vmware)
    session.commit()
    session.refresh(vmware)
    session.close()
    return vmware


def test_ldap(ldap_url, ldap_port, bind_dn, bind_credentials):
    def decode(str):
        return base64.b64decode(str).decode("utf-8")

    AD_SERVER = f"{ldap_url}:{ldap_port}"
    server = Server(AD_SERVER, connect_timeout=10)
    logger.info(f"Initializing LDAP connection for  {bind_dn}")
    try:
        conn = Connection(
            server,
            user=bind_dn,
            password=decode(bind_credentials),
            authentication="SIMPLE",
            auto_bind=True,
        )

        if conn.bound:
            logger.info(f"Authentication successful for user: {bind_dn}")
            conn.unbind()
            return {"is_valid": True}
        else:
            logger.warning(f"Authentication FAILED for user: {bind_dn}")
            print(f"Error: {conn.result}")
            error = {"is_valid": False, "error": conn.result}
            return error
    except Exception as e:
        logger.debug(f"Error: {e}")
        error = {"is_valid": False, "error": str(e)}
        return error


def test_vmware_esxi_configuration(
    login,
    password,
    api_url,
    target_name,
    target_type,
    datacenter_name,
    datastore_name,
    pool_ressource_name,
):
    errors = []

    try:
        print("Authenticating to vCenter, user: {}".format(login))
        try:
            ip = socket.gethostbyname(api_url)

        except socket.gaierror:
            print("The server is unreachable.")
            error = f"Échec de résolution de l’adresse du serveur: {api_url}"
            errors.append(error)
            return errors

        sessionRequest = requests.post(
            f"https://{api_url}/rest/com/vmware/cis/session",
            auth=(login, password),
            verify=False,
        )
        if sessionRequest.status_code != 200:
            if sessionRequest.status_code == 401:
                error = "Informations d’identification non valides"
                errors.append(error)
            else:
                error = "Service indisponible"
                errors.append(error)

        elif sessionRequest.status_code == 200:
            session_id = sessionRequest.json()["value"]
            headers = {"vmware-api-session-id": session_id}
            if target_type == "host":
                hostsRequest = requests.get(
                    f"https://{api_url}/rest/vcenter/host",
                    headers=headers,
                    verify=False,
                )

                if hostsRequest.status_code == 200:
                    hostsList = hostsRequest.json()["value"]
                    hosts = list(
                        filter(
                            lambda x: x["name"] == target_name.split("/")[1], hostsList
                        )
                    )

                    if len(hosts) == 0:
                        error = "Host introuvable"
                        errors.append(error)
                else:
                    error = "Host Service indisponible"
                    errors.append(error)

            elif target_type == "cluster":
                clustersRequest = requests.get(
                    f"https://{api_url}/rest/vcenter/cluster",
                    headers=headers,
                    verify=False,
                )

                if clustersRequest.status_code == 200:
                    clustersList = clustersRequest.json()["value"]
                    clusters = list(
                        filter(lambda x: x["name"] == target_name, clustersList)
                    )
                    if len(clusters) == 0:
                        error = "Cluster introuvable"
                        errors.append(error)
                else:
                    error = "Cluster Service indisponible"
                    errors.append(error)

            datastoresRequest = requests.get(
                f"https://{api_url}/rest/vcenter/datastore",
                headers=headers,
                verify=False,
            )

            if datastoresRequest.status_code == 200:
                datastoresList = datastoresRequest.json()["value"]
                datastores = list(
                    filter(lambda x: x["name"] == datastore_name, datastoresList)
                )
                if len(datastores) == 0:
                    error = "Datastore introuvable"
                    errors.append(error)
            else:
                error = "Datastore Service indisponible"
                errors.append(error)

            datacentersRequest = requests.get(
                f"https://{api_url}/rest/vcenter/datacenter",
                headers=headers,
                verify=False,
            )

            if datacentersRequest.status_code == 200:
                datacentersList = datacentersRequest.json()["value"]
                datacenters = list(
                    filter(lambda x: x["name"] == datacenter_name, datacentersList)
                )

                if len(datacenters) == 0:
                    error = "Datacenter introuvable"
                    errors.append(error)
            else:
                error = "Datacenter Service indisponible"
                errors.append(error)

            poolsRequest = requests.get(
                f"https://{api_url}/rest/vcenter/resource-pool",
                headers=headers,
                verify=False,
            )
            print("testing pool")

            if poolsRequest.status_code == 200:
                poolsList = poolsRequest.json()["value"]
                pools = list(
                    filter(lambda x: x["name"] == pool_ressource_name, poolsList)
                )

                if len(pools) == 0:
                    error = "Resource pool introuvable"
                    errors.append(error)
            else:
                error = "Resource pool Service indisponible"
                errors.append(error)

        return errors
    except Exception as e:
        error = f"Service indisponible : {e}"
        errors.append(error)
        return errors


def test_key_pair_match(private_key_str, public_key_str, private_key_pwd):
    try:
        private_key = RSAKey.from_private_key(
            StringIO(private_key_str), private_key_pwd
        )

        extracted_public_key = private_key.get_base64()

        extracted_key_full = f"ssh-rsa {extracted_public_key}"
        public_key_str = " ".join(public_key_str.split()[:2])

        is_valid = extracted_key_full.strip() == public_key_str.strip()
        return {"is_valid": is_valid}

    except ssh_exception.PasswordRequiredException as e:
        print(f"Error: {e}")
        return {"has_password": True}

    except Exception as error:
        print(f"Error: {error}")
        return {"error": str(error)}


def test_ssl_with_domain(domain, certificate):
    try:
        # check if the provided certificate string is valid
        try:
            cert = x509.load_pem_x509_certificate(
                certificate.encode(), default_backend()
            )

        except:
            return False

        cn = None
        for item in cert.subject:
            if item.oid == x509.NameOID.COMMON_NAME:
                cn = item.value

        san_domains = []
        try:
            san_ext = cert.extensions.get_extension_for_oid(
                x509.OID_SUBJECT_ALTERNATIVE_NAME
            )
            san_domains = [entry.value for entry in san_ext.value]
        except x509.ExtensionNotFound:
            san_domains = []

        if domain in san_domains or domain == cn:
            return True
        else:
            return False

    except Exception as e:
        print(e)
        return False


def update_vmware_esxi_configuration(
    id: int,
    alias: str,
    login: str,
    password: str,
    api_url: str,
    api_timeout: int,
    allow_unverified_ssl: bool,
    datacenter_name: str,
    datacenter_id: str,
    target_name: str,
    target_id: str,
    target_type: str,
    datastore_name: str,
    datastore_id: str,
    pool_ressource_name: str,
    pool_ressource_id: str,
    Session,
):
    print("alias", alias)
    session = Session()
    vmware = session.query(VMwareEsxi).get(id)
    if vmware is None:
        raise ValueError(f"VMware configuration with ID {id} not found")

    vmware.alias = alias
    vmware.login = login
    vmware.password = encrypt_password(password)
    vmware.api_url = api_url
    vmware.api_timeout = api_timeout
    vmware.allow_unverified_ssl = allow_unverified_ssl
    vmware.datacenter_name = datacenter_name
    vmware.datacenter_id = datacenter_id
    vmware.target_name = target_name
    vmware.target_id = target_id
    vmware.target_type = target_type
    vmware.datastore_name = datastore_name
    vmware.datastore_id = datastore_id
    vmware.pool_ressource_name = pool_ressource_name
    vmware.pool_ressource_id = pool_ressource_id
    session.commit()
    session.refresh(vmware)
    session.close()
    return vmware


def delete_vmware_esxi_configuration(id, Session):
    if Session is None:
        print("Session is not initialized")
        return
    session = Session()
    vmware = session.query(VMwareEsxi).get(id)
    if vmware is None:
        print("VMware Esxi configuration not found")
        session.close()
        return
    session.delete(vmware)
    session.commit()
    session.close()


def add_nutanix_ahv_configuration(
    alias, login, password, host, port, allow_unverified_ssl, is_connected, Session
):
    if Session is None:
        print("Session is not initialized")
        return
    session = Session()

    # Fetch the configuration
    configuration = session.query(Configuration).get(1)
    if configuration is None:
        print("Configuration not found")
        session.close()
        return

    # Create NutanixAHV instance
    nutanix = NutanixAHV(
        alias=alias,
        login=login,
        password=encrypt_password(password),
        host=host,
        port=port,
        allow_unverified_ssl=allow_unverified_ssl,
        is_connected=is_connected,
        configuration=configuration,
    )

    # Add to the configuration's list of nutanix instances
    configuration.nutanixs.append(nutanix)

    # Commit the transaction to persist the object
    session.commit()

    # Explicitly flush the object and refresh it from the session
    session.flush()  # Ensure it's fully persisted
    session.refresh(nutanix)  # Make sure we can access all its attributes

    # Close the session
    session.close()

    return nutanix


def update_nutanix_ahv_configuration(
    id, alias, login, password, host, port, allow_unverified_ssl, Session
):
    if Session is None:
        print("Session is not initialized")
        return
    session = Session()
    nutanix = session.query(NutanixAHV).get(id)
    if nutanix is None:
        print("Nutanix AHV configuration not found")
        session.close()
        return
    nutanix.alias = alias
    nutanix.login = login
    nutanix.password = password
    nutanix.host = host
    nutanix.port = port
    nutanix.allow_unverified_ssl = allow_unverified_ssl
    session.commit()
    session.refresh(nutanix)
    session.close()
    return nutanix


def delete_nutanix_ahv_configuration(id, Session):
    if Session is None:
        print("Session is not initialized")
        return
    session = Session()
    nutanix = session.query(NutanixAHV).get(id)
    if nutanix is None:
        print("Nutanix AHV configuration not found")
        session.close()
        return
    session.delete(nutanix)
    session.commit()
    session.close()


def get_hypervisor_list(Session):
    if Session is None:
        print("Session is not initialized")
        return []
    session = Session()
    result = []
    vmwares = session.query(VMwareEsxi).all()
    for vmware in vmwares:
        result.append(
            {
                "id": vmware.id,
                "alias": vmware.alias,
                "type": "vmware",
                "is_connected": vmware.is_connected,
            }
        )
    nutanixs = session.query(NutanixAHV).all()
    for nutanix in nutanixs:
        result.append(
            {
                "id": nutanix.id,
                "alias": nutanix.alias,
                "type": "nutanix",
                "is_connected": nutanix.is_connected,
            }
        )
    session.close()
    return result


def get_hypervisor(id, type, Session):
    if Session is None:
        print("Session is not initialized")
        return None
    session = Session()
    hypervisor = None
    if type == "vmware":
        hypervisor = session.query(VMwareEsxi).get(id)
    elif type == "nutanix":
        hypervisor = session.query(NutanixAHV).get(id)
    session.close()
    return hypervisor


def delete_hypervisor(id, type, Session):
    if Session is None:
        print("Session is not initialized")
        return
    session = Session()
    hypervisor = None
    if type == "vmware":
        hypervisor = session.query(VMwareEsxi).get(id)
    elif type == "nutanix":
        hypervisor = session.query(NutanixAHV).get(id)
    if hypervisor is None:
        print("Hypervisor not found")
        session.close()
        return
    session.delete(hypervisor)
    session.commit()
    session.close()


def get_databases(Session):
    if Session is None:
        print("Session is not initialized")
        return []
    session = Session()
    databases = session.query(Database).all()
    session.close()
    return databases


def add_database(
    name, type, alias, host, port, login, password, Session, servername=None
):
    if Session is None:
        print("Session is not initialized")
        return
    session = Session()
    configuration = session.query(Configuration).get(1)
    if configuration is None:
        print("Configuration not found")
        session.close()
        return
    database = Database(
        name=name,
        servername=servername,
        type=type,
        alias=alias,
        host=host,
        port=port,
        login=login,
        password=password,
        configuration=configuration,
    )
    configuration.databases.append(database)
    session.commit()
    session.flush()  # Ensure it's fully persisted
    session.refresh(database)  # Make sure we can access all its attributes
    session.close()
    return database


def update_database(
    id, name, type, alias, host, port, login, password, Session, servername=None
):
    if Session is None:
        print("Session is not initialized")
        return
    session = Session()
    database = session.query(Database).get(id)
    if database is None:
        print("Database not found")
        session.close()
        return
    database.name = name
    database.servername = servername
    database.type = type
    database.alias = alias
    database.host = host
    database.port = port
    database.login = login
    database.password = password
    session.commit()
    session.flush()  # Ensure it's fully persisted
    session.refresh(database)  # Make sure we can access all its attributes
    session.close()
    return database


def delete_database(id, Session):
    if Session is None:
        print("Session is not initialized")
        return
    session = Session()
    database = session.query(Database).get(id)
    if database is None:
        print("Database not found")
        session.close()
        return
    session.delete(database)
    session.commit()
    session.close()


def test_database(type, name, host, port, login, password, servername=None):
    print("Trying connection to db")

    def decode(str):
        return base64.b64decode(str).decode("utf-8")

    try:
        if type == "Postgresql":
            conn = psycopg2.connect(
                dbname=name,
                user=decode(login),
                password=decode(password),
                host=host,
                port=port,
            )
            conn.close()
            return {"is_valid": True}
        if type == "Informix":
            return test_informix(
                host, servername, decode(login), decode(password), name, port
            )
    except Exception as e:
        print(f"Error: {e}")
        error = {"is_valid": False, "error": str(e)}
        return error


def test_informix(db_host, db_server, db_user, db_password, db_database, db_port):
    try:
        sqlhost_file = os.getenv(
            "SQLHOSTS_FILE", "/opt/IBM/Informix.4.50.FC11W1/etc/sqlhosts"
        )
        sqlhost_string = f"{db_server} onsoctcp {db_host} {db_port}"
        try:
            with open(sqlhost_file, "w") as f:
                f.write(sqlhost_string)
        except Exception as e:
            print(f"Error : {e}")

        env = os.environ.copy()

        env["PYTHONPATH"] = "/home/devops/venv_37/lib/python3.7/site-packages"

        result = subprocess.run(
            [
                "/home/devops/venv_37/bin/python3.7",
                "/home/devops/venv_37/informix_test.py",
                db_host,
                db_server,
                db_user,
                db_password,
                db_database,
                str(db_port),
            ],
            capture_output=True,
            text=True,
        )

        result_stdout = result.stdout
        result_stderr = result.stderr
        print(f"result : {result_stdout}")
        print(f"error : {result_stderr}")
        locale_error = result_stdout.find("-23197")
        print("local error", locale_error)
        if locale_error > -1 or not result_stdout:
            return {"is_valid": True}

        error = {"is_valid": False, "error": str(result_stdout)}
        return error

    except Exception as e:
        print(f"Error: {e}")
        error = {"is_valid": False, "error": str(e)}
        return error


def url_parser(url):
    print("url parser...")
    http_regex = r"https?://"
    port_regex = r":\d{1,5}"
    if re.match(http_regex, url):
        protocol, url = url.split("://")
        host = url.split(":")[0].split("/")[0]
        print(url)
        if re.findall(port_regex, url):
            print("port found")
            print(re.findall(port_regex, url)[0])
            port = re.findall(port_regex, url)[0].split(":")[1]
            print(f"PORT {port}")
        else:
            port = 80 if protocol == "http" else 443
    else:
        if len(url.split(":")) > 1:
            host, port = url.split(":")
            print(f"URL PARSER RESULT : {host} {port}")
        else:
            host = url.split("/")[0]
            port = 80
    return host, port


def test_services(destination, Session, port=None):
    if not port:
        print(destination, port)
        try:
            host, port1 = url_parser(destination)
            return test_service_port(host, port1)
        except Exception as e:
            print(f"An error occurred: {e}")
            return False
    else:
        return test_service_port(destination, port)


def get_monitoring_config(Session):
    if Session is None:
        print("Session is not initialized")
        return None
    session = Session()
    monitoring = session.query(Monitoring).get(1)
    session.close()
    if monitoring is None:
        print("Monitoring configuration not found")
        return None
    return monitoring


def update_monitoring_config(
    deploy_embeded_monitoring_stack,
    logs_retention_period,
    logs_retention_disk_space,
    metrics_retention_period,
    metrics_retnetion_disk_space,
    Session,
):
    if Session is None:
        print("Session is not initialized")
        return
    session = Session()
    monitoring = session.query(Monitoring).get(1)
    if monitoring is None:
        print("Monitoring configuration not found")
        session.close()
        return
    monitoring.deploy_embeded_monitoring_stack = deploy_embeded_monitoring_stack
    monitoring.logs_retention_period = logs_retention_period
    monitoring.logs_retention_disk_space = logs_retention_disk_space
    monitoring.metrics_retention_period = metrics_retention_period
    monitoring.metrics_retnetion_disk_space = metrics_retnetion_disk_space
    session.commit()
    session.refresh(monitoring)
    session.close()
    return monitoring


def get_ldaps(Session):
    if Session is None:
        print("Session is not initialized")
        return []
    session = Session()
    ldaps = session.query(Ldap).all()
    session.close()
    return ldaps


def add_ldap(
    ldap_type,
    ldap_url,
    ldap_port,
    bind_dn,
    bind_credentials,
    user_dn,
    user_ldap_attributes,
    search_scope,
    Session,
):
    if Session is None:
        print("Session is not initialized")
        return
    session = Session()
    configuration = session.query(Configuration).get(1)
    if configuration is None:
        print("Configuration not found")
        session.close()
        return
    ldap = Ldap(
        ldap_type=ldap_type,
        ldap_url=ldap_url,
        ldap_port=ldap_port,
        bind_dn=bind_dn,
        bind_credentials=bind_credentials,
        user_dn=user_dn,
        user_ldap_attributes=user_ldap_attributes,
        search_scope=search_scope,
        configuration=configuration,
    )
    configuration.ldaps.append(ldap)
    session.commit()
    session.refresh(ldap)
    session.close()
    return ldap


def update_ldap(
    id,
    ldap_type,
    ldap_url,
    ldap_port,
    bind_dn,
    bind_credentials,
    user_dn,
    user_ldap_attributes,
    search_scope,
    Session,
):
    if Session is None:
        print("Session is not initialized")
        return
    session = Session()
    ldap = session.query(Ldap).get(id)
    if ldap is None:
        print("Ldap not found")
        session.close()
        return
    ldap.ldap_type = ldap_type
    ldap.ldap_url = ldap_url
    ldap.ldap_port = ldap_port
    ldap.bind_dn = bind_dn
    ldap.bind_credentials = bind_credentials
    ldap.user_dn = user_dn
    ldap.user_ldap_attributes = user_ldap_attributes
    ldap.search_scope = search_scope
    session.commit()
    session.refresh(ldap)
    session.close()
    return ldap


def delete_ldap(id, Session):
    if Session is None:
        print("Session is not initialized")
        return
    session = Session()
    ldap = session.query(Ldap).get(id)
    if ldap is None:
        print("Ldap not found")
        session.close()
        return
    session.delete(ldap)
    session.commit()
    session.close()


def get_security(Session):
    if Session is None:
        print("Session is not initialized")
        return None
    session = Session()
    security = session.query(Security).get(1)
    session.close()
    if security is None:
        print("Security configuration not found")
        return None
    return security


def update_security(
    use_proxy,
    porxy_host,
    proxy_port,
    proxy_login,
    proxy_password,
    ssh_pulic_key,
    ssh_private_key,
    ssh_private_key_pwd,
    base_domain,
    env_prefix,
    pem_certificate,
    Session,
):
    if Session is None:
        print("Session is not initialized")
        return
    session = Session()
    security = session.query(Security).get(1)
    if security is None:
        print("Security configuration not found")
        session.close()
        return
    security.use_proxy = use_proxy
    security.porxy_host = porxy_host
    security.proxy_port = proxy_port
    security.proxy_login = proxy_login
    security.proxy_password = proxy_password
    security.ssh_pulic_key = ssh_pulic_key
    security.ssh_private_key = ssh_private_key
    security.ssh_private_key_pwd = ssh_private_key_pwd
    security.base_domain = base_domain
    security.env_prefix = env_prefix
    security.pem_certificate = pem_certificate
    session.commit()
    session.refresh(security)
    session.close()
    return security


def get_zones(Session):
    if Session is None:
        print("Session is not initialized")
        return []
    session = Session()
    zones = session.query(Zone).all()
    session.close()
    return zones


def get_zone_by_id(id, Session):
    if Session is None:
        print("Session is not initialized")
        return None
    session = Session()
    zone = session.query(Zone).options(joinedload(Zone.virtual_machines)).get(id)
    session.close()
    return zone


def add_zone(
    name,
    sub_network,
    network_mask,
    dns,
    hypervisor_type,
    gateway,
    domain,
    vlan_name,
    hypervisor_id,
    ip_pool_start,
    ip_pool_end,
    Session,
):
    if Session is None:
        print("Session is not initialized")
        return
    session = Session()
    zone = None

    if hypervisor_type == "vmware":
        vmware = session.query(VMwareEsxi).get(hypervisor_id)
        if vmware is None:
            print("VMware Esxi configuration not found")
            session.close()
            return
        zone = Zone(
            name=name,
            sub_network=sub_network,
            network_mask=network_mask,
            dns=dns,
            hypervisor_type=hypervisor_type,
            gateway=gateway,
            domain=domain,
            vlan_name=vlan_name,
            ip_pool_start=ip_pool_start,
            ip_pool_end=ip_pool_end,
            vmware=vmware,
        )
    elif hypervisor_type == "nutanix":
        nutanix = session.query(NutanixAHV).get(hypervisor_id)
        if nutanix is None:
            print("Nutanix AHV configuration not found")
            session.close()
            return
        zone = Zone(
            name=name,
            sub_network=sub_network,
            network_mask=network_mask,
            dns=dns,
            hypervisor_type=hypervisor_type,
            gateway=gateway,
            domain=domain,
            vlan_name=vlan_name,
            ip_pool_start=ip_pool_start,
            ip_pool_end=ip_pool_end,
            nutanix=nutanix,
        )
    if zone is not None:
        session.add(zone)
        session.commit()
        session.refresh(zone)

    session.close()
    return zone


def update_zone(
    id,
    name,
    sub_network,
    network_mask,
    dns,
    hypervisor_type,
    gateway,
    domain,
    vlan_name,
    hypervisor_id,
    ip_pool_start,
    ip_pool_end,
    Session,
):
    if Session is None:
        print("Session is not initialized")
        return
    session = Session()
    zone = None  # Initialize zone to None
    try:
        # Fetch the existing Zone by ID
        zone = session.query(Zone).get(id)
        if zone is None:
            print("Zone not found")
            return

        # Update zone attributes
        zone.name = name
        zone.sub_network = sub_network
        zone.network_mask = network_mask
        zone.dns = dns
        zone.hypervisor_type = hypervisor_type
        zone.gateway = gateway
        zone.domain = domain
        zone.vlan_name = vlan_name
        zone.ip_pool_start = ip_pool_start
        zone.ip_pool_end = ip_pool_end

        # Handle specific hypervisor configurations
        if hypervisor_type == "vmware":
            vmware = session.query(VMwareEsxi).get(hypervisor_id)
            if vmware is None:
                print("VMware Esxi configuration not found")
                return
            zone.vmware = vmware  # Update VMware relationship
            zone.nutanix = None  # Clear Nutanix relationship if switching types
        elif hypervisor_type == "nutanix":
            nutanix = session.query(NutanixAHV).get(hypervisor_id)
            if nutanix is None:
                print("Nutanix AHV configuration not found")
                return
            zone.nutanix = nutanix  # Update Nutanix relationship
            zone.vmware = None  # Clear VMware relationship if switching types

        # Commit the changes
        session.commit()

        # Refresh the object to ensure it's up-to-date
        session.refresh(zone)
    except Exception as e:
        session.rollback()
        print(f"An error occurred: {e}")
    finally:
        session.close()

        return zone


# Client-specific service functions removed:
# Firebase: get_firebase_db, add_firebase_db, update_firebase_db
# Facebook: get_facebook, add_facebook, update_facebook  
# Signature: get_signature, add_signature, update_signature
# FCM: get_fcm, add_fcm, update_fcm
# Google: get_google, add_google, update_google

def get_sms_providers(Session):
    if Session is None:
        print("Session is not initialized")
        return []
    session = Session()
    sms_providers = session.query(SMSProvider).all()
    session.close()
    return sms_providers


def add_sms_provider(url, login, password, binder, Session):
    if Session is None:
        print("Session is not initialized")
        return
    session = Session()
    configuration = session.query(Configuration).get(1)
    if configuration is None:
        print("Configuration not found")
        session.close()
        return
    sms_provider = SMSProvider(
        url=url,
        login=login,
        password=password,
        binder=binder,
        configuration=configuration,
    )
    configuration.sms_providers.append(sms_provider)
    session.commit()
    session.refresh(sms_provider)
    session.close()
    return sms_provider


def clear_vault_table(Session):
    if Session is None:
        print("Session is not initialized")
        return
    session = Session()
    session.query(VaultCredentials).delete()
    session.commit()
    session.close()


def add_vault_keys(keys, Session):
    if Session is None:
        print("Session is not initialized")
        return
    session = Session()
    for key in keys:
        payload = VaultCredentials(type="key", value=key)
        session.add(payload)
    session.commit()
    session.close()

    return keys


def add_vault_token(token, Session):
    if Session is None:
        print("Session is not initialized")
        return
    session = Session()
    token_payload = VaultCredentials(type="token", value=token)
    session.add(token_payload)
    session.commit()
    session.close()

    return token_payload


def update_sms_provider(id, url, login, password, binder, Session):
    if Session is None:
        print("Session is not initialized")
        return
    session = Session()
    sms_provider = session.query(SMSProvider).get(id)
    if sms_provider is None:
        print("SMS Provider not found")
        session.close()
        return
    sms_provider.url = url
    sms_provider.login = login
    sms_provider.password = password
    sms_provider.binder = binder

    session.commit()
    session.refresh(sms_provider)
    session.close()
    return sms_provider


def delete_sms_provider(id, Session):
    if Session is None:
        print("Session is not initialized")
        return
    session = Session()
    sms_provider = session.query(SMSProvider).get(id)
    if sms_provider is None:
        print("SMS Provider not found", id)
        session.close()
        return
    session.delete(sms_provider)
    session.commit()
    session.close()
    return sms_provider


def get_smtp_servers(Session):
    if Session is None:
        print("Session is not initialized")
        return []
    session = Session()
    smtp_servers = session.query(SMTPServer).all()
    session.close()
    return smtp_servers


def add_smtp_server(host, port, login, password, mail_from, use_tls_ssl, Session):
    if Session is None:
        print("Session is not initialized")
        return
    session = Session()
    configuration = session.query(Configuration).get(1)
    if configuration is None:
        print("Configuration not found")
        session.close()
        return
    smtp_server = SMTPServer(
        host=host,
        port=port,
        login=login,
        password=password,
        mail_from=mail_from,
        use_tls_ssl=use_tls_ssl,
        configuration=configuration,
    )
    configuration.smtp_servers.append(smtp_server)
    session.commit()
    session.refresh(smtp_server)
    session.close()
    return smtp_server


def update_smtp_provider(
    id, host, login, password, mail_from, use_tls_ssl, port, Session
):
    if Session is None:
        print("Session is not initialized")
        return
    session = Session()
    smtp_provider = session.query(SMTPServer).get(id)
    if smtp_provider is None:
        print("SMTP Provider not found")
        session.close()
        return
    smtp_provider.host = host
    smtp_provider.login = login
    smtp_provider.password = password
    smtp_provider.mail_from = mail_from
    smtp_provider.use_tls_ssl = use_tls_ssl
    smtp_provider.port = port
    session.commit()
    session.refresh(smtp_provider)
    session.close()
    return smtp_provider


def delete_smtp_server(id, Session):
    if Session is None:
        print("Session is not initialized")
        return
    session = Session()
    smtp_server = session.query(SMTPServer).get(id)
    if smtp_server is None:
        print("SMTP Server not found", id)
        session.close()
        return
    session.delete(smtp_server)
    session.commit()
    session.close()
    return smtp_server


# Client-specific service functions removed:
# Arcgis: get_arcgis_servers, add_arcgis_server, update_arcgis_provider, delete_arcgis_server
# Payment: get_payment_providers, add_payment_provider, update_payment_provider, delete_payment_provider
# Publishing: get_publishing_providers, add_publishing_provider, update_publishing_provider, delete_publishing_provider


# Client-specific server management functions removed:
# add_server(), update_server(), delete_server()
# These only handled client-specific services (Alfresco, Auth, GCBO, GMAO, Firebase, etc.)


def get_services(Session):
    """Get all generic services (SMS, SMTP, LDAP, Database)"""
    if Session is None:
        print("Session is not initialized")
        return []
    session = Session()
    result = []
    
    # Generic services only - client-specific services removed
    # get all sms providers
    sms_providers = session.query(SMSProvider).all()
    for sms_provider in sms_providers:
        result.append({"id": sms_provider.id, "type": "sms_provider"})
    
    # get all smtp servers
    smtp_servers = session.query(SMTPServer).all()
    for smtp_server in smtp_servers:
        result.append({"id": smtp_server.id, "type": "smtp_server"})
    
    # get all ldap providers
    ldap_providers = session.query(Ldap).all()
    for ldap_provider in ldap_providers:
        result.append(
            {
                "id": ldap_provider.id,
                "type": ldap_provider.ldap_type,
            }
        )
    
    # get all databases
    databases = session.query(Database).all()
    for database in databases:
        result.append({"id": database.id, "type": "database"})
    
    session.close()
    return result


def get_service(id, type, Session):
    """Get a specific generic service by ID and type"""
    if Session is None:
        print("Session is not initialized")
        return None
    session = Session()
    service = None
    
    # Generic services only - client-specific services removed
    if type == "sms_provider":
        service = session.query(SMSProvider).get(id)
    elif type == "smtp_server":
        service = session.query(SMTPServer).get(id)
    elif type == "ldap":
        service = session.query(Ldap).get(id)
    elif type == "internal_users":
        service = session.query(Ldap).get(id)
    elif type == "external_users":
        service = session.query(Ldap).get(id)
    elif type == "database":
        service = session.query(Database).get(id)

    session.close()
    return service


# get_server() function removed - only handled client-specific services
# (alfresco, auth, gcbo, gmao, firebase, fcm, google, facebook, signature)


def get_virtual_machines(Session):
    if Session is None:
        print("Session is not initialized")
        return []
    session = Session()
    virtual_machines = session.query(VirtualMachine).all()
    session.close()
    return virtual_machines


def add_virtual_machine(
    hostname,
    roles,
    ip,
    group,
    nb_cpu,
    ram,
    os_disk_size,
    data_disk_size,
    zone_id,
    Session,
):
    if Session is None:
        print("Session is not initialized")
        return
    session = Session()
    zone = session.query(Zone).get(zone_id)
    if zone is None:
        print("Zone not found")
        session.close()
        return
    virtual_machine = VirtualMachine(
        hostname=hostname,
        roles=roles,
        group=group,
        ip=ip,
        nb_cpu=nb_cpu,
        ram=ram,
        os_disk_size=os_disk_size,
        data_disk_size=data_disk_size,
        zone=zone,
    )
    zone.virtual_machines.append(virtual_machine)
    session.commit()
    session.close()
    return virtual_machine


def update_virtual_machine(
    id,
    hostname,
    roles,
    group,
    ip,
    nb_cpu,
    ram,
    os_disk_size,
    data_disk_size,
    status,
    zone_id,
    Session,
):
    if Session is None:
        print("Session is not initialized")
        return
    session = Session()
    virtual_machine = session.query(VirtualMachine).get(id)
    if virtual_machine is None:
        print("Virtual Machine not found")
        session.close()
        return
    virtual_machine.hostname = hostname
    virtual_machine.roles = roles
    virtual_machine.group = group
    virtual_machine.ip = ip
    virtual_machine.nb_cpu = nb_cpu
    virtual_machine.ram = ram
    virtual_machine.os_disk_size = os_disk_size
    virtual_machine.data_disk_size = data_disk_size
    virtual_machine.status = status
    zone = session.query(Zone).get(zone_id)
    if zone is None:
        print("Zone not found")
        session.close()
        return
    virtual_machine.zone = zone
    session.commit()
    session.refresh(virtual_machine)
    if group == "LBLAN":
        update_dns_related_ip(ip, Session)
    elif group == "LBINTEGRATION":
        update_flow_matrix_source(ip, Session)
    session.close()
    return virtual_machine


def update_status_vm(id, status, Session):
    if Session is None:
        print("Session is not initialized")
        return
    session = Session()
    virtual_machine = session.query(VirtualMachine).get(id)
    if virtual_machine is None:
        print("Virtual Machine not found")
        session.close()
        return
    virtual_machine.status = status
    session.commit()
    session.close()
    return virtual_machine


def get_vms_to_create(Session):
    if Session is None:
        print("Session is not initialized")
        return []
    session = Session()
    virtual_machines = (
        session.query(VirtualMachine).filter(VirtualMachine.status == "to_create").all()
    )
    session.close()
    return virtual_machines


def get_vms_by_group(group, Session):
    if Session is None:
        print("Session is not initialized")
        return []
    session = Session()
    virtual_machines = (
        session.query(VirtualMachine).filter(VirtualMachine.group == group).all()
    )
    session.close()
    return virtual_machines


def get_vault_token(Session):
    if Session is None:
        print("Session is not initialized")
        return []
    session = Session()
    token = (
        session.query(VaultCredentials).filter(VaultCredentials.type == "token").first()
    )
    session.close()
    return token.value


def get_vault_creds(Session):
    if Session is None:
        print("Session is not initialized")
        return []
    session = Session()
    creds = session.query(VaultCredentials).all()
    session.close()
    return creds


def get_all_dns(Session):
    if Session is None:
        print("Session is not initialized")
        return []
    session = Session()
    dns = session.query(Dns).all()
    session.close()
    return dns


def add_dns(name, hostname, ip, Session):
    if Session is None:
        print("Session is not initialized")
        return
    session = Session()
    try:
        dns = Dns(
            name=name,
            hostname=hostname,
            ip=ip,
        )
        session.add(dns)
        session.commit()
        return dns
    finally:
        session.close()


def update_dns_related_ip(new_ip, Session):
    if Session is None:
        print("Session is not initialized")
        return

    session = Session()
    try:
        session.query(Dns).update({Dns.ip: new_ip}, synchronize_session=False)
        session.commit()
        print(f"All FlowMatrix sources updated to: {new_ip}")
    except Exception as e:
        session.rollback()
        print(f"Error during update: {e}")
    finally:
        session.close()


def get_flow_matrix(Session):
    if Session is None:
        print("Session is not initialized")
        return []
    session = Session()
    flow_matrix = session.query(FlowMatrix).all()
    session.close()
    return flow_matrix


def add_flow_matrix(source, destination, protocol, port, Session, description=None):
    if Session is None:
        print("Session is not initialized")
        return
    session = Session()
    flow_matrix = FlowMatrix(
        source=source,
        destination=destination,
        protocol=protocol,
        port=port,
        description=description,
    )
    session.add(flow_matrix)
    session.commit()
    session.close()

    return flow_matrix


def update_status_flow(id, is_open, Session):
    if Session is None:
        print("Session is not initialized")
        return
    session = Session()
    flow_matrix = session.query(FlowMatrix).get(id)
    if flow_matrix is None:
        print("Flow Matrix not found")
        session.close()
        return
    flow_matrix.is_open = is_open
    session.commit()
    session.close()
    return flow_matrix


def update_flow_matrix_source(new_source, Session):
    if Session is None:
        print("Session is not initialized")
        return

    session = Session()
    try:
        session.query(FlowMatrix).update(
            {FlowMatrix.source: new_source}, synchronize_session=False
        )
        session.commit()
        print(f"All FlowMatrix sources updated to: {new_source}")
    except Exception as e:
        session.rollback()
        print(f"Error during update: {e}")
    finally:
        session.close()


def get_ansible_roles(Session):
    if Session is None:
        print("Session is not initialized")
        return []
    session = Session()
    ansible_roles = (
        session.query(AnsibleRole)
        # .filter(AnsibleRole.status.notin_(["failed", "successful"]))
        .order_by(AnsibleRole.order.asc())
        .all()
    )
    session.close()
    return ansible_roles


def add_ansible_role(role_name, order, Session):
    if Session is None:
        print("Session is not initialized")
        return
    session = Session()
    ansible_role = AnsibleRole(
        role_name=role_name,
        order=order,
        start_time=datetime.datetime.now(),
        status="init",
    )
    session.add(ansible_role)
    session.commit()
    session.close()
    return ansible_role


def update_ansible_role(role_name, runner_ident, status, Session):
    if Session is None:
        print("Session is not initialized")
        return
    session = Session()
    # ansible_role = (
    #     session.query(AnsibleRole)
    #     .filter(AnsibleRole.status.notin_(["failed", "successful"]))
    #     .order_by(AnsibleRole.order)
    #     .first()
    # )
    ansible_role = (
        session.query(AnsibleRole).filter(AnsibleRole.role_name == role_name).first()
    )
    if ansible_role is None:
        print("Ansible Role not found")
        session.close()
        return
    ansible_role.status = status
    ansible_role.runner_ident = runner_ident
    if status == "failde" or status == "successful":
        ansible_role.end_time = datetime.datetime.now()
    if status == "starting":
        ansible_role.start_time = datetime.datetime.now()
    session.commit()
    session.close()
    return ansible_role


def get_ansible_role_status(role_name, Session):
    if Session is None:
        print("Session is not initialized")
        return
    session = Session()
    ansible_role = (
        session.query(AnsibleRole).filter(AnsibleRole.role_name == role_name).first()
    )
    return ansible_role.status


def get_task_logs(runner_ident, Session):
    if Session is None:
        print("Session is not initialized")
        return []
    session = Session()
    task_logs = (
        session.query(TaskLog)
        .filter(TaskLog.runner_ident == runner_ident)
        .order_by(TaskLog.id.asc())
        .all()
    )
    session.close()
    return task_logs


def delete_all_ansible_roles(Session):
    if Session is None:
        print("Session is not initialized")
        return
    session = Session()
    session.query(TaskLog).delete()
    session.query(AnsibleRole).delete()
    session.commit()
    session.close()


def get_task_logs(runner_ident, Session):
    if Session is None:
        print("Session is not initialized")
        return []
    session = Session()
    task_logs = (
        session.query(TaskLog)
        .filter(TaskLog.runner_ident == runner_ident)
        .order_by(TaskLog.id.asc())
        .all()
    )
    session.close()
    return task_logs


def add_task_logs(event, task, stdout, runner_ident, Session):
    if Session is None:
        print("Session is not initialized")
        return
    session = Session()
    task_log = TaskLog(
        event=event,
        task=task,
        stdout=stdout,
        runner_ident=runner_ident,
    )
    session.add(task_log)
    session.commit()
    session.close()
    return task_log


# Product-specific DNS functions removed (add_dns_gco, add_dns_eservices)
# Add custom DNS entries manually using add_dns() function as needed


def increment_ip(ip, n=1):
    parts = list(map(int, ip.split(".")))
    for _ in range(n):
        parts[3] += 1
        for i in range(3, -1, -1):
            if parts[i] > 255:
                parts[i] = 0
                if i > 0:
                    parts[i - 1] += 1
    return ".".join(map(str, parts))


def ip_to_int(ip):
    """
    Convert IP address string to 32-bit integer for numeric comparison.
    Example: "192.168.1.1" -> 3232235777
    """
    parts = list(map(int, ip.split(".")))
    return (parts[0] << 24) + (parts[1] << 16) + (parts[2] << 8) + parts[3]


def int_to_ip(num):
    """
    Convert 32-bit integer back to IP address string.
    Example: 3232235777 -> "192.168.1.1"
    """
    return ".".join(str((num >> (8 * (3 - i))) & 255) for i in range(4))


def is_ip_in_pool(ip, pool_start, pool_end):
    """
    Check if an IP address is within the specified pool range.
    Returns True if IP is in [pool_start, pool_end], False otherwise.
    """
    ip_int = ip_to_int(ip)
    start_int = ip_to_int(pool_start)
    end_int = ip_to_int(pool_end)
    return start_int <= ip_int <= end_int


def get_next_available_ip(zone_id, Session):
    """
    Find the next available IP address within a zone's defined pool.
    This function:
    1. Gets the zone's IP pool range
    2. Retrieves all currently assigned IPs in that zone
    3. Returns the first unassigned IP in the pool

    Args:
        zone_id: The ID of the zone to allocate an IP from
        Session: The database session

    Returns:
        str: The next available IP address

    Raises:
        Exception: If no IPs are available in the pool
    """
    session = Session()

    try:
        # 1. Get the zone with its IP pool configuration
        zone = session.query(Zone).filter(Zone.id == zone_id).first()
        if not zone:
            raise ValueError(f"Zone with ID {zone_id} not found")

        if not zone.ip_pool_start or not zone.ip_pool_end:
            raise ValueError(f"Zone {zone.name} does not have IP pool configured")

        # 2. Get all currently assigned IPs in this zone
        assigned_ips = {
            vm.ip
            for vm in session.query(VirtualMachine)
            .filter(VirtualMachine.zone_id == zone_id)
            .all()
        }

        # 3. Iterate through the pool to find the first available IP
        current_ip_int = ip_to_int(zone.ip_pool_start)
        end_ip_int = ip_to_int(zone.ip_pool_end)

        while current_ip_int <= end_ip_int:
            current_ip = int_to_ip(current_ip_int)

            # Check if this IP is already assigned
            if current_ip not in assigned_ips:
                session.close()
                return current_ip

            current_ip_int += 1

        # If we get here, the pool is exhausted
        raise Exception(
            f"No available IP addresses in zone '{zone.name}' "
            f"(pool: {zone.ip_pool_start} - {zone.ip_pool_end})"
        )

    finally:
        session.close()


def a_configurations(user_count, Session):
    """
    Get VM configuration for a specific user count.
    Returns a dictionary mapping vm_type to VMConfiguration objects.
    """
    if Session is None:
        print("Session is not initialized")
        return {}
    session = Session()
    configs = (
        session.query(VMConfiguration)
        .filter(VMConfiguration.user_count == user_count)
        .all()
    )
    session.close()

    # Convert to dictionary for easy lookup
    config_dict = {config.vm_type: config for config in configs}
    return config_dict


def seed_vm_configurations(Session):
    """
    Seed the VMConfiguration table with recommended values for different user counts.
    Implements new architecture with CONTROL/WORKER split for Kubernetes clusters.
    - Control plane: 3 master nodes max (RKEAPPS_CONTROL, RKEMIDDLEWARE_CONTROL)
    - Worker nodes: Unlimited (RKEAPPS_WORKER, RKEMIDDLEWARE_WORKER)
    - Load balancers: Always exactly 2 VMs (LBLAN, LBDMZ, LBINTEGRATION)
    - RKEDMZ: Always exactly 3 VMs (fixed)
    """
    if Session is None:
        print("Session is not initialized")
        return

    session = Session()

    # Check if data already exists
    existing_count = session.query(VMConfiguration).count()
    if existing_count > 0:
        print(
            f"VMConfiguration table already has {existing_count} records. Skipping seed."
        )
        session.close()
        return

    # Configuration for 100 users
    configs_100 = [
        # RKEAPPS - Control Plane (3 master nodes with combined roles)
        {
            "user_count": 100,
            "vm_type": "RKEAPPS_CONTROL",
            "node_count": 3,
            "cpu_per_node": 4,
            "ram_per_node": 8192,
            "os_disk_size": 80,
            "data_disk_size": 100,
            "roles": "master,worker,cns",
        },
        # RKEAPPS - CNS (0 for 100 users)
        {
            "user_count": 100,
            "vm_type": "RKEAPPS_CNS",
            "node_count": 0,
            "cpu_per_node": 4,
            "ram_per_node": 8192,
            "os_disk_size": 80,
            "data_disk_size": 100,
            "roles": "worker,cns",
        },
        # RKEAPPS - Worker nodes (0 for 100 users, scales with load)
        {
            "user_count": 100,
            "vm_type": "RKEAPPS_WORKER",
            "node_count": 0,
            "cpu_per_node": 4,
            "ram_per_node": 8192,
            "os_disk_size": 80,
            "data_disk_size": 0,
            "roles": "worker",
        },
        # RKEMIDDLEWARE - Control Plane
        {
            "user_count": 100,
            "vm_type": "RKEMIDDLEWARE_CONTROL",
            "node_count": 3,
            "cpu_per_node": 4,
            "ram_per_node": 8192,
            "os_disk_size": 80,
            "data_disk_size": 100,
            "roles": "master,worker,cns",
        },
        # RKEMIDDLEWARE - CNS (0 for 100 users)
        {
            "user_count": 100,
            "vm_type": "RKEMIDDLEWARE_CNS",
            "node_count": 0,
            "cpu_per_node": 4,
            "ram_per_node": 8192,
            "os_disk_size": 80,
            "data_disk_size": 100,
            "roles": "worker,cns",
        },
        # RKEMIDDLEWARE - Worker nodes
        {
            "user_count": 100,
            "vm_type": "RKEMIDDLEWARE_WORKER",
            "node_count": 0,
            "cpu_per_node": 4,
            "ram_per_node": 8192,
            "os_disk_size": 80,
            "data_disk_size": 0,
            "roles": "worker",
        },
        # RKEDMZ - Fixed 3 nodes
        {
            "user_count": 100,
            "vm_type": "RKEDMZ",
            "node_count": 3,
            "cpu_per_node": 4,
            "ram_per_node": 4096,
            "os_disk_size": 80,
            "data_disk_size": 100,
            "roles": "master,worker,cns",
        },
        # Load Balancers - Always 2 VMs, CPU/RAM scale, disk always 0
        {
            "user_count": 100,
            "vm_type": "LBLAN",
            "node_count": 2,
            "cpu_per_node": 2,
            "ram_per_node": 2048,
            "os_disk_size": 60,
            "data_disk_size": 0,
            "roles": "loadbalancer",
        },
        {
            "user_count": 100,
            "vm_type": "LBDMZ",
            "node_count": 2,
            "cpu_per_node": 2,
            "ram_per_node": 2048,
            "os_disk_size": 60,
            "data_disk_size": 0,
            "roles": "loadbalancer",
        },
        {
            "user_count": 100,
            "vm_type": "LBINTEGRATION",
            "node_count": 2,
            "cpu_per_node": 2,
            "ram_per_node": 2048,
            "os_disk_size": 60,
            "data_disk_size": 0,
            "roles": "loadbalancer",
        },
        # Infrastructure VMs
        {
            "user_count": 100,
            "vm_type": "GITOPS",
            "node_count": 1,
            "cpu_per_node": 4,
            "ram_per_node": 8192,
            "os_disk_size": 60,
            "data_disk_size": 200,
            "roles": "git,docker-registry",
        },
        {
            "user_count": 100,
            "vm_type": "MONITORING",
            "node_count": 1,
            "cpu_per_node": 4,
            "ram_per_node": 16384,
            "os_disk_size": 60,
            "data_disk_size": 200,
            "roles": "admin,monitoring",
        },
        {
            "user_count": 100,
            "vm_type": "VAULT",
            "node_count": 1,
            "cpu_per_node": 4,
            "ram_per_node": 16384,
            "os_disk_size": 60,
            "data_disk_size": 20,
            "roles": "vault",
        },
    ]

    # Configuration for 500 users
    configs_500 = [
        # RKEAPPS - Control Plane
        {
            "user_count": 500,
            "vm_type": "RKEAPPS_CONTROL",
            "node_count": 3,
            "cpu_per_node": 4,
            "ram_per_node": 8192,
            "os_disk_size": 80,
            "data_disk_size": 0,
            "roles": "master",
        },
        # RKEAPPS - CNS (3 for 500 users)
        {
            "user_count": 500,
            "vm_type": "RKEAPPS_CNS",
            "node_count": 3,
            "cpu_per_node": 4,
            "ram_per_node": 8192,
            "os_disk_size": 80,
            "data_disk_size": 150,
            "roles": "worker,cns",
        },
        # RKEAPPS - Worker nodes (1 for 500 users)
        {
            "user_count": 500,
            "vm_type": "RKEAPPS_WORKER",
            "node_count": 1,
            "cpu_per_node": 4,
            "ram_per_node": 8196,
            "os_disk_size": 80,
            "data_disk_size": 0,
            "roles": "worker",
        },
        # RKEMIDDLEWARE - Control Plane
        {
            "user_count": 500,
            "vm_type": "RKEMIDDLEWARE_CONTROL",
            "node_count": 3,
            "cpu_per_node": 4,
            "ram_per_node": 8192,
            "os_disk_size": 80,
            "data_disk_size": 0,
            "roles": "master",
        },
        # RKEMIDDLEWARE - CNS (3 for 500 users)
        {
            "user_count": 500,
            "vm_type": "RKEMIDDLEWARE_CNS",
            "node_count": 3,
            "cpu_per_node": 4,
            "ram_per_node": 8192,
            "os_disk_size": 100,
            "data_disk_size": 150,
            "roles": "worker,cns",
        },
        # RKEMIDDLEWARE - Worker nodes
        {
            "user_count": 500,
            "vm_type": "RKEMIDDLEWARE_WORKER",
            "node_count": 1,
            "cpu_per_node": 4,
            "ram_per_node": 8192,
            "os_disk_size": 80,
            "data_disk_size": 0,
            "roles": "worker",
        },
        # RKEDMZ - Fixed 3 nodes
        {
            "user_count": 500,
            "vm_type": "RKEDMZ",
            "node_count": 3,
            "cpu_per_node": 4,
            "ram_per_node": 8192,
            "os_disk_size": 80,
            "data_disk_size": 200,
            "roles": "master,worker,cns",
        },
        # Load Balancers - Always 2 VMs
        {
            "user_count": 500,
            "vm_type": "LBLAN",
            "node_count": 2,
            "cpu_per_node": 4,
            "ram_per_node": 4096,
            "os_disk_size": 60,
            "data_disk_size": 0,
            "roles": "loadbalancer",
        },
        {
            "user_count": 500,
            "vm_type": "LBDMZ",
            "node_count": 2,
            "cpu_per_node": 4,
            "ram_per_node": 4096,
            "os_disk_size": 60,
            "data_disk_size": 0,
            "roles": "loadbalancer",
        },
        {
            "user_count": 500,
            "vm_type": "LBINTEGRATION",
            "node_count": 2,
            "cpu_per_node": 2,
            "ram_per_node": 2048,
            "os_disk_size": 60,
            "data_disk_size": 0,
            "roles": "loadbalancer",
        },
        # Infrastructure VMs
        {
            "user_count": 500,
            "vm_type": "GITOPS",
            "node_count": 1,
            "cpu_per_node": 4,
            "ram_per_node": 8192,
            "os_disk_size": 60,
            "data_disk_size": 200,
            "roles": "git,docker-registry",
        },
        {
            "user_count": 500,
            "vm_type": "MONITORING",
            "node_count": 1,
            "cpu_per_node": 4,
            "ram_per_node": 8192,
            "os_disk_size": 60,
            "data_disk_size": 200,
            "roles": "admin,monitoring",
        },
        {
            "user_count": 500,
            "vm_type": "VAULT",
            "node_count": 1,
            "cpu_per_node": 4,
            "ram_per_node": 8192,
            "os_disk_size": 60,
            "data_disk_size": 20,
            "roles": "vault",
        },
    ]

    # Configuration for 1000 users
    configs_1000 = [
        # RKEAPPS - Control Plane
        {
            "user_count": 1000,
            "vm_type": "RKEAPPS_CONTROL",
            "node_count": 3,
            "cpu_per_node": 4,
            "ram_per_node": 8192,
            "os_disk_size": 80,
            "data_disk_size": 0,
            "roles": "master",
        },
        # RKEAPPS - CNS (3 for 1000 users)
        {
            "user_count": 1000,
            "vm_type": "RKEAPPS_CNS",
            "node_count": 3,
            "cpu_per_node": 4,
            "ram_per_node": 8192,
            "os_disk_size": 80,
            "data_disk_size": 200,
            "roles": "worker,cns",
        },
        # RKEAPPS - Worker nodes (5 for 1000 users)
        {
            "user_count": 1000,
            "vm_type": "RKEAPPS_WORKER",
            "node_count": 5,
            "cpu_per_node": 8,
            "ram_per_node": 16384,
            "os_disk_size": 80,
            "data_disk_size": 0,
            "roles": "worker",
        },
        # RKEMIDDLEWARE - Control Plane
        {
            "user_count": 1000,
            "vm_type": "RKEMIDDLEWARE_CONTROL",
            "node_count": 3,
            "cpu_per_node": 4,
            "ram_per_node": 8192,
            "os_disk_size": 80,
            "data_disk_size": 0,
            "roles": "master",
        },
        # RKEMIDDLEWARE - CNS (3 for 1000 users)
        {
            "user_count": 1000,
            "vm_type": "RKEMIDDLEWARE_CNS",
            "node_count": 3,
            "cpu_per_node": 4,
            "ram_per_node": 8192,
            "os_disk_size": 80,
            "data_disk_size": 200,
            "roles": "worker,cns",
        },
        # RKEMIDDLEWARE - Worker nodes
        {
            "user_count": 1000,
            "vm_type": "RKEMIDDLEWARE_WORKER",
            "node_count": 4,
            "cpu_per_node": 8,
            "ram_per_node": 16384,
            "os_disk_size": 80,
            "data_disk_size": 0,
            "roles": "worker",
        },
        # RKEDMZ - Fixed 3 nodes
        {
            "user_count": 1000,
            "vm_type": "RKEDMZ",
            "node_count": 3,
            "cpu_per_node": 6,
            "ram_per_node": 8192,
            "os_disk_size": 80,
            "data_disk_size": 250,
            "roles": "master,worker,cns",
        },
        # Load Balancers - Always 2 VMs
        {
            "user_count": 1000,
            "vm_type": "LBLAN",
            "node_count": 2,
            "cpu_per_node": 4,
            "ram_per_node": 4096,
            "os_disk_size": 60,
            "data_disk_size": 0,
            "roles": "loadbalancer",
        },
        {
            "user_count": 1000,
            "vm_type": "LBDMZ",
            "node_count": 2,
            "cpu_per_node": 4,
            "ram_per_node": 4096,
            "os_disk_size": 60,
            "data_disk_size": 0,
            "roles": "loadbalancer",
        },
        {
            "user_count": 1000,
            "vm_type": "LBINTEGRATION",
            "node_count": 2,
            "cpu_per_node": 4,
            "ram_per_node": 4096,
            "os_disk_size": 60,
            "data_disk_size": 0,
            "roles": "loadbalancer",
        },
        # Infrastructure VMs
        {
            "user_count": 1000,
            "vm_type": "GITOPS",
            "node_count": 1,
            "cpu_per_node": 4,
            "ram_per_node": 8192,
            "os_disk_size": 60,
            "data_disk_size": 200,
            "roles": "git,docker-registry",
        },
        {
            "user_count": 1000,
            "vm_type": "MONITORING",
            "node_count": 1,
            "cpu_per_node": 6,
            "ram_per_node": 16384,
            "os_disk_size": 60,
            "data_disk_size": 200,
            "roles": "admin,monitoring",
        },
        {
            "user_count": 1000,
            "vm_type": "VAULT",
            "node_count": 1,
            "cpu_per_node": 4,
            "ram_per_node": 8192,
            "os_disk_size": 60,
            "data_disk_size": 20,
            "roles": "vault",
        },
    ]

    # Configuration for 10000 users
    configs_10000 = [
        # RKEAPPS - Control Plane
        {
            "user_count": 10000,
            "vm_type": "RKEAPPS_CONTROL",
            "node_count": 3,
            "cpu_per_node": 4,
            "ram_per_node": 8192,
            "os_disk_size": 80,
            "data_disk_size": 0,
            "roles": "master",
        },
        # RKEAPPS - CNS (3 for 10000 users)
        {
            "user_count": 10000,
            "vm_type": "RKEAPPS_CNS",
            "node_count": 3,
            "cpu_per_node": 4,
            "ram_per_node": 8192,
            "os_disk_size": 80,
            "data_disk_size": 400,
            "roles": "worker,cns",
        },
        # RKEAPPS - Worker nodes (6 for 10000 users)
        {
            "user_count": 10000,
            "vm_type": "RKEAPPS_WORKER",
            "node_count": 6,
            "cpu_per_node": 8,
            "ram_per_node": 16384,
            "os_disk_size": 80,
            "data_disk_size": 0,
            "roles": "worker",
        },
        # RKEMIDDLEWARE - Control Plane
        {
            "user_count": 10000,
            "vm_type": "RKEMIDDLEWARE_CONTROL",
            "node_count": 3,
            "cpu_per_node": 4,
            "ram_per_node": 8192,
            "os_disk_size": 80,
            "data_disk_size": 0,
            "roles": "master",
        },
        # RKEMIDDLEWARE - CNS (3 for 10000 users)
        {
            "user_count": 10000,
            "vm_type": "RKEMIDDLEWARE_CNS",
            "node_count": 3,
            "cpu_per_node": 4,
            "ram_per_node": 8192,
            "os_disk_size": 80,
            "data_disk_size": 500,
            "roles": "worker,cns",
        },
        # RKEMIDDLEWARE - Worker nodes
        {
            "user_count": 10000,
            "vm_type": "RKEMIDDLEWARE_WORKER",
            "node_count": 12,
            "cpu_per_node": 8,
            "ram_per_node": 16384,
            "os_disk_size": 80,
            "data_disk_size": 0,
            "roles": "worker",
        },
        # RKEDMZ - Fixed 3 nodes
        {
            "user_count": 10000,
            "vm_type": "RKEDMZ",
            "node_count": 3,
            "cpu_per_node": 8,
            "ram_per_node": 16384,
            "os_disk_size": 80,
            "data_disk_size": 200,
            "roles": "master,worker,cns",
        },
        # Load Balancers - Always 2 VMs
        {
            "user_count": 10000,
            "vm_type": "LBLAN",
            "node_count": 2,
            "cpu_per_node": 8,
            "ram_per_node": 8192,
            "os_disk_size": 60,
            "data_disk_size": 0,
            "roles": "loadbalancer",
        },
        {
            "user_count": 10000,
            "vm_type": "LBDMZ",
            "node_count": 2,
            "cpu_per_node": 8,
            "ram_per_node": 8192,
            "os_disk_size": 60,
            "data_disk_size": 0,
            "roles": "loadbalancer",
        },
        {
            "user_count": 10000,
            "vm_type": "LBINTEGRATION",
            "node_count": 2,
            "cpu_per_node": 4,
            "ram_per_node": 4096,
            "os_disk_size": 60,
            "data_disk_size": 0,
            "roles": "loadbalancer",
        },
        # Infrastructure VMs
        {
            "user_count": 10000,
            "vm_type": "GITOPS",
            "node_count": 1,
            "cpu_per_node": 8,
            "ram_per_node": 16384,
            "os_disk_size": 60,
            "data_disk_size": 500,
            "roles": "git,docker-registry",
        },
        {
            "user_count": 10000,
            "vm_type": "MONITORING",
            "node_count": 1,
            "cpu_per_node": 8,
            "ram_per_node": 32768,
            "os_disk_size": 60,
            "data_disk_size": 500,
            "roles": "admin,monitoring",
        },
        {
            "user_count": 10000,
            "vm_type": "VAULT",
            "node_count": 1,
            "cpu_per_node": 4,
            "ram_per_node": 16384,
            "os_disk_size": 60,
            "data_disk_size": 20,
            "roles": "vault",
        },
    ]

    # Combine all configurations
    all_configs = configs_100 + configs_500 + configs_1000 + configs_10000

    # Insert into database
    for config_data in all_configs:
        config = VMConfiguration(**config_data)
        session.add(config)

    session.commit()
    print(f"Seeded VMConfiguration table with {len(all_configs)} records")
    session.close()


def migrate_vm_configurations(Session):
    """
    Migrate existing VM configurations from old architecture to new CONTROL/WORKER split.
    This function should be called when upgrading from the old architecture to the new one.

    Old architecture: RKEAPPS, RKEMIDDLEWARE (single types with varying node counts)
    New architecture: RKEAPPS_CONTROL (3) + RKEAPPS_WORKER (N), RKEMIDDLEWARE_CONTROL (3) + RKEMIDDLEWARE_WORKER (N)

    Load Balancers are fixed at 2 nodes in the new architecture.
    RKEDMZ is fixed at 3 nodes in the new architecture.
    """
    if Session is None:
        print("Session is not initialized")
        return

    session = Session()

    # Check if migration is needed (old VM types exist)
    old_configs = (
        session.query(VMConfiguration)
        .filter(VMConfiguration.vm_type.in_(["RKEAPPS", "RKEMIDDLEWARE"]))
        .all()
    )

    if not old_configs:
        print("No old VM configurations found. Migration not needed.")
        session.close()
        return

    print(f"Found {len(old_configs)} old VM configurations. Starting migration...")

    # Get all unique user counts from old configurations
    user_counts = sorted(set(config.user_count for config in old_configs))

    # For each user count, migrate the configuration
    for user_count in user_counts:
        print(f"\nMigrating configuration for {user_count} users...")

        # Get old configurations for this user count
        old_rkeapps = (
            session.query(VMConfiguration)
            .filter(
                VMConfiguration.vm_type == "RKEAPPS",
                VMConfiguration.user_count == user_count,
            )
            .first()
        )

        old_rkemiddleware = (
            session.query(VMConfiguration)
            .filter(
                VMConfiguration.vm_type == "RKEMIDDLEWARE",
                VMConfiguration.user_count == user_count,
            )
            .first()
        )

        # Migrate RKEAPPS
        if old_rkeapps and old_rkeapps.node_count > 3:
            control_count = 3
            worker_count = old_rkeapps.node_count - 3

            # Update RKEAPPS to RKEAPPS_CONTROL
            old_rkeapps.vm_type = "RKEAPPS_CONTROL"
            old_rkeapps.node_count = control_count
            print(f"  - Updated RKEAPPS -> RKEAPPS_CONTROL: {control_count} nodes")

            # Create or update RKEAPPS_WORKER
            existing_worker = (
                session.query(VMConfiguration)
                .filter(
                    VMConfiguration.vm_type == "RKEAPPS_WORKER",
                    VMConfiguration.user_count == user_count,
                )
                .first()
            )

            if existing_worker:
                existing_worker.node_count = worker_count
                print(f"  - Updated RKEAPPS_WORKER: {worker_count} nodes")
            else:
                worker_config = VMConfiguration(
                    user_count=user_count,
                    vm_type="RKEAPPS_WORKER",
                    node_count=worker_count,
                    cpu_per_node=old_rkeapps.cpu_per_node,
                    ram_per_node=old_rkeapps.ram_per_node,
                    os_disk_size=old_rkeapps.os_disk_size,
                    data_disk_size=old_rkeapps.data_disk_size,
                    roles="worker",
                )
                session.add(worker_config)
                print(f"  - Created RKEAPPS_WORKER: {worker_count} nodes")

        # Migrate RKEMIDDLEWARE
        if old_rkemiddleware and old_rkemiddleware.node_count > 3:
            control_count = 3
            worker_count = old_rkemiddleware.node_count - 3

            # Update RKEMIDDLEWARE to RKEMIDDLEWARE_CONTROL
            old_rkemiddleware.vm_type = "RKEMIDDLEWARE_CONTROL"
            old_rkemiddleware.node_count = control_count
            print(
                f"  - Updated RKEMIDDLEWARE -> RKEMIDDLEWARE_CONTROL: {control_count} nodes"
            )

            # Create or update RKEMIDDLEWARE_WORKER
            existing_worker = (
                session.query(VMConfiguration)
                .filter(
                    VMConfiguration.vm_type == "RKEMIDDLEWARE_WORKER",
                    VMConfiguration.user_count == user_count,
                )
                .first()
            )

            if existing_worker:
                existing_worker.node_count = worker_count
                print(f"  - Updated RKEMIDDLEWARE_WORKER: {worker_count} nodes")
            else:
                worker_config = VMConfiguration(
                    user_count=user_count,
                    vm_type="RKEMIDDLEWARE_WORKER",
                    node_count=worker_count,
                    cpu_per_node=old_rkemiddleware.cpu_per_node,
                    ram_per_node=old_rkemiddleware.ram_per_node,
                    os_disk_size=old_rkemiddleware.os_disk_size,
                    data_disk_size=old_rkemiddleware.data_disk_size,
                    roles="worker",
                )
                session.add(worker_config)
                print(f"  - Created RKEMIDDLEWARE_WORKER: {worker_count} nodes")

        # Fix Load Balancers to exactly 2 nodes
        for lb_type in ["LBLAN", "LBDMZ", "LBINTEGRATION"]:
            lb_config = (
                session.query(VMConfiguration)
                .filter(
                    VMConfiguration.vm_type == lb_type,
                    VMConfiguration.user_count == user_count,
                )
                .first()
            )

            if lb_config and lb_config.node_count != 2:
                old_count = lb_config.node_count
                lb_config.node_count = 2
                print(f"  - Fixed {lb_type}: {old_count} nodes -> 2 nodes")

        # Fix RKEDMZ to exactly 3 nodes
        rkedmz_config = (
            session.query(VMConfiguration)
            .filter(
                VMConfiguration.vm_type == "RKEDMZ",
                VMConfiguration.user_count == user_count,
            )
            .first()
        )

        if rkedmz_config and rkedmz_config.node_count != 3:
            old_count = rkedmz_config.node_count
            rkedmz_config.node_count = 3
            print(f"  - Fixed RKEDMZ: {old_count} nodes -> 3 nodes")

    # Commit all changes
    session.commit()
    print("\nMigration completed successfully!")
    session.close()


def scaffold_architecture(Session):
    """
    SIMPLIFIED VERSION FOR TESTING - MES-OMNI STYLE
    ================================================
    VMs are now created directly in initial_db.py on database initialization.
    This function just ensures VMs exist and returns - no dynamic generation.

    To modify VMs, edit initial_db.py and delete the database to reinitialize.
    """
    if Session is None:
        print("Session is not initialized")
        return

    session = Session()

    # Check if VMs already exist (created by initial_db.py)
    vm_count = session.query(VirtualMachine).count()
    if vm_count > 0:
        print(f"VMs already exist ({vm_count} VMs found), scaffold complete.")
        session.close()
        return

    # If no VMs exist, log a warning - user needs to configure initial_db.py
    print("WARNING: No VMs found in database!")
    print("Please configure your VMs in initial_db.py and reinitialize the database.")
    print("Delete sql_app.db and restart the application to recreate.")
    session.close()



def populate_db_fake_data(Session):
    """
    Populate database with test data.
    NOTE: Client-specific data has been removed/commented out.
    Configure your own values through the UI or API instead.
    """
    # Seed VM configurations first
    seed_vm_configurations(Session)

    # Example: Add VMware ESXi configuration
    # Replace with your own values
    # hypervisor = add_vmware_esxi_configuration(
    #     alias="vmware_esxi",
    #     login="your-username@your-domain.com",
    #     password="your-password",
    #     api_url="your-vcenter.your-domain.com",
    #     api_timeout=10,
    #     allow_unverified_ssl=True,
    #     datacenter_name="YourDatacenter",
    #     datacenter_id="dc1",
    #     target_name="YourCluster",
    #     target_id="cluster1",
    #     target_type="host",
    #     datastore_name="YourDatastore",
    #     datastore_id="datastore1",
    #     pool_ressource_name="YourResourcePool",
    #     pool_ressource_id="pool1",
    #     is_connected=True,
    #     Session=Session,
    # )
    
    # Example: Add databases
    # add_database(
    #     alias="prod",
    #     name="prod",
    #     type="informix",
    #     host="your-db-host.com",
    #     port="2034",
    #     login="base64-encoded-username",
    #     password="base64-encoded-password",
    #     Session=Session,
    # )
    
    # Example: Add LDAP servers
    # add_ldap(
    #     ldap_type="internal_users",
    #     ldap_url="your-ldap-ip",
    #     ldap_port=389,
    #     bind_dn="cn=admin,dc=example,dc=com",
    #     bind_credentials="password",
    #     user_dn="ou=users,dc=example,dc=com",
    #     user_ldap_attributes="",
    #     search_scope="subtree",
    #     Session=Session,
    # )
    
    # Example: Add SMS provider
    # add_sms_provider(
    #     url="http://your-sms-gateway.com/api/send",
    #     login="your-sms-username",
    #     password="your-sms-password",
    #     binder="your-binder",
    #     Session=Session,
    # )
    
    # Example: Configure security settings
    # update_security(
    #     use_proxy=False,
    #     porxy_host="",
    #     proxy_port=0,
    #     proxy_login="",
    #     proxy_password="",
    #     ssh_pulic_key="your-ssh-public-key",
    #     ssh_private_key="your-ssh-private-key",
    #     ssh_private_key_pwd="",
    #     base_domain="your-domain.com",
    #     env_prefix="",
    #     pem_certificate="your-certificate",
    #     Session=Session,
    # )
    
    # Example: Add SMTP server
    # add_smtp_server(
    #     host="smtp.your-domain.com",
    #     port=25,
    #     login="smtp-user",
    #     password="smtp-password",
    #     use_tls_ssl=False,
    #     mail_from="noreply@your-domain.com",
    #     Session=Session,
    # )

    # Example: Add zones (if hypervisor exists)
    # if hypervisor:
    #     zone_lan = add_zone(
    #         name="lan",
    #         sub_network="10.0.0.0",  # Replace with your subnet
    #         network_mask="24",
    #         dns="10.0.0.1",  # Replace with your DNS
    #         hypervisor_id=hypervisor.id,
    #         hypervisor_type="vmware",
    #         gateway="10.0.0.1",  # Replace with your gateway
    #         domain="your-domain.com",
    #         vlan_name="VLAN_100",
    #         ip_pool_start="10.0.0.100",
    #         ip_pool_end="10.0.0.200",
    #         Session=Session,
    #     )
    
    pass  # Function body is now just examples


def test_flows(Session):
    try:
        flows = get_flow_matrix(Session)
        security = get_security(Session)
        pkey_str = security.ssh_private_key
        passphrase = security.ssh_private_key_pwd
        for flow in flows:
            if re.match("ldap://", flow.destination):
                flow.destination = flow.destination.split("ldap://")[1]
            isPortOpen = test_is_Port_Open(
                source=flow.source,
                destination=flow.destination,
                port=flow.port,
                protocol=flow.protocol,
                pkey_str=pkey_str,
                passphrase=passphrase,
            )

            update_status_flow(flow.id, isPortOpen, Session)
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False


def test_service_port(destination, port):
    try:
        result = subprocess.run(
            ["nc", "-vz", "-w 5", destination, str(port)],
            capture_output=True,
            text=True,
            check=True,
        )
        result_stdout = result.stdout
        result_stderr = result.stderr
        print(f"result : {result_stdout}")
        print(f"error : {result_stderr}")
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False


def test_is_Port_Open(source, destination, port, protocol, pkey_str, passphrase=None):
    source_client = client.SSHClient()
    source_client.set_missing_host_key_policy(AutoAddPolicy())
    if pkey_str:
        try:
            pkey = RSAKey.from_private_key(StringIO(pkey_str), passphrase)

        except Exception:
            print(f"Error: {e}")
            return False

    try:
        source_client.connect(hostname=source, pkey=pkey, passphrase=passphrase)
        if protocol == "udp":
            command = "nc -vzu"
        else:
            command = "nc -vz"

        full_command = f"{command} {destination} {port} 2>&1;"
        stdin, stdout, stderr = source_client.exec_command(full_command)
        output = stdout.read().decode()
        exit_status = int(stdout.channel.recv_exit_status())
        source_client.close()

        if exit_status == 0:
            return True
        else:
            return False
    except Exception as e:
        print(f"Error: {e}")
        return False


def scaffold_test_architecture(Session):
    """
    Scaffold minimal 3-VM test architecture for AWS testing.
    Creates VMs only if they don't already exist.

    VM Configuration (modify IPs here for your AWS VMs):
    - VM1: infra-vm (10.0.1.11) - Docker Registry + Gogs
    - VM2: rke-master (10.0.1.12) - RKE2 Master
    - VM3: rke-worker (10.0.1.13) - RKE2 Worker
    """
    if Session is None:
        logger.error("Session is not initialized")
        return

    session = Session()

    # Check if VMs already exist
    if session.query(VirtualMachine).count() != 0:
        logger.info("VMs already exist, skipping scaffold")
        session.close()
        return

    logger.info("Scaffolding minimal 3-VM test architecture...")

    # ============================================================================
    # MINIMAL TEST CONFIGURATION - MODIFY THESE VALUES FOR YOUR AWS VMS
    # ============================================================================
    VM_CONFIG = {
        "base_domain": "test.local",
        "env_prefix": "test",
        "network": {
            "subnet": "10.0.1.0",
            "mask": 24,
            "gateway": "10.0.1.1",
            "dns": "8.8.8.8,8.8.4.4"
        },
        "vms": [
            {
                "hostname": "infra-vm",
                "ip": "10.0.1.11",  # ← CHANGE THIS to your AWS VM2 private IP
                "group": "gitops",  # Will deploy Docker Registry + Gogs
                "roles": "docker-registry,gogs",
                "cpu": 2,
                "ram": 4096,
                "disk": 30
            },
            {
                "hostname": "rke-master",
                "ip": "10.0.1.12",  # ← CHANGE THIS to your AWS VM3 private IP
                "group": "RKEAPPS",  # Will deploy RKE2 master
                "roles": "rke2-server",
                "cpu": 2,
                "ram": 4096,
                "disk": 30
            },
            {
                "hostname": "rke-worker",
                "ip": "10.0.1.13",  # ← CHANGE THIS to your AWS VM4 private IP
                "group": "RKEAPPS_WORKER",  # Will deploy RKE2 worker
                "roles": "rke2-agent",
                "cpu": 2,
                "ram": 4096,
                "disk": 30
            }
        ]
    }
    # ============================================================================

    session.close()

    # Update security settings
    security = get_security(Session)
    if security:
        update_security(
            use_proxy=security.use_proxy,
            porxy_host=security.porxy_host,
            proxy_port=security.proxy_port,
            proxy_login=security.proxy_login,
            proxy_password=security.proxy_password,
            ssh_pulic_key=security.ssh_pulic_key,
            ssh_private_key=security.ssh_private_key,
            ssh_private_key_pwd=security.ssh_private_key_pwd,
            base_domain=VM_CONFIG["base_domain"],
            env_prefix=VM_CONFIG["env_prefix"],
            pem_certificate=security.pem_certificate,
            Session=Session
        )

    # Get or create zone
    zones = get_zones(Session)
    if zones:
        zone_id = zones[0].id
    else:
        zone = add_zone(
            name="TEST_ZONE",
            sub_network=VM_CONFIG["network"]["subnet"],
            network_mask=VM_CONFIG["network"]["mask"],
            dns=VM_CONFIG["network"]["dns"],
            hypervisor_id=None,
            hypervisor_type="vmware",  # Placeholder
            gateway=VM_CONFIG["network"]["gateway"],
            domain=VM_CONFIG["base_domain"],
            vlan_name="default",
            Session=Session
        )
        zone_id = zone.id

    # Create 3 VMs
    for vm_config in VM_CONFIG["vms"]:
        vm = add_virtual_machine(
            hostname=vm_config["hostname"],
            ip=vm_config["ip"],
            zone_id=zone_id,
            group=vm_config["group"],
            roles=vm_config["roles"],
            nb_cpu=vm_config["cpu"],
            ram=vm_config["ram"],
            os_disk_size=vm_config["disk"],
            data_disk_size=0,
            Session=Session
        )
        logger.info(f"✅ Created VM: {vm_config['hostname']} ({vm_config['ip']}) - {vm_config['group']}")

    logger.info("✅ Minimal 3-VM test architecture scaffolded successfully!")


if __name__ == "__main__":
    db_path = "./tests/harmonisation_runner.db"
    if os.path.exists(db_path):
        os.remove(db_path)
    # _, Session = get_session(db_path)
    # populate_db_fake_data(Session)
    print("Initialize database ./tests/harmonisation_runner.db with fake data done...")
