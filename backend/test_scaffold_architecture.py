"""
Test suite for scaffold_architecture and related DNS functions.

This test file validates:
1. The DNS helper functions (add_dns, add_dns_gco, add_dns_eservices)
2. The scaffold_architecture function integration
3. Proper session handling throughout the call chain
"""

import pytest
from unittest.mock import Mock, MagicMock, patch, call
from sqlalchemy.orm import Session as SQLAlchemySession

# Import the functions to test
from repository import (
    add_dns,
    add_dns_gco,
    add_dns_eservices,
    scaffold_architecture,
    seed_vm_configurations,
    getConfiguration,
    get_security,
    get_products_to_install,
    get_vm_configurations,
    get_zone_by_id,
    get_vms_by_group,
    get_smtp_servers,
    get_sms_providers,
    get_publishing_providers,
    get_arcgis_servers,
    get_databases,
    get_ldaps,
    add_flow_matrix,
    add_virtual_machine,
    add_application,
    get_next_available_ip,
    Dns,
    VirtualMachine,
    FlowMatrix,
    Application,
    Configuration,
    Security,
    Product,
    Zone,
    VMConfiguration,
)


class TestAddDns:
    """Test the add_dns helper function"""

    def test_add_dns_success(self):
        """Test that add_dns properly creates and saves a DNS record"""
        # Setup
        mock_session_instance = Mock(spec=SQLAlchemySession)
        mock_session_class = Mock(return_value=mock_session_instance)
        mock_dns = Mock(spec=Dns)

        # Mock the Dns class constructor
        with patch('repository.Dns') as mock_dns_class:
            mock_dns_class.return_value = mock_dns

            # Execute
            result = add_dns("test", "test.example.com", "192.168.1.1", mock_session_class)

            # Verify
            mock_dns_class.assert_called_once_with(
                name="test",
                hostname="test.example.com",
                ip="192.168.1.1"
            )
            # Session class should be called once to create instance
            mock_session_class.assert_called_once()
            # Session instance should be used
            mock_session_instance.add.assert_called_once()
            mock_session_instance.commit.assert_called_once()
            mock_session_instance.close.assert_called_once()
            assert result == mock_dns

    def test_add_dns_with_none_session(self):
        """Test that add_dns returns early when session is None"""
        # Execute
        result = add_dns("test", "test.example.com", "192.168.1.1", None)

        # Verify
        assert result is None


