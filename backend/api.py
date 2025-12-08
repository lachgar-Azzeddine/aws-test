import logging
# from fastapi.concurrency import run_in_threadpool
from typing import Annotated,List  # , Optional
import uvicorn
from fastapi import BackgroundTasks, FastAPI, HTTPException,Depends
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from install import (
    install_all_roles,
)
from models import (
    # Client-specific service models removed:
    # AlfrescoModel, AuthModel, GCBOModel, GMAOModel,
    # FacebookModel, FcmModel, FirebaseDbModel, GoogleModel,
    # PaymentProviderModel, PublishingProviderModel, SignatureServiceModel, ArcgisModel
    AnsibleRoleModel,
    ConfigurationModel,
    DatabaseModel,
    DnsModel,
    FlowMatrixModel,
    GlobalRecap,
    HypervisorModel,
    LdapModel,
    LdapPartialModel,
    MonitoringModel,
    NutanixAHVModel,
    # ProductModel removed - no longer using product-based system
    SecurityModel,
    SecurityUpdateModel,
    SMSProviderModel,
    SMTPServerModel,
    ServiceModel,
    TaskLogModel,
    VaultCredentialsModel,
    VirtualMachineModel,
    VMwareEsxiModel,
    ZoneModel,
    certificatModel,
    sshKeyModel,
)
from repository import (
    # Client-specific service functions removed:
    # add_arcgis_server, add_facebook, add_fcm, add_firebase_db, add_google,
    # add_payment_provider, add_publishing_provider, add_server, add_signature,
    # delete_arcgis_server, delete_payment_provider, delete_publishing_provider, delete_server,
    # get_arcgis_servers, get_payment_providers, get_publishing_providers, get_server,
    # update_arcgis_provider, update_facebook, update_fcm, update_firebase_db,
    # update_google, update_payment_provider, update_publishing_provider,
    # update_server, update_signature
    add_database,
    add_flow_matrix,
    add_zone,
    # populate_db_fake_data,
    add_ldap,
    add_nutanix_ahv_configuration,
    add_sms_provider,
    add_smtp_server,
    add_vmware_esxi_configuration,
    delete_all_ansible_roles,
    delete_database,
    delete_hypervisor,
    delete_ldap,
    delete_nutanix_ahv_configuration,
    delete_sms_provider,
    delete_smtp_server,
    delete_vmware_esxi_configuration,
    get_all_dns,
    get_ansible_roles,
    get_databases,
    get_flow_matrix,
    get_hypervisor,
    get_hypervisor_list,
    get_ldaps,
    get_monitoring_config,
    # get_products_to_install removed - no longer using product-based system
    get_security,
    get_service,
    get_services,
    get_sms_providers,
    get_smtp_servers,
    get_task_logs,
    get_vault_creds,
    get_virtual_machines,
    get_vms_by_group,
    get_zone_by_id,
    get_zones,
    getConfiguration,
    get_session,
    # prepare_install_products removed - no longer using product-based system
    # set_installed_products removed - no longer using product-based system
    # query_products removed - no longer using product-based system
    scaffold_architecture,
    test_database,
    test_flows,
    test_key_pair_match,
    test_ldap,
    test_services,
    test_ssl_with_domain,
    test_vmware_esxi_configuration,
    update_current_step,
    update_database,
    update_ldap,
    update_monitoring_config,
    update_number_concurent_users,
    update_nutanix_ahv_configuration,
    update_security,
    update_sms_provider,
    update_smtp_provider,
    update_virtual_machine,
    update_vmware_esxi_configuration,
    update_zone,
)



logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Get session
_, Session = get_session()


# populate_db_fake_data(Session)
app = FastAPI()

