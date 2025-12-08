#!/usr/bin/env python3
"""
Test script to validate the hostname prefix fix.

This script tests the fix for the double prefix issue in VM hostname generation.
"""

def generate_hostname(hostname_prefix, prefix, i):
    """
    Simulates the fixed hostname generation logic from repository.py.

    Args:
        hostname_prefix: The base hostname prefix from hostname_map
        prefix: The environment prefix (e.g., "test-")
        i: The VM index number

    Returns:
        The generated hostname
    """
    # Strip any existing environment prefix from hostname_prefix to prevent duplication
    # This handles cases where hostname_map values might already include the prefix
    # Only strip if prefix includes trailing hyphen (real-world scenario)
    base_hostname = hostname_prefix
    if prefix and prefix.endswith("-") and hostname_prefix.startswith(prefix):
        base_hostname = hostname_prefix[len(prefix):]

    return f"{prefix}{base_hostname}{i}"


def test_hostname_generation():
    """
    Test various scenarios for hostname generation.
    """
    test_cases = [
        # Test case format: (hostname_prefix, prefix, vm_index, expected_result, description)

        # Test 1: Normal case - no existing prefix
        ("vault", "test-", 1, "test-vault1", "Normal case: VAULT with test- prefix"),

        # Test 2: Already prefixed (the bug scenario)
        ("test-vault", "test-", 1, "test-vault1", "Bug case: VAULT already has test- prefix"),

        # Test 3: Empty prefix
        ("vault", "", 1, "vault1", "Empty prefix: VAULT with no prefix"),

        # Test 4: Already prefixed with empty prefix
        ("test-vault", "", 1, "test-vault1", "Pre-existing prefix with empty env prefix"),

        # Test 5: Different prefix
        ("test-vault", "prod-", 1, "prod-test-vault1", "Different prefix: changing from test- to prod-"),

        # Test 6: LBLAN multi-VM
        ("lblan", "test-", 1, "test-lblan1", "LBLAN VM 1 with test-"),
        ("lblan", "test-", 2, "test-lblan2", "LBLAN VM 2 with test-"),
        ("test-lblan", "test-", 1, "test-lblan1", "LBLAN already prefixed"),

        # Test 7: RKEAPPS_CONTROL
        ("rkeapp-master", "test-", 1, "test-rkeapp-master1", "RKEAPPS_CONTROL VM 1"),
        ("test-rkeapp-master", "test-", 1, "test-rkeapp-master1", "RKEAPPS_CONTROL already prefixed"),

        # Test 8: GITOPS (single VM)
        ("gitops", "test-", 1, "test-gitops1", "GITOPS with test-"),
        ("test-gitops", "test-", 1, "test-gitops1", "GITOPS already prefixed"),

        # Test 9: Different environment prefixes
        ("dev-vault", "dev-", 1, "dev-vault1", "Dev environment with dev- prefix"),
        ("staging-vault", "staging-", 1, "staging-vault1", "Staging environment"),
        ("prod-vault", "prod-", 1, "prod-vault1", "Production environment"),

        # Test 10: Long prefix
        ("verylongprefix-vault", "verylongprefix-", 1, "verylongprefix-vault1", "Long prefix"),

        # Test 11: Complex VM types
        ("rkemiddleware-master", "test-", 3, "test-rkemiddleware-master3", "RKEMIDDLEWARE_CONTROL VM 3"),
        ("rkeapp-worker", "test-", 5, "test-rkeapp-worker5", "RKEAPPS_WORKER VM 5"),
    ]

    print("=" * 80)
    print("HOSTNAME PREFIX FIX - TEST SUITE")
    print("=" * 80)
    print()

    passed = 0
    failed = 0

    for hostname_prefix, prefix, vm_index, expected, description in test_cases:
        result = generate_hostname(hostname_prefix, prefix, vm_index)
        status = "✓ PASS" if result == expected else "✗ FAIL"

        if result == expected:
            passed += 1
            print(f"{status} | {description}")
            print(f"       Input: hostname_prefix='{hostname_prefix}', prefix='{prefix}', i={vm_index}")
            print(f"       Output: '{result}'")
        else:
            failed += 1
            print(f"{status} | {description}")
            print(f"       Input: hostname_prefix='{hostname_prefix}', prefix='{prefix}', i={vm_index}")
            print(f"       Expected: '{expected}'")
            print(f"       Got:      '{result}'")
        print()

    print("=" * 80)
    print(f"SUMMARY: {passed} passed, {failed} failed out of {len(test_cases)} tests")
    print("=" * 80)

    return failed == 0


