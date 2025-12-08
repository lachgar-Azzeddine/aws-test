#!/usr/bin/env python3
"""
Test script for the new VM configuration architecture with CONTROL/WORKER split.

This script tests:
1. seed_vm_configurations() with new architecture
2. get_vm_configurations() retrieval
3. migrate_vm_configurations() for legacy data
4. Proper implementation of constraints:
   - Control plane: exactly 3 master nodes
   - Worker nodes: scales with user count
   - Load balancers: exactly 2 VMs
   - RKEDMZ: exactly 3 VMs
5. All user counts: 100, 500, 1000, 10000
"""

import os
import sys
import tempfile

# Add the backend directory to the path
sys.path.insert(0, '/home/mrabbah/Documents/srm-cs/runner-src/backend')

from models import Base, VMConfiguration
from repository import (
    get_session,
    seed_vm_configurations,
    get_vm_configurations,
    migrate_vm_configurations,
    populate_db_fake_data,
)
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


def test_seed_vm_configurations():
    """Test that seed_vm_configurations creates the correct data."""
    print("=" * 80)
    print("TEST 1: seed_vm_configurations() with new architecture")
    print("=" * 80)

    # Create a temporary database
    with tempfile.NamedTemporaryFile(delete=False, suffix='.db') as tmp:
        db_path = tmp.name

    try:
        # Create database and session
        engine = create_engine(f'sqlite:///{db_path}')
        Base.metadata.create_all(engine)
        Session = sessionmaker(autocommit=False, autoflush=False, bind=engine)

        # Seed the configurations
        seed_vm_configurations(Session)

        # Verify configurations for each user count
        for user_count in [100, 500, 1000, 10000]:
            print(f"\n--- Verifying configuration for {user_count} users ---")
            configs = get_vm_configurations(user_count, Session)

            # Check control plane types
            assert "RKEAPPS_CONTROL" in configs, "RKEAPPS_CONTROL not found"
            assert "RKEMIDDLEWARE_CONTROL" in configs, "RKEMIDDLEWARE_CONTROL not found"
            assert configs["RKEAPPS_CONTROL"].node_count == 3, f"RKEAPPS_CONTROL should have 3 nodes, got {configs['RKEAPPS_CONTROL'].node_count}"
            assert configs["RKEMIDDLEWARE_CONTROL"].node_count == 3, f"RKEMIDDLEWARE_CONTROL should have 3 nodes, got {configs['RKEMIDDLEWARE_CONTROL'].node_count}"
            print(f"✓ Control plane: RKEAPPS_CONTROL={configs['RKEAPPS_CONTROL'].node_count} nodes, RKEMIDDLEWARE_CONTROL={configs['RKEMIDDLEWARE_CONTROL'].node_count} nodes")

            # Check worker types
            assert "RKEAPPS_WORKER" in configs, "RKEAPPS_WORKER not found"
            assert "RKEMIDDLEWARE_WORKER" in configs, "RKEMIDDLEWARE_WORKER not found"
            if user_count == 100:
                assert configs["RKEAPPS_WORKER"].node_count == 0, f"RKEAPPS_WORKER should have 0 nodes for 100 users, got {configs['RKEAPPS_WORKER'].node_count}"
                assert configs["RKEMIDDLEWARE_WORKER"].node_count == 0, f"RKEMIDDLEWARE_WORKER should have 0 nodes for 100 users, got {configs['RKEMIDDLEWARE_WORKER'].node_count}"
                print(f"✓ Worker nodes (100 users): RKEAPPS_WORKER={configs['RKEAPPS_WORKER'].node_count} nodes, RKEMIDDLEWARE_WORKER={configs['RKEMIDDLEWARE_WORKER'].node_count} nodes")
            elif user_count == 500:
                assert configs["RKEAPPS_WORKER"].node_count == 1, f"RKEAPPS_WORKER should have 1 node for 500 users, got {configs['RKEAPPS_WORKER'].node_count}"
                assert configs["RKEMIDDLEWARE_WORKER"].node_count == 1, f"RKEMIDDLEWARE_WORKER should have 1 node for 500 users, got {configs['RKEMIDDLEWARE_WORKER'].node_count}"
                print(f"✓ Worker nodes (500 users): RKEAPPS_WORKER={configs['RKEAPPS_WORKER'].node_count} nodes, RKEMIDDLEWARE_WORKER={configs['RKEMIDDLEWARE_WORKER'].node_count} nodes")
            elif user_count == 1000:
                assert configs["RKEAPPS_WORKER"].node_count == 5, f"RKEAPPS_WORKER should have 5 nodes for 1000 users, got {configs['RKEAPPS_WORKER'].node_count}"
                assert configs["RKEMIDDLEWARE_WORKER"].node_count == 4, f"RKEMIDDLEWARE_WORKER should have 4 nodes for 1000 users, got {configs['RKEMIDDLEWARE_WORKER'].node_count}"
                print(f"✓ Worker nodes (1000 users): RKEAPPS_WORKER={configs['RKEAPPS_WORKER'].node_count} nodes, RKEMIDDLEWARE_WORKER={configs['RKEMIDDLEWARE_WORKER'].node_count} nodes")
            elif user_count == 10000:
                assert configs["RKEAPPS_WORKER"].node_count == 6, f"RKEAPPS_WORKER should have 6 nodes for 10000 users, got {configs['RKEAPPS_WORKER'].node_count}"
                assert configs["RKEMIDDLEWARE_WORKER"].node_count == 12, f"RKEMIDDLEWARE_WORKER should have 12 nodes for 10000 users, got {configs['RKEMIDDLEWARE_WORKER'].node_count}"
                print(f"✓ Worker nodes (10000 users): RKEAPPS_WORKER={configs['RKEAPPS_WORKER'].node_count} nodes, RKEMIDDLEWARE_WORKER={configs['RKEMIDDLEWARE_WORKER'].node_count} nodes")

            # Check RKEDMZ (always 3 nodes)
            assert "RKEDMZ" in configs, "RKEDMZ not found"
            assert configs["RKEDMZ"].node_count == 3, f"RKEDMZ should always have 3 nodes, got {configs['RKEDMZ'].node_count}"
            print(f"✓ RKEDMZ: {configs['RKEDMZ'].node_count} nodes (fixed)")

            # Check Load Balancers (always 2 nodes)
            for lb_type in ["LBLAN", "LBDMZ", "LBINTEGRATION"]:
                assert lb_type in configs, f"{lb_type} not found"
                assert configs[lb_type].node_count == 2, f"{lb_type} should always have 2 nodes, got {configs[lb_type].node_count}"
                assert configs[lb_type].data_disk_size == 0, f"{lb_type} should have 0GB data disk, got {configs[lb_type].data_disk_size}GB"
            print(f"✓ Load Balancers: LBLAN={configs['LBLAN'].node_count} nodes, LBDMZ={configs['LBDMZ'].node_count} nodes, LBINTEGRATION={configs['LBINTEGRATION'].node_count} nodes (all fixed at 2, 0GB data disk)")

            # Check roles - different for 100 users (combined) vs 500+ (separated)
            if user_count == 100:
                # Combined architecture: CONTROL nodes have all roles
                expected_control_roles = "master,worker,cns"
            else:
                # Separated architecture: CONTROL nodes are master only, CNS nodes handle storage
                expected_control_roles = "master"

            assert configs["RKEAPPS_CONTROL"].roles == expected_control_roles, f"RKEAPPS_CONTROL should have '{expected_control_roles}' roles for {user_count} users, got {configs['RKEAPPS_CONTROL'].roles}"
            assert configs["RKEAPPS_WORKER"].roles == "worker", f"RKEAPPS_WORKER should have 'worker' role, got {configs['RKEAPPS_WORKER'].roles}"
            assert configs["RKEMIDDLEWARE_CONTROL"].roles == expected_control_roles, f"RKEMIDDLEWARE_CONTROL should have '{expected_control_roles}' roles for {user_count} users, got {configs['RKEMIDDLEWARE_CONTROL'].roles}"
            assert configs["RKEMIDDLEWARE_WORKER"].roles == "worker", f"RKEMIDDLEWARE_WORKER should have 'worker' role, got {configs['RKEMIDDLEWARE_WORKER'].roles}"

            # Check CNS nodes for 500+ users
            if user_count >= 500:
                assert "RKEAPPS_CNS" in configs, "RKEAPPS_CNS not found for 500+ users"
                assert configs["RKEAPPS_CNS"].roles == "worker,cns", f"RKEAPPS_CNS should have 'worker,cns' roles, got {configs['RKEAPPS_CNS'].roles}"
                assert "RKEMIDDLEWARE_CNS" in configs, "RKEMIDDLEWARE_CNS not found for 500+ users"
                assert configs["RKEMIDDLEWARE_CNS"].roles == "worker,cns", f"RKEMIDDLEWARE_CNS should have 'worker,cns' roles, got {configs['RKEMIDDLEWARE_CNS'].roles}"
                print(f"✓ Roles ({user_count} users - separated): CONTROL='{expected_control_roles}', CNS='worker,cns', WORKER='worker'")
            else:
                print(f"✓ Roles ({user_count} users - combined): CONTROL='{expected_control_roles}', WORKER='worker'")

        print("\n✅ TEST 1 PASSED: seed_vm_configurations() works correctly with new architecture")

    finally:
        # Clean up
        if os.path.exists(db_path):
            os.unlink(db_path)


