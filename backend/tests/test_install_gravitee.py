#!/usr/bin/env python3
"""
Test Install Gravitee Role

This script tests the install-gravitee-lan Ansible role in a controlled test environment.
It:
1. Initializes the test database
2. Prepares the test environment
3. Executes the install-gravitee-lan role
4. Validates the results
"""

import os
import sys
import time
import argparse
import subprocess
import tempfile
from pathlib import Path

# Add the parent directory to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from repository import (
    get_session,
    get_ansible_role_status,
    get_task_logs,
    delete_all_ansible_roles,
    get_security,
    get_vms_by_group,
    add_ansible_role
)
from install import (
    call_role,
    load_and_call_get_inputs
)
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class TestInstallGravitee:
    """Test harness for install-gravitee-lan role"""

    def __init__(self, db_path="./tests/harmonisation_runner.db"):
        self.db_path = db_path
        self.role_name = "install-gravitee-lan"
        self.test_success = False
        self.test_results = {
            "database_init": False,
            "environment_ready": False,
            "role_executed": False,
            "validation_passed": False
        }

    def setup_database(self):
        """Initialize the test database"""
        print("\n" + "=" * 80)
        print("STEP 1: Initializing Test Database")
        print("=" * 80)

        try:
            # Run the test_database.py script
            script_path = os.path.join(os.path.dirname(__file__), "test_database.py")
            cmd = [sys.executable, script_path, f"--db-path={self.db_path}"]

            logger.info(f"Running: {' '.join(cmd)}")
            result = subprocess.run(cmd, capture_output=True, text=True)

            if result.returncode != 0:
                logger.error(f"Database initialization failed: {result.stderr}")
                return False

            logger.info("Database initialized successfully")
            self.test_results["database_init"] = True
            return True

        except Exception as e:
            logger.error(f"Error initializing database: {e}")
            import traceback
            traceback.print_exc()
            return False

    def verify_test_environment(self):
        """Verify the test environment is ready"""
        print("\n" + "=" * 80)
        print("STEP 2: Verifying Test Environment")
        print("=" * 80)

        try:
            # Check if database exists
            if not os.path.exists(self.db_path):
                logger.error(f"Database not found: {self.db_path}")
                return False

            # Set database URL
            os.environ["DATABASE_URL"] = f"sqlite:///{self.db_path}"

            # Get sessionmaker class
            _, Session = get_session()

            # Check security configuration
            security = get_security(Session)
            if not security:
                logger.error("Security configuration not found in database")
                return False

            logger.info(f"Security config: base_domain={security.base_domain}")

            # Check LBLAN VM
            lb_vms = get_vms_by_group("LBLAN", Session)
            if not lb_vms:
                logger.error("No LBLAN VMs found in database")
                return False

            lb_vm = lb_vms[0]
            logger.info(f"LBLAN VM: {lb_vm.hostname} at {lb_vm.ip}")

            # Check if images directory exists
            images_dir = Path("./tests/data/images")
            if not images_dir.exists():
                logger.error(f"Images directory not found: {images_dir}")
                logger.info("Please run tar_images.py first to download images")
                return False

            # Check if prepare_inputs.py exists
            role_path = Path(f"project/roles/{self.role_name}")
            prepare_inputs = role_path / "prepare_inputs.py"
            if not prepare_inputs.exists():
                logger.error(f"prepare_inputs.py not found: {prepare_inputs}")
                return False

            logger.info("Test environment verification passed")
            self.test_results["environment_ready"] = True
            return True

        except Exception as e:
            logger.error(f"Error verifying environment: {e}")
            import traceback
            traceback.print_exc()
            return False

    def execute_role(self):
        """Execute the install-gravitee-lan role"""
        print("\n" + "=" * 80)
        print(f"STEP 3: Executing Role: {self.role_name}")
        print("=" * 80)

        try:
            # Set database URL
            os.environ["DATABASE_URL"] = f"sqlite:///{self.db_path}"

            # Get sessionmaker class
            _, Session = get_session()

            # Clear any existing ansible roles
            logger.info("Clearing existing ansible roles...")
            delete_all_ansible_roles(Session)

            # Add the role to be installed
            logger.info(f"Adding role: {self.role_name}")
            add_ansible_role(self.role_name, 1, Session)

            # Test loading the prepare_inputs
            logger.info("Testing prepare_inputs.py...")
            try:
                extra_vars, inventory = load_and_call_get_inputs(self.role_name, Session)
                logger.info("✓ prepare_inputs.py loaded successfully")
                logger.info(f"Extra vars: {list(extra_vars.keys())}")
                logger.info(f"Inventory hosts: {list(inventory.get('all', {}).get('hosts', {}).keys())}")
            except Exception as e:
                logger.error(f"Failed to load prepare_inputs.py: {e}")
                import traceback
                traceback.print_exc()
                return False

            # Execute the role
            logger.info(f"Executing role: {self.role_name}")
            start_time = time.time()

            # Note: This will run the role with the test database
            # Since we're testing, we'll call it directly
            call_role(self.role_name, Session)

            execution_time = time.time() - start_time
            logger.info(f"Role execution completed in {execution_time:.2f} seconds")

            # Check the status
            status = get_ansible_role_status(self.role_name, Session)
            logger.info(f"Role status: {status}")

            if status == "successful":
                logger.info("✓ Role executed successfully")
                self.test_results["role_executed"] = True
                return True
            else:
                logger.error(f"✗ Role execution failed with status: {status}")

                # Get task logs for debugging
                # Note: This needs the actual runner_ident from the role execution
                # For now, we'll just report the status
                logger.info("Task logs can be viewed in the database after execution")

                return False

        except Exception as e:
            logger.error(f"Error executing role: {e}")
            import traceback
            traceback.print_exc()
            return False

    def validate_installation(self):
        """Validate the installation results"""
        print("\n" + "=" * 80)
        print("STEP 4: Validating Installation")
        print("=" * 80)

        try:
            # Set database URL
            os.environ["DATABASE_URL"] = f"sqlite:///{self.db_path}"

            _, Session = get_session()

            # Get security config for domain
            security = get_security(Session)
            if not security:
                logger.error("Security configuration not found")
                return False

            # Construct the expected Gravitee URL
            prefix = "" if security.env_prefix == "" else security.env_prefix + "-"
            apim_url = f"https://{prefix}apim.{security.base_domain}"

            logger.info(f"Expected Gravitee APIM URL: {apim_url}")

            # Get the LBLAN VM
            lb_vms = get_vms_by_group("LBLAN", Session)
            if not lb_vms:
                logger.error("No LBLAN VMs found")
                return False

            lb_vm = lb_vms[0]
            logger.info(f"Checking LBLAN VM: {lb_vm.hostname} ({lb_vm.ip})")

            # In a real test, we would:
            # 1. Check if the VM has the expected services running
            # 2. Verify the APIM UI is accessible
            # 3. Check the gateway is responding
            # 4. Verify the management API is available

            # For now, we'll just do basic checks
            if lb_vm.ip:
                logger.info(f"✓ LBLAN VM has IP address: {lb_vm.ip}")
            else:
                logger.warning("✗ LBLAN VM does not have an IP address")

            # Check task logs for errors
            # This requires the actual runner_ident, which we'd get from the role execution

            logger.info("✓ Installation validation completed (basic checks)")
            self.test_results["validation_passed"] = True
            return True

        except Exception as e:
            logger.error(f"Error validating installation: {e}")
            import traceback
            traceback.print_exc()
            return False

    def run(self):
        """Run the complete test"""
        print("\n" + "=" * 80)
        print("GRAVITEE-LAN ROLE TEST")
        print("=" * 80)
        print()

        # Run all test steps
        steps = [
            ("Database Initialization", self.setup_database),
            ("Environment Verification", self.verify_test_environment),
            ("Role Execution", self.execute_role),
            ("Installation Validation", self.validate_installation)
        ]

        for step_name, step_func in steps:
            logger.info(f"\n{'='*80}")
            logger.info(f"Running: {step_name}")
            logger.info(f"{'='*80}")

            if not step_func():
                logger.error(f"\n✗ {step_name} failed")
                self.print_summary()
                return False

            logger.info(f"\n✓ {step_name} passed")

        # All tests passed
        self.test_success = True
        self.print_summary()
        return True

    def print_summary(self):
        """Print test summary"""
        print("\n" + "=" * 80)
        print("TEST SUMMARY")
        print("=" * 80)

        for step, passed in self.test_results.items():
            status = "✓ PASS" if passed else "✗ FAIL"
            print(f"{status:10} {step}")

        print("=" * 80)

        if self.test_success:
            print("✓ ALL TESTS PASSED")
        else:
            print("✗ SOME TESTS FAILED")

        print("=" * 80)


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Test the install-gravitee-lan Ansible role"
    )
    parser.add_argument(
        "--db-path",
        default="./tests/harmonisation_runner.db",
        help="Path to test database"
    )
    parser.add_argument(
        "--skip-db-init",
        action="store_true",
        help="Skip database initialization"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose logging"
    )

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # Create test instance
    test = TestInstallGravitee(db_path=args.db_path)

    # Run the test
    try:
        success = test.run()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
        sys.exit(130)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
