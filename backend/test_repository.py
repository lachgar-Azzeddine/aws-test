import unittest
import os
from repository import (
    initialize_database,
    query_products,
    get_products_to_install,
    prepare_install_products,
    getConfiguration,
    update_number_concurent_users,
    add_vmware_esxi_configuration,
    # update_vmware_esxi_configuration,
    # delete_vmware_esxi_configuration,
    # add_nutanix_ahv_configuration,
    # update_nutanix_ahv_configuration,
    # delete_nutanix_ahv_configuration,
    get_hypervisor_list,
    get_hypervisor,
    # delete_hypervisor,
    get_databases,
    add_database,
    # update_database,
    # delete_database,
    get_monitoring_config,
    update_monitoring_config,
    get_ldaps,
    add_ldap,
    # update_ldap,
    # delete_ldap,
    get_security,
    update_security,
    get_zones,
    get_zone_by_id,
    add_zone,
    # get_sms_providers,
    # add_sms_provider,
    # update_sms_provider,
    # delete_sms_provider,
    # get_smtp_servers,
    # add_smtp_server,
    # delete_smtp_server,
    # get_payment_providers,
    # add_payment_provider,
    # update_payment_provider,
    # delete_payment_provider,
    # get_publishing_providers,
    # add_publishing_provider,
    # update_publishing_provider,
    # delete_publishing_provider,
    # get_services,
    # get_service,
    get_virtual_machines,
    add_virtual_machine,
    # update_virtual_machine,
    update_status_vm,
    get_vms_to_create,
    get_vms_by_group,
    # get_all_dns,
    # add_dns,
    # get_flow_matrix,
    # add_flow_matrix,
    # update_status_flow,
    # get_palybooks_run,
    # add_palybook_run,
    # update_playbook_run,
    # get_task_logs,
    # add_task_logs,
)