def test_migrate_vm_configurations():
    """Test that migrate_vm_configurations correctly migrates old data."""
    print("\n" + "=" * 80)
    print("TEST 2: migrate_vm_configurations() for legacy data")
    print("=" * 80)

    # Create a temporary database
    with tempfile.NamedTemporaryFile(delete=False, suffix='.db') as tmp:
        db_path = tmp.name

    try:
        # Create database and session
        engine = create_engine(f'sqlite:///{db_path}')
        Base.metadata.create_all(engine)
        Session = sessionmaker(autocommit=False, autoflush=False, bind=engine)

        # Simulate old architecture data (insert manually)
        session = Session()
        old_configs = [
            # Old RKEAPPS with 5 nodes
            VMConfiguration(user_count=1000, vm_type="RKEAPPS", node_count=5, cpu_per_node=8, ram_per_node=16384, os_disk_size=80, data_disk_size=200, roles="master,worker,cns"),
            # Old RKEMIDDLEWARE with 5 nodes
            VMConfiguration(user_count=1000, vm_type="RKEMIDDLEWARE", node_count=5, cpu_per_node=8, ram_per_node=16384, os_disk_size=80, data_disk_size=200, roles="master,worker,cns"),
            # RKEDMZ with 5 nodes (should be fixed to 3)
            VMConfiguration(user_count=1000, vm_type="RKEDMZ", node_count=5, cpu_per_node=6, ram_per_node=8192, os_disk_size=80, data_disk_size=150, roles="master,worker,cns"),
            # Load balancers with 3 nodes (should be fixed to 2)
            VMConfiguration(user_count=1000, vm_type="LBLAN", node_count=3, cpu_per_node=4, ram_per_node=4096, os_disk_size=60, data_disk_size=0, roles="loadbalancer"),
            VMConfiguration(user_count=1000, vm_type="LBDMZ", node_count=3, cpu_per_node=4, ram_per_node=4096, os_disk_size=60, data_disk_size=0, roles="loadbalancer"),
            VMConfiguration(user_count=1000, vm_type="LBINTEGRATION", node_count=3, cpu_per_node=4, ram_per_node=4096, os_disk_size=60, data_disk_size=0, roles="loadbalancer"),
            # Infrastructure VMs
            VMConfiguration(user_count=1000, vm_type="GITOPS", node_count=1, cpu_per_node=4, ram_per_node=8192, os_disk_size=60, data_disk_size=200, roles="git,docker-registry"),
            VMConfiguration(user_count=1000, vm_type="MONITORING", node_count=1, cpu_per_node=6, ram_per_node=20480, os_disk_size=80, data_disk_size=200, roles="admin,monitoring"),
            VMConfiguration(user_count=1000, vm_type="VAULT", node_count=1, cpu_per_node=4, ram_per_node=16384, os_disk_size=80, data_disk_size=200, roles="vault"),
        ]
        for config in old_configs:
            session.add(config)
        session.commit()
        session.close()

        print("\n--- Before migration ---")
        configs = get_vm_configurations(1000, Session)
        if 'RKEAPPS' in configs:
            print(f"RKEAPPS: {configs['RKEAPPS'].node_count} nodes")
        else:
            print(f"RKEAPPS: NOT FOUND")
        if 'RKEMIDDLEWARE' in configs:
            print(f"RKEMIDDLEWARE: {configs['RKEMIDDLEWARE'].node_count} nodes")
        else:
            print(f"RKEMIDDLEWARE: NOT FOUND")
        if 'RKEDMZ' in configs:
            print(f"RKEDMZ: {configs['RKEDMZ'].node_count} nodes")
        else:
            print(f"RKEDMZ: NOT FOUND")
        if 'LBLAN' in configs:
            print(f"LBLAN: {configs['LBLAN'].node_count} nodes")
        else:
            print(f"LBLAN: NOT FOUND")

        # Run migration
        print("\n--- Running migration ---")
        migrate_vm_configurations(Session)

        print("\n--- After migration ---")
        configs = get_vm_configurations(1000, Session)

        # Verify RKEAPPS was split
        assert "RKEAPPS_CONTROL" in configs, "RKEAPPS_CONTROL not found after migration"
        assert configs["RKEAPPS_CONTROL"].node_count == 3, f"RKEAPPS_CONTROL should have 3 nodes after migration, got {configs['RKEAPPS_CONTROL'].node_count}"
        assert "RKEAPPS_WORKER" in configs, "RKEAPPS_WORKER not found after migration"
        assert configs["RKEAPPS_WORKER"].node_count == 2, f"RKEAPPS_WORKER should have 2 nodes after migration (5-3), got {configs['RKEAPPS_WORKER'].node_count}"
        print(f"✓ RKEAPPS split: CONTROL={configs['RKEAPPS_CONTROL'].node_count} nodes, WORKER={configs['RKEAPPS_WORKER'].node_count} nodes")

        # Verify RKEMIDDLEWARE was split
        assert "RKEMIDDLEWARE_CONTROL" in configs, "RKEMIDDLEWARE_CONTROL not found after migration"
        assert configs["RKEMIDDLEWARE_CONTROL"].node_count == 3, f"RKEMIDDLEWARE_CONTROL should have 3 nodes after migration, got {configs['RKEMIDDLEWARE_CONTROL'].node_count}"
        assert "RKEMIDDLEWARE_WORKER" in configs, "RKEMIDDLEWARE_WORKER not found after migration"
        assert configs["RKEMIDDLEWARE_WORKER"].node_count == 2, f"RKEMIDDLEWARE_WORKER should have 2 nodes after migration (5-3), got {configs['RKEMIDDLEWARE_WORKER'].node_count}"
        print(f"✓ RKEMIDDLEWARE split: CONTROL={configs['RKEMIDDLEWARE_CONTROL'].node_count} nodes, WORKER={configs['RKEMIDDLEWARE_WORKER'].node_count} nodes")

        # Verify RKEDMZ was fixed to 3 nodes
        assert "RKEDMZ" in configs, "RKEDMZ not found after migration"
        assert configs["RKEDMZ"].node_count == 3, f"RKEDMZ should be fixed to 3 nodes, got {configs['RKEDMZ'].node_count}"
        print(f"✓ RKEDMZ fixed: {configs['RKEDMZ'].node_count} nodes")

        # Verify Load Balancers were fixed to 2 nodes
        for lb_type in ["LBLAN", "LBDMZ", "LBINTEGRATION"]:
            assert lb_type in configs, f"{lb_type} not found after migration"
            assert configs[lb_type].node_count == 2, f"{lb_type} should be fixed to 2 nodes, got {configs[lb_type].node_count}"
        print(f"✓ Load Balancers fixed: LBLAN={configs['LBLAN'].node_count} nodes, LBDMZ={configs['LBDMZ'].node_count} nodes, LBINTEGRATION={configs['LBINTEGRATION'].node_count} nodes")

        print("\n✅ TEST 2 PASSED: migrate_vm_configurations() works correctly")

    finally:
        # Clean up
        if os.path.exists(db_path):
            os.unlink(db_path)