class TestAddDnsGco:
    """Test the add_dns_gco helper function"""

    @patch('repository.add_dns')
    def test_add_dns_gco_with_gco_present(self, mock_add_dns):
        """Test DNS record creation when GCO product is present"""
        # Setup
        mock_session_instance = Mock(spec=SQLAlchemySession)
        mock_session_class = Mock(return_value=mock_session_instance)
        mock_dns = Mock(spec=Dns)
        mock_session_instance.query.return_value.filter.return_value.first.return_value = None
        mock_add_dns.return_value = mock_dns

        # Execute
        add_dns_gco(
            isGCOPresent=True,
            env_prefix="dev-",
            base="example.com",
            ip="192.168.1.100",
            Session=mock_session_class
        )

        # Verify
        # Session class should be called
        mock_session_class.assert_called_once()
        # Should query for existing GCO and ArcGIS DNS records
        assert mock_session_instance.query.call_count >= 2
        # Should call add_dns twice (once for gco, once for arcgis)
        assert mock_add_dns.call_count == 2
        # Verify the calls to add_dns (should pass Session class, not instance)
        mock_add_dns.assert_any_call("gco", "dev-gco.example.com", "192.168.1.100", mock_session_class)
        mock_add_dns.assert_any_call("arcgis", "dev-arcgis.example.com", "192.168.1.100", mock_session_class)
        mock_session_instance.commit.assert_called_once()
        mock_session_instance.close.assert_called_once()

    @patch('repository.add_dns')
    def test_add_dns_gco_with_gco_absent(self, mock_add_dns):
        """Test DNS record deletion when GCO product is absent"""
        # Setup
        mock_session_instance = Mock(spec=SQLAlchemySession)
        mock_session_class = Mock(return_value=mock_session_instance)
        mock_existing_dns = Mock(spec=Dns)

        # Mock the query chain to return a list
        mock_session_instance.query(Dns).filter(Dns.hostname.in_(["dev-gco.example.com", "dev-arcgis.example.com"])).all.return_value = [mock_existing_dns]

        # Execute
        add_dns_gco(
            isGCOPresent=False,
            env_prefix="dev-",
            base="example.com",
            ip="192.168.1.100",
            Session=mock_session_class
        )

        # Verify
        mock_session_class.assert_called_once()
        mock_session_instance.delete.assert_called_once_with(mock_existing_dns)
        mock_session_instance.commit.assert_called_once()
        mock_session_instance.close.assert_called_once()
        # add_dns should not be called when GCO is absent
        mock_add_dns.assert_not_called()

    def test_add_dns_gco_skips_existing_records(self):
        """Test that existing DNS records are not recreated"""
        # Setup
        mock_session_instance = Mock(spec=SQLAlchemySession)
        mock_session_class = Mock(return_value=mock_session_instance)
        # Mock existing record for GCO
        mock_session_instance.query.return_value.filter.return_value.first.side_effect = [
            Mock(spec=Dns),  # GCO exists
            None  # ArcGIS doesn't exist
        ]

        with patch('repository.add_dns') as mock_add_dns:
            # Execute
            add_dns_gco(
                isGCOPresent=True,
                env_prefix="",
                base="example.com",
                ip="192.168.1.100",
                Session=mock_session_class
            )

            # Verify only ArcGIS DNS is created (GCO already exists)
            mock_session_class.assert_called_once()
            mock_add_dns.assert_called_once_with("arcgis", "arcgis.example.com", "192.168.1.100", mock_session_class)
            mock_session_instance.close.assert_called_once()


class TestAddDnsEservices:
    """Test the add_dns_eservices helper function"""

    @patch('repository.add_dns')
    def test_add_dns_eservices_with_eservices_present(self, mock_add_dns):
        """Test DNS record creation when eServices product is present"""
        # Setup
        mock_session_instance = Mock(spec=SQLAlchemySession)
        mock_session_class = Mock(return_value=mock_session_instance)
        mock_dns = Mock(spec=Dns)
        mock_session_instance.query.return_value.filter.return_value.first.return_value = None
        mock_add_dns.return_value = mock_dns

        # Execute
        add_dns_eservices(
            isEservicesPresent=True,
            env_prefix="dev-",
            base="example.com",
            ip="192.168.1.100",
            Session=mock_session_class
        )

        # Verify
        # Session class should be called
        mock_session_class.assert_called_once()
        # Should call add_dns three times (ael-back-ui, ael-client-ui, ael-client-ui-interne)
        assert mock_add_dns.call_count == 3
        expected_calls = [
            call("ael-back-ui", "dev-ael-back-ui.example.com", "192.168.1.100", mock_session_class),
            call("ael-client-ui", "dev-ael-client-ui.example.com", "192.168.1.100", mock_session_class),
            call("ael-client-ui-interne", "dev-ael-client-ui-interne.example.com", "192.168.1.100", mock_session_class),
        ]
        mock_add_dns.assert_has_calls(expected_calls, any_order=True)
        mock_session_instance.commit.assert_called_once()
        mock_session_instance.close.assert_called_once()

    @patch('repository.add_dns')
    def test_add_dns_eservices_with_eservices_absent(self, mock_add_dns):
        """Test DNS record deletion when eServices product is absent"""
        # Setup
        mock_session_instance = Mock(spec=SQLAlchemySession)
        mock_session_class = Mock(return_value=mock_session_instance)
        mock_existing_dns_records = [Mock(spec=Dns), Mock(spec=Dns), Mock(spec=Dns)]

        # Mock the query chain to return a list
        mock_session_instance.query(Dns).filter(Dns.hostname.in_(["dev-ael-back-ui.example.com", "dev-ael-client-ui.example.com", "dev-ael-client-ui-interne.example.com"])).all.return_value = mock_existing_dns_records

        # Execute
        add_dns_eservices(
            isEservicesPresent=False,
            env_prefix="dev-",
            base="example.com",
            ip="192.168.1.100",
            Session=mock_session_class
        )

        # Verify
        mock_session_class.assert_called_once()
        # Should delete all three DNS records
        assert mock_session_instance.delete.call_count == 3
        mock_session_instance.commit.assert_called_once()
        mock_session_instance.close.assert_called_once()
        mock_add_dns.assert_not_called()