def test_edge_cases():
    """
    Test edge cases that might cause issues.
    """
    print("\n" + "=" * 80)
    print("EDGE CASE TESTS")
    print("=" * 80)
    print()

    edge_cases = [
        # Edge case: prefix in middle of hostname
        ("test-vault-dev", "test-", 1, "test-vault-dev1", "Prefix appears twice (shouldn't strip)"),

        # Edge case: partial match
        ("test-vault", "test", 1, "testtest-vault1", "Prefix without trailing hyphen (shouldn't strip - no hyphen in prefix)"),

        # Edge case: single character prefix
        ("a-vault", "a-", 1, "a-vault1", "Single char prefix"),

        # Edge case: numeric prefix (unusual but possible)
        ("1-vault", "1-", 1, "1-vault1", "Numeric prefix"),
    ]

    passed = 0
    failed = 0

    for hostname_prefix, prefix, vm_index, expected, description in edge_cases:
        result = generate_hostname(hostname_prefix, prefix, vm_index)
        status = "✓ PASS" if result == expected else "✗ FAIL"

        if result == expected:
            passed += 1
            print(f"{status} | {description}")
        else:
            failed += 1
            print(f"{status} | {description}")
            print(f"       Expected: '{expected}'")
            print(f"       Got:      '{result}'")
        print()

    print(f"EDGE CASES: {passed} passed, {failed} failed")
    return failed == 0


def demonstrate_fix():
    """
    Demonstrate the fix with the original bug scenario.
    """
    print("\n" + "=" * 80)
    print("DEMONSTRATION: Original Bug Scenario")
    print("=" * 80)
    print()

    print("Scenario: User has env_prefix='test' and hostname_map contains 'test-vault'")
    print()

    # Simulate old behavior (without the fix)
    def old_generate_hostname(hostname_prefix, prefix, i):
        return f"{prefix}{hostname_prefix}{i}"

    hostname_prefix = "test-vault"
    prefix = "test-"
    vm_index = 1

    print(f"Input:")
    print(f"  hostname_prefix = '{hostname_prefix}'")
    print(f"  prefix = '{prefix}'")
    print(f"  vm_index = {vm_index}")
    print()

    old_result = old_generate_hostname(hostname_prefix, prefix, vm_index)
    new_result = generate_hostname(hostname_prefix, prefix, vm_index)

    print(f"Results:")
    print(f"  Old (buggy) behavior: '{old_result}'")
    print(f"  New (fixed) behavior: '{new_result}'")
    print()
    print(f"Expected: 'test-vault1'")
    print(f"Bug was:  '{old_result}' ❌ (includes duplicate prefix!)")
    print(f"Fixed:    '{new_result}' ✓ (duplicate prefix removed)")
    print()


if __name__ == "__main__":
    # Run all tests
    all_passed = True

    # Test main scenarios
    if not test_hostname_generation():
        all_passed = False

    # Test edge cases
    if not test_edge_cases():
        all_passed = False

    # Demonstrate the fix
    demonstrate_fix()

    # Final summary
    print("\n" + "=" * 80)
    if all_passed:
        print("✓ ALL TESTS PASSED - Fix is working correctly!")
    else:
        print("✗ SOME TESTS FAILED - Please review the implementation")
    print("=" * 80)