class TestRepositoryMethods(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.db_path = "./tests/test_harmonisation_runner.db"
        # test if the file exists and delete it if it does
        if os.path.exists(cls.db_path):
            os.remove(cls.db_path)
        _, cls.Session = initialize_database(cls.db_path)

    @classmethod
    def tearDownClass(cls):
        if os.path.exists(cls.db_path):
            os.remove(cls.db_path)

    def test_initialize_database(self):
        self.assertTrue(os.path.exists(self.db_path))

    def test_query_products(self):
        products = query_products(self.Session)
        self.assertEqual(len(products), 3)

    def test_get_products_to_install(self):
        products = get_products_to_install(self.Session)
        self.assertEqual(len(products), 0)

    def test_prepare_install_products(self):
        prepare_install_products([1, 2], self.Session)
        products = get_products_to_install(self.Session)
        self.assertEqual(len(products), 2)

    def test_getConfiguration(self):
        config = getConfiguration(self.Session)
        self.assertIsNotNone(config)
        if config:
            self.assertTrue(hasattr(config, "number_concurrent_users"))
            self.assertEqual(config.number_concurrent_users, 100)

    def test_update_number_concurent_users(self):
        update_number_concurent_users(100, self.Session)
        config = getConfiguration(self.Session)
        if config:
            self.assertTrue(hasattr(config, "number_concurrent_users"))
            self.assertEqual(config.number_concurrent_users, 100)

    # Add more test methods for other functions...
    def test_add_vmware_esxi_configuration(self):
        add_vmware_esxi_configuration(
            alias="vmware_esxi",
            login="mrabbah@gmail.com",
            password="password",
            api_url="10.10.2.43",
            api_timeout=10,
            allow_unverified_ssl=True,
            datacenter_name="dc1",
            datacenter_id="dc1",
            cluster_name="cluster1",
            cluster_id="cluster1",
            datastore_name="datastore1",
            datastore_id="dtatstore1",
            pool_ressource_name="pool1",
            pool_ressource_id="pool1",
            is_connected=True,
            Session=self.Session,
        )
        hypervisors = get_hypervisor_list(self.Session)
        self.assertEqual(len(hypervisors), 1)

    def test_get_hypervisor(self):
        hypervisor = get_hypervisor(1, "vmware", self.Session)
        self.assertIsNotNone(hypervisor)
        if hypervisor:
            self.assertEqual(hypervisor.alias, "vmware_esxi")

    def test_add_database(self):
        add_database(
            name="prod1",
            type="informix",
            host="10.10.20.49",
            port="5432",
            login="prod1login",
            password="prod1password",
            Session=self.Session,
        )
        add_database(
            name="sig",
            type="informix",
            host="10.10.20.59",
            port="5432",
            login="siglogin",
            password="sigpwd",
            Session=self.Session,
        )
        add_database(
            name="flowabledb",
            type="postgresql",
            host="10.10.20.89",
            port="5432",
            login="flowablelogin",
            password="flowabledbpwd",
            Session=self.Session,
        )
        databases = get_databases(self.Session)
        self.assertEqual(len(databases), 3)

    def test_monitoring_config(self):
        monitoring_config = get_monitoring_config(self.Session)
        self.assertIsNotNone(monitoring_config)
        if monitoring_config:
            self.assertTrue(
                hasattr(monitoring_config, "deploy_embeded_monitoring_stack")
            )
            self.assertEqual(monitoring_config.deploy_embeded_monitoring_stack, True)

        update_monitoring_config(
            deploy_embeded_monitoring_stack=False,
            logs_retention_period=30,
            logs_retention_disk_space=100,
            metrics_retention_period=30,
            metrics_retnetion_disk_space=100,
            Session=self.Session,
        )
        monitoring_config = get_monitoring_config(self.Session)

        if monitoring_config:
            self.assertTrue(
                hasattr(monitoring_config, "deploy_embeded_monitoring_stack")
            )
            self.assertEqual(monitoring_config.deploy_embeded_monitoring_stack, False)

    def test_get_ldaps(self):
        ldaps = get_ldaps(self.Session)
        self.assertEqual(len(ldaps), 0)

        add_ldap(
            alias="internal_users",
            ldap_url="10.10.20.200",
            ldap_port="869",
            bind_dn="cn=admin",
            bind_credentials="password",
            user_dn="ou=users,dc=example,dc=com",
            user_ldap_attributes="",
            search_scope="serach",
            Session=self.Session,
        )
        add_ldap(
            alias="external_users",
            ldap_url="10.10.20.230",
            ldap_port="869",
            bind_dn="cn=admin",
            bind_credentials="password",
            user_dn="ou=users,dc=example,dc=com",
            user_ldap_attributes="",
            search_scope="serach",
            Session=self.Session,
        )
        ldaps = get_ldaps(self.Session)
        self.assertEqual(len(ldaps), 2)

    def test_security(self):
        security = get_security(self.Session)
        self.assertIsNotNone(security)
        security_updated = update_security(
            use_proxy=True,
            porxy_host="http://192.169.0.55",
            proxy_port=8080,
            alias="",
            proxy_login="",
            proxy_password="",
            ssh_pulic_key="ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQDQ3jX3f5QnH2g4XjxV5v",
            ssh_private_key="ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQDQ3jX3f5QnH2g4XjxV5v",
            base_domain="dev.example.com",
            pem_certificate="pem_certificate",
            Session=self.Session,
        )

        if security_updated:
            self.assertTrue(hasattr(security_updated, "use_proxy"))
            self.assertEqual(security_updated.use_proxy, True)

    def test_zones_management(self):
        hypervisor = get_hypervisor(1, "vmware", self.Session)
        if hypervisor:
            zone_lan = add_zone(
                name="lan",
                sub_network="10.10.0.0",
                network_mask="255.255.0.0",
                dns="8.8.8.8",
                hypervisor_id=hypervisor.id,
                hypervisor_type="vmware",
                gateway="10.10.0.1",
                domain="example.com",
                Session=self.Session,
            )
            self.assertIsNotNone(zone_lan)
            zone_dmz = add_zone(
                name="dmz",
                sub_network="10.20.0.0",
                network_mask="255.255.0.0",
                dns="8.8.8.8",
                hypervisor_id=hypervisor.id,
                hypervisor_type="vmware",
                gateway="10.20.0.1",
                domain="example.com",
                Session=self.Session,
            )
            self.assertIsNotNone(zone_dmz)
            zones = get_zones(self.Session)
            self.assertEqual(len(zones), 2)
            if zone_lan:
                zone_lan_bis = get_zone_by_id(zone_lan.id, self.Session)
                self.assertIsNotNone(zone_lan_bis)
                if zone_lan_bis:
                    self.assertEqual(zone_lan_bis.name, "lan")

    def test_virtual_machines(self):
        zone_lan = get_zone_by_id(1, self.Session)
        if zone_lan:
            add_virtual_machine(
                hostname="master1",
                roles="master",
                group="rke",
                ip="10.10.0.10",
                nb_cpu=4,
                ram=16,
                os_disk_size=80,
                data_disk_size=0,
                zone_id=zone_lan.id,
                Session=self.Session,
            )
            add_virtual_machine(
                hostname="master2",
                roles="master",
                group="rke",
                ip="10.10.0.11",
                nb_cpu=4,
                ram=16,
                os_disk_size=80,
                data_disk_size=0,
                zone_id=zone_lan.id,
                Session=self.Session,
            )
            add_virtual_machine(
                hostname="master3",
                roles="master",
                group="rke",
                ip="10.10.0.12",
                nb_cpu=4,
                ram=16,
                os_disk_size=80,
                data_disk_size=0,
                zone_id=zone_lan.id,
                Session=self.Session,
            )
            vms = get_virtual_machines(self.Session)
            self.assertEqual(len(vms), 3, self.Session)

            update_status_vm(1, "running", self.Session)
            update_status_vm(2, "running", self.Session)

            vms_to_create = get_vms_to_create(self.Session)
            self.assertEqual(len(vms_to_create), 1)

            vms = get_vms_by_group("rke", self.Session)
            self.assertEqual(len(vms), 3)


if __name__ == "__main__":
    unittest.main()