def test_vm_counts_summary():
    """Test and display a summary of VM counts for all user counts."""
    print("\n" + "=" * 80)
    print("TEST 3: VM Count Summary for All User Counts")
    print("=" * 80)

    # Create a temporary database
    with tempfile.NamedTemporaryFile(delete=False, suffix='.db') as tmp:
        db_path = tmp.name

    try:
        # Create database and session
        engine = create_engine(f'sqlite:///{db_path}')
        Base.metadata.create_all(engine)
        Session = sessionmaker(autocommit=False, autoflush=False, bind=engine)

        # Seed the configurations
        seed_vm_configurations(Session)

        # Display summary for each user count
        for user_count in [100, 500, 1000, 10000]:
            print(f"\n{'='*60}")
            print(f"Configuration for {user_count} users")
            print(f"{'='*60}")
            configs = get_vm_configurations(user_count, Session)

            # Control Plane
            control_rkeapps = configs["RKEAPPS_CONTROL"].node_count
            control_rkemiddleware = configs["RKEMIDDLEWARE_CONTROL"].node_count
            control_rkedmz = configs["RKEDMZ"].node_count

            # Workers
            worker_rkeapps = configs["RKEAPPS_WORKER"].node_count
            worker_rkemiddleware = configs["RKEMIDDLEWARE_WORKER"].node_count

            # Load Balancers
            lb_lan = configs["LBLAN"].node_count
            lb_dmz = configs["LBDMZ"].node_count
            lb_integration = configs["LBINTEGRATION"].node_count

            # Infrastructure
            gitops = configs["GITOPS"].node_count
            monitoring = configs["MONITORING"].node_count
            vault = configs["VAULT"].node_count

            # Calculate totals
            total_nodes = (
                control_rkeapps + worker_rkeapps +
                control_rkemiddleware + worker_rkemiddleware +
                control_rkedmz +
                lb_lan + lb_dmz + lb_integration +
                gitops + monitoring + vault
            )

            # Display results
            print(f"\nControl Plane (Masters - Fixed at 3):")
            print(f"  RKEAPPS_CONTROL:        {control_rkeapps:3d} nodes")
            print(f"  RKEMIDDLEWARE_CONTROL:  {control_rkemiddleware:3d} nodes")
            print(f"  RKEDMZ:                 {control_rkedmz:3d} nodes")

            print(f"\nWorker Nodes (Scales with load):")
            print(f"  RKEAPPS_WORKER:         {worker_rkeapps:3d} nodes")
            print(f"  RKEMIDDLEWARE_WORKER:   {worker_rkemiddleware:3d} nodes")

            print(f"\nLoad Balancers (Fixed at 2 for HA):")
            print(f"  LBLAN:                  {lb_lan:3d} nodes")
            print(f"  LBDMZ:                  {lb_dmz:3d} nodes")
            print(f"  LBINTEGRATION:          {lb_integration:3d} nodes")

            print(f"\nInfrastructure (Fixed at 1):")
            print(f"  GITOPS:                 {gitops:3d} node")
            print(f"  MONITORING:             {monitoring:3d} node")
            print(f"  VAULT:                  {vault:3d} node")

            print(f"\n{'='*60}")
            print(f"TOTAL VMs: {total_nodes:3d} nodes")
            print(f"{'='*60}")

            # Verify constraints
            assert control_rkeapps == 3, f"RKEAPPS_CONTROL should be 3, got {control_rkeapps}"
            assert control_rkemiddleware == 3, f"RKEMIDDLEWARE_CONTROL should be 3, got {control_rkemiddleware}"
            assert control_rkedmz == 3, f"RKEDMZ should be 3, got {control_rkedmz}"
            assert lb_lan == 2, f"LBLAN should be 2, got {lb_lan}"
            assert lb_dmz == 2, f"LBDMZ should be 2, got {lb_dmz}"
            assert lb_integration == 2, f"LBINTEGRATION should be 2, got {lb_integration}"
            assert gitops == 1, f"GITOPS should be 1, got {gitops}"
            assert monitoring == 1, f"MONITORING should be 1, got {monitoring}"
            assert vault == 1, f"VAULT should be 1, got {vault}"

        print("\n✅ TEST 3 PASSED: All VM counts are correct for all user counts")

    finally:
        # Clean up
        if os.path.exists(db_path):
            os.unlink(db_path)