origins = [
    "*",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/get_global_recap", response_model=List[GlobalRecap])
def get_global_recap():
    return [
        GlobalRecap(zone="LAN Apps", total_cpu=144, total_memory=200, total_disk=1000),
        GlobalRecap(zone="LAN Infra", total_cpu=144, total_memory=200, total_disk=1000),
        GlobalRecap(zone="DMZ", total_cpu=144, total_memory=200, total_disk=1000),
    ]

@app.post("/start", response_model=bool)
async def start_install(background_tasks: BackgroundTasks):
    delete_all_ansible_roles(Session)
    background_tasks.add_task(install_all_roles, Session)
    # install_all_roles(Session)
    return True


# SMS Providers
@app.get("/sms-providers", response_model=List[SMSProviderModel])
def read_sms_providers():
    return get_sms_providers(Session)


# Security
@app.get("/security", response_model=SecurityModel)
def read_security_config():
    """
    Retrieve the security configuration.
    """
    # Call the get_security function from the repository
    security_config = get_security(Session)

    # Check if the security configuration exists
    if not security_config:
        raise HTTPException(status_code=404, detail="Security configuration not found")

    # Return the security configuration
    return SecurityModel.model_validate(security_config)


@app.put("/security", response_model=SecurityModel)
def update_security_config(security_data: SecurityUpdateModel):
    """
    Update the security configuration.
    """
    # Call the update_security function with the new data
    updated_security = update_security(
        use_proxy=security_data.use_proxy,
        porxy_host=security_data.porxy_host,
        proxy_port=security_data.proxy_port,
        proxy_login=security_data.proxy_login,
        proxy_password=security_data.proxy_password,
        ssh_pulic_key=security_data.ssh_pulic_key,
        ssh_private_key=security_data.ssh_private_key,
        ssh_private_key_pwd=security_data.ssh_private_key_pwd,
        base_domain=security_data.base_domain,
        env_prefix=security_data.env_prefix,
        pem_certificate=security_data.pem_certificate,
        Session=Session,
    )

    # Check if the security configuration exists
    if not updated_security:
        raise HTTPException(status_code=404, detail="Security configuration not found")

    # Return the updated security configuration
    return SecurityModel.model_validate(updated_security)


@app.post("/tester-certificat", response_model=bool)
def test_crt(certificat: certificatModel):
    cert_dict = certificat.dict()
    return test_ssl_with_domain(**cert_dict)


# Hypervisors
@app.get("/hypervisors", response_model=List[HypervisorModel])
def get_hypervisors():
    return get_hypervisor_list(Session)


@app.get("/hypervisor/{id}")
def read_hypervisor(id: int, type: str):
    """
    Retrieve a hypervisor by ID based on type ('vmware' or 'nutanix').
    """
    # Call the get_hypervisor function from your repository
    hypervisor = get_hypervisor(id, type, Session)

    # Check for existence and return result
    if not hypervisor:
        raise HTTPException(status_code=404, detail="Hypervisor not found")

    # If type is "nutanix", change the response model dynamically
    if type == "nutanix":
        return NutanixAHVModel.model_validate(hypervisor)

    # Default response model for VMware
    return VMwareEsxiModel.model_validate(hypervisor)


@app.delete("/hypervisor/{id}")
def remove_hypervisor(id: int, type: str):
    """
    Delete a hypervisor by ID based on type ('vmware' or 'nutanix').
    """
    delete_hypervisor(id, type, Session)
    return {
        "message": f"{type.capitalize()} hypervisor with ID {id} deleted successfully"
    }


# Product endpoints removed - no longer using product-based system
# /products, /products/to-install, /products/prepare-install, /products/set-installed deleted


# Configuration
@app.get("/configuration", response_model=ConfigurationModel)
def read_configuration():
    config = getConfiguration(Session)
    if not config:
        raise HTTPException(status_code=404, detail="Configuration not found")
    return config


@app.put("/configuration/concurrent-users")
def update_concurrent_users(
    number: int,
):
    config = update_number_concurent_users(number, Session)
    if not config:
        raise HTTPException(status_code=404, detail="Configuration not found")
    return {"message": "Concurrent users updated"}


@app.put("/configuration/current_step")
def update_step(
    number: int,
):
    step = update_current_step(number, Session)
    if not step:
        raise HTTPException(status_code=404, detail="Configuration not found")
    return {"message": "current configuration step updated"}


@app.get("/configuration/current_step")
def get_step():
    config = getConfiguration(Session)
    if not config:
        raise HTTPException(status_code=404, detail="Configuration not found")
    return {"current_step": config.current_step}


# VMware
@app.post("/vmware", response_model=VMwareEsxiModel)
def add_vmware(vmware: VMwareEsxiModel):
    # Exclude the 'id' field from the data
    vmware_dict = vmware.dict(
        exclude={"id", "type"}
    )  # Exclude 'id' as it's auto-generated
    return add_vmware_esxi_configuration(**vmware_dict, Session=Session)


@app.post("/vmware-test")
def test_vmware(vmware: VMwareEsxiModel):
    vmware_dict = vmware.dict(
        include={
            "login",
            "password",
            "api_url",
            "datacenter_name",
            "target_name",
            "target_type",
            "datastore_name",
            "pool_ressource_name",
        }
    )
    return test_vmware_esxi_configuration(**vmware_dict)


@app.post(
    "/ssh-keys-test",
)
def test_ssh_keys(ssh_pair: sshKeyModel):
    ssh_dict = ssh_pair.dict()
    return test_key_pair_match(**ssh_dict)


@app.put("/vmware/{id}", response_model=VMwareEsxiModel)
def update_vmware(id: int, vmware: VMwareEsxiModel):
    return update_vmware_esxi_configuration(
        id=id,
        **vmware.model_dump(
            exclude={"id", "is_connected", "type"}
        ), # Exclude 'id' and 'is_connected' as they're auto-generated
          Session=Session  
    )


@app.delete("/vmware/{id}")
def delete_vmware(
    id: int,
):
    delete_vmware_esxi_configuration(id, Session)
    return {"message": "VMware Esxi configuration deleted"}


# Nutanix
@app.post("/nutanix", response_model=NutanixAHVModel)
def add_nutanix(nutanix: NutanixAHVModel):
    print(
        "Received POST request for /nutanix"
    )  # Confirm that the request is reaching the endpoint
    print(nutanix.dict())  # Print the incoming data for debugging
    nutanix_dict = nutanix.dict(
        exclude={"id", "type"}
    )  # Exclude 'id' as it's auto-generated
    return add_nutanix_ahv_configuration(**nutanix_dict, Session=Session)


@app.put("/nutanix/{id}", response_model=NutanixAHVModel)
def update_nutanix(
    id: int,
    nutanix: NutanixAHVModel,
):
    return update_nutanix_ahv_configuration(
        id,
        **nutanix.model_dump(exclude={"id", "is_connected", "type"}),
        Session=Session,
    )


@app.delete("/nutanix/{id}")
def delete_nutanix(
    id: int,
):
    delete_nutanix_ahv_configuration(id, Session)
    return {"message": "Nutanix AHV configuration deleted"}


# Databases
@app.get("/databases", response_model=List[DatabaseModel])
def read_databases():
    return get_databases(Session)


@app.post("/database", response_model=DatabaseModel)
def add_database_item(
    database: DatabaseModel,
):
    database_dict = database.dict(exclude={"id", "is_connected"})
    return add_database(**database_dict, Session=Session)


@app.put("/database/{id}", response_model=DatabaseModel)
def update_database_item(
    id: int,
    database: DatabaseModel,
):
    return update_database(
        id, **database.model_dump(exclude={"id", "is_connected"}), Session=Session
    )


@app.delete("/database/{id}")
def delete_database_item(
    id: int,
):
    delete_database(id, Session)
    return {"message": "Database configuration deleted"}

@app.post("/database-test")
def test_database_item(database: DatabaseModel):
    print("testing database")
    return test_database(
        **database.model_dump(
            exclude={"id", "is_connected","alias"}
        )
    )

@app.post("/service-test", response_model=bool)
def test_service(service: ServiceModel):
    service_dict = service.dict()
    return test_services(**service_dict, Session=Session)

# Monitoring
@app.get("/monitoring", response_model=MonitoringModel)
def read_monitoring_config():
    return get_monitoring_config(Session)


@app.put("/monitoring", response_model=MonitoringModel)
def updt_monitoring_config(
    monitoring: MonitoringModel,
):
    return update_monitoring_config(
        **monitoring.model_dump(exclude={"id"}), Session=Session
    )


# LDAPS
@app.get("/ldaps", response_model=List[LdapModel])
def read_ldaps():
    return get_ldaps(Session)


@app.post("/ldap", response_model=LdapModel)
def add_ldap_item(
    ldap: LdapModel,
):
    ldap_dict = ldap.dict(exclude={"id"})
    return add_ldap(**ldap_dict, Session=Session)

@app.post("/ldap-test")
def test_ldap_item(
    ldap: LdapPartialModel,
):
    return test_ldap(**ldap.model_dump())


@app.put("/ldap/{id}", response_model=LdapModel)
def update_ldap_item(
    id: int,
    ldap: LdapModel,
):
    return update_ldap(id, **ldap.model_dump(exclude={"id"}), Session=Session)


@app.delete("/ldap/{id}")
def delete_ldap_item(
    id: int,
):
    delete_ldap(id, Session)
    return {"message": "LDAP configuration deleted"}


# Zones
@app.get("/zones", response_model=List[ZoneModel])
def read_zones():
    return get_zones(Session)


# @app.post("/zone", response_model=ZoneModel)
# def add_zone_item(
#     zone: ZoneModel,
#     hypervisor_id: int,
# ):
#
#     return add_zone(**zone.model_dump(exclude={"id"}), hypervisor_id=hypervisor_id ,Session=Session)


@app.put("/zone/{id}/{hypervisor_id}", response_model=ZoneModel)
def update_zone_item(
    id: int,
    hypervisor_id: int,
    zone: ZoneModel,
):
    return update_zone(
        id,
        **zone.model_dump(exclude={"id"}),
        hypervisor_id=hypervisor_id,
        Session=Session,
    )


@app.get("/zones/{id}", response_model=ZoneModel)
def read_zone_by_id(id: int):
    """
    Retrieve a zone by ID.
    """
    # Call the get_zone_by_id function from the repository
    zone = get_zone_by_id(id, Session)

    # Check if the zone exists
    if not zone:
        raise HTTPException(status_code=404, detail="Zone not found")

    # Return the zone data
    return ZoneModel.model_validate(zone)


# Virtual Machines
@app.get("/virtual-machines", response_model=List[VirtualMachineModel])
def read_virtual_machines():
    
    scaffold_architecture(Session)
    return get_virtual_machines(Session)


@app.put("/virtual-machine/{id}", response_model=VirtualMachineModel)
def update_virtual_machine_item(
    id: int,
    vm: VirtualMachineModel,
):
    return update_virtual_machine(id, **vm.model_dump(exclude={"id"}),Session=Session)


# Playbooks and Task Logs
@app.get("/ansible_roles", response_model=List[AnsibleRoleModel])
def retreive_ansible_roles():
    return get_ansible_roles(Session)


@app.get("/task-logs/{runner_ident}", response_model=List[TaskLogModel])
def obtain_task_logs(
    runner_ident: str,
):
    return get_task_logs(runner_ident, Session)


# DNS and Flow Matrix
@app.get("/dns", response_model=List[DnsModel])
def read_dns():
    return get_all_dns(Session)


@app.post("/add-flow", response_model=FlowMatrixModel)
def create_flow(flow: FlowMatrixModel):
    return add_flow_matrix(
        **flow.model_dump(exclude={"id", "is_open"}), Session=Session
    )


@app.get("/flow-matrix", response_model=List[FlowMatrixModel])
def read_flow_matrix():
    return get_flow_matrix(Session)


# SMS Provider Endpoints
@app.post("/sms-providers", response_model=SMSProviderModel)
def create_sms_provider(provider: SMSProviderModel):
    return add_sms_provider(**provider.model_dump(exclude={"id"}), Session=Session)


@app.put("/sms-providers/{id}", response_model=SMSProviderModel)
def modify_sms_provider(id: int, provider: SMSProviderModel):
    updated_provider = update_sms_provider(
        id, **provider.model_dump(exclude={"id"}), Session=Session
    )
    if not updated_provider:
        raise HTTPException(status_code=404, detail="SMS Provider not found")
    return updated_provider


@app.delete("/sms-providers/{id}")
def remove_sms_provider(id: int):
    result = delete_sms_provider(id, Session)
    if result is None:
        raise HTTPException(status_code=404, detail="SMS Provider not found")
    return {"message": "SMS Provider deleted successfully"}


# SMTP Server Endpoints
@app.get("/smtp-servers", response_model=List[SMTPServerModel])
def read_smtp_servers():
    return get_smtp_servers(Session)


@app.post("/smtp-servers", response_model=SMTPServerModel)
def create_smtp_server(server: SMTPServerModel):
    return add_smtp_server(**server.model_dump(exclude={"id"}), Session=Session)


@app.put("/smtp-servers/{id}", response_model=SMTPServerModel)
def modify_smtp_provider(id: int, provider: SMTPServerModel):
    updated_provider = update_smtp_provider(
        id, **provider.model_dump(exclude={"id"}), Session=Session
    )
    if not updated_provider:
        raise HTTPException(status_code=404, detail="SMTP Provider not found")
    return updated_provider


@app.delete("/smtp-servers/{id}")
def remove_smtp_server(id: int):
    result = delete_smtp_server(id, Session)
    if result is None:
        raise HTTPException(status_code=404, detail="SMTP Server not found")
    return {"message": "SMTP Server deleted successfully"}


# Client-specific service endpoints removed (43 endpoints total):
# - ArcGIS Server: GET, POST, PUT, DELETE /arcgis-servers
# - Alfresco: GET, POST, PUT, DELETE /alfresco
# - Auth Server: GET, POST, PUT, DELETE /auth
# - GCBO: GET, POST, PUT, DELETE /gcbo
# - GMAO: GET, POST, PUT, DELETE /gmao
# - Firebase: GET, POST, PUT, DELETE /firebase
# - FCM: GET, POST, PUT, DELETE /fcm
# - Google: GET, POST, PUT, DELETE /google
# - Facebook: GET, POST, PUT, DELETE /facebook
# - Signature: GET, POST, PUT, DELETE /signature
# - Payment Provider: GET, POST, PUT, DELETE /payment-providers
# - Publishing Provider: GET, POST, PUT, DELETE /publishing-providers


# Services Endpoints
@app.get("/services", response_model=List[dict])
def read_services():
    return get_services(Session)


@app.get("/services/{id}")
def read_service(id: int, type: str):
    service = get_service(id, type, Session)
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")
    return service


@app.get("/virtual-machines/group/{group}", response_model=List[VirtualMachineModel])
def read_vms_by_group(group: str):
    """
    Retrieve all virtual machines by their group.
    """
    # Call the get_vms_by_group function from the repository
    virtual_machines = get_vms_by_group(group, Session)

    # Return the list of virtual machines in the specified group
    return virtual_machines


@app.get("/test-flows", response_model=bool)
def testing_flows():
    return test_flows(Session)

@app.get("/vault-creds", response_model=List[VaultCredentialsModel])
def read_vault_credentials():
    vault_creds = get_vault_creds(Session)
    return vault_creds

@app.post("/init-data", response_model=bool)
def initialize_data():
    return True


if __name__ == "__main__":
    uvicorn.run("api:app", host="0.0.0.0", port=8008, reload=True)