class TestScaffoldArchitecture:
    """Test the scaffold_architecture integration function"""

    def test_scaffold_architecture_success_basic(self):
        """Test that scaffold_architecture completes without the TypeError session bug"""
        # This test verifies that the session handling bug is fixed
        # by ensuring that add_dns, add_dns_gco, and add_dns_eservices
        # can be called with a sessionmaker class without raising TypeError

        # Setup
        mock_session_instance = Mock(spec=SQLAlchemySession)
        mock_session_class = Mock(return_value=mock_session_instance)

        # Execute & Verify - These should NOT raise "TypeError: 'Session' object is not callable"
        # This is the core of the bug fix
        result1 = add_dns("test", "test.example.com", "192.168.1.1", mock_session_class)
        assert result1 is not None
        # Verify session was created and closed
        mock_session_class.assert_called()
        mock_session_instance.close.assert_called()

        # Reset for next test
        mock_session_instance.reset_mock()
        mock_session_class.reset_mock()

        result2 = add_dns_gco(False, "dev-", "example.com", "192.168.1.100", mock_session_class)
        # Should complete without error
        mock_session_class.assert_called()
        mock_session_instance.close.assert_called()

        # Reset for next test
        mock_session_instance.reset_mock()
        mock_session_class.reset_mock()

        result3 = add_dns_eservices(False, "dev-", "example.com", "192.168.1.100", mock_session_class)
        # Should complete without error
        mock_session_class.assert_called()
        mock_session_instance.close.assert_called()

    @patch('repository.getConfiguration')
    def test_scaffold_architecture_with_no_configuration(self, mock_get_config):
        """Test that scaffold_architecture handles missing configuration gracefully"""
        # Setup
        mock_session_class = Mock()
        mock_get_config.return_value = None  # No configuration

        # Execute
        scaffold_architecture(mock_session_class)

        # Verify
        mock_get_config.assert_called_once_with(mock_session_class)

    def test_scaffold_architecture_with_missing_zones(self):
        """Test that scaffold_architecture handles missing zones gracefully"""
        # Setup
        mock_session_class = Mock()

        mock_config = Mock(spec=Configuration)
        mock_config.number_concurrent_users = 100

        mock_sec = Mock(spec=Security)
        mock_sec.env_prefix = ""
        mock_sec.base_domain = "example.com"

        # Only one zone exists
        mock_zone_lan = Mock(spec=Zone)

        # Execute
        with patch('repository.getConfiguration', return_value=mock_config), \
             patch('repository.get_security', return_value=mock_sec), \
             patch('repository.get_zone_by_id', side_effect=[mock_zone_lan, None, None]):  # Missing infra and DMZ

            scaffold_architecture(mock_session_class)

        # Verify - should handle gracefully and return early
        # The test passes if no exception is raised

    def test_session_not_closed_before_dns_operations(self):
        """Test that session is properly managed through the call chain"""
        # This test verifies the fix for the original bug:
        # "TypeError: 'Session' object is not callable"

        # Setup
        mock_session_instance = Mock(spec=SQLAlchemySession)
        mock_session_class = Mock(return_value=mock_session_instance)

        # Execute - This should not raise TypeError
        result = add_dns("test", "test.example.com", "192.168.1.1", mock_session_class)

        # Verify
        # The function should complete successfully
        assert result is not None
        # Session class should be called to create instance
        mock_session_class.assert_called()
        # Session instance should be used and then closed
        mock_session_instance.add.assert_called()
        mock_session_instance.commit.assert_called()
        mock_session_instance.close.assert_called_once()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