def test_cns_constraint():
    """Test that only VMs with 'cns' role have data disks."""
    print("\n" + "=" * 80)
    print("TEST 4: CNS Constraint - Only VMs with 'cns' role should have data disks")
    print("=" * 80)

    # Create a temporary database
    with tempfile.NamedTemporaryFile(delete=False, suffix='.db') as tmp:
        db_path = tmp.name

    try:
        # Create database and session
        engine = create_engine(f'sqlite:///{db_path}')
        Base.metadata.create_all(engine)
        Session = sessionmaker(autocommit=False, autoflush=False, bind=engine)

        # Seed the configurations
        seed_vm_configurations(Session)

        # Test each user count
        for user_count in [100, 500, 1000, 10000]:
            print(f"\n--- Verifying CNS constraint for {user_count} users ---")
            configs = get_vm_configurations(user_count, Session)

            # VMs WITH "cns" role (should have data disks > 0)
            # Different for 100 users (combined) vs 500+ (separated)
            if user_count == 100:
                # Combined architecture: CONTROL nodes have 'cns' role
                cns_vms = {
                    "RKEAPPS_CONTROL": configs["RKEAPPS_CONTROL"],
                    "RKEMIDDLEWARE_CONTROL": configs["RKEMIDDLEWARE_CONTROL"],
                    "RKEDMZ": configs["RKEDMZ"],
                }
            else:
                # Separated architecture: CNS nodes have 'cns' role, CONTROL nodes don't
                cns_vms = {
                    "RKEAPPS_CNS": configs["RKEAPPS_CNS"],
                    "RKEMIDDLEWARE_CNS": configs["RKEMIDDLEWARE_CNS"],
                    "RKEDMZ": configs["RKEDMZ"],
                }

            # VMs WITHOUT "cns" role (should have data disks = 0)
            if user_count == 100:
                non_cns_vms = {
                    "RKEAPPS_WORKER": configs["RKEAPPS_WORKER"],
                    "RKEMIDDLEWARE_WORKER": configs["RKEMIDDLEWARE_WORKER"],
                }
            else:
                non_cns_vms = {
                    "RKEAPPS_CONTROL": configs["RKEAPPS_CONTROL"],
                    "RKEMIDDLEWARE_CONTROL": configs["RKEMIDDLEWARE_CONTROL"],
                    "RKEAPPS_WORKER": configs["RKEAPPS_WORKER"],
                    "RKEMIDDLEWARE_WORKER": configs["RKEMIDDLEWARE_WORKER"],
                }

            # Load Balancers (should always have 0 data disk)
            lb_vms = {
                "LBLAN": configs["LBLAN"],
                "LBDMZ": configs["LBDMZ"],
                "LBINTEGRATION": configs["LBINTEGRATION"],
            }

            # Verify CNS VMs have data disks
            print("\n  VMs WITH 'cns' role (should have data disks > 0):")
            for vm_type, config in cns_vms.items():
                assert config.data_disk_size > 0, f"{vm_type} has 'cns' role but data_disk_size is {config.data_disk_size}, should be > 0"
                print(f"    ✓ {vm_type}: {config.data_disk_size}GB (has 'cns' role)")

            # Verify non-CNS worker VMs have 0 data disk
            print("\n  VMs WITHOUT 'cns' role (should have data disks = 0):")
            for vm_type, config in non_cns_vms.items():
                assert config.data_disk_size == 0, f"{vm_type} does NOT have 'cns' role but data_disk_size is {config.data_disk_size}, should be 0"
                print(f"    ✓ {vm_type}: {config.data_disk_size}GB (no 'cns' role)")

            # Verify Load Balancers have 0 data disk
            print("\n  Load Balancers (should have data disks = 0):")
            for vm_type, config in lb_vms.items():
                assert config.data_disk_size == 0, f"{vm_type} should have 0 data disk, got {config.data_disk_size}"
                print(f"    ✓ {vm_type}: {config.data_disk_size}GB")

        print("\n✅ TEST 4 PASSED: CNS constraint verified - only VMs with 'cns' role have data disks")

    finally:
        # Clean up
        if os.path.exists(db_path):
            os.unlink(db_path)


def main():
    """Run all tests."""
    print("\n" + "=" * 80)
    print("VM CONFIGURATION NEW ARCHITECTURE TEST SUITE")
    print("Testing CONTROL/WORKER split, fixed LBs, and RKEDMZ constraints")
    print("=" * 80 + "\n")

    try:
        test_seed_vm_configurations()
        test_migrate_vm_configurations()
        test_vm_counts_summary()
        test_cns_constraint()

        print("\n" + "=" * 80)
        print("✅ ALL TESTS PASSED!")
        print("=" * 80)
        print("\nSummary:")
        print("  ✓ seed_vm_configurations() creates correct new architecture")
        print("  ✓ get_vm_configurations() retrieves configurations correctly")
        print("  ✓ migrate_vm_configurations() migrates legacy data correctly")
        print("  ✓ Control plane: exactly 3 master nodes")
        print("  ✓ Worker nodes: scales with user count")
        print("  ✓ Load balancers: exactly 2 VMs (fixed)")
        print("  ✓ RKEDMZ: exactly 3 VMs (fixed)")
        print("  ✓ All user counts tested: 100, 500, 1000, 10000")
        print("  ✓ CNS constraint: Only VMs with 'cns' role have data disks")
        print("=" * 80 + "\n")

    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
