#!/usr/bin/env python3
"""
Test script for IP pool allocation logic
"""

def ip_to_int(ip):
    """Convert IP address string to 32-bit integer for numeric comparison."""
    parts = list(map(int, ip.split(".")))
    return (parts[0] << 24) + (parts[1] << 16) + (parts[2] << 8) + parts[3]


def int_to_ip(num):
    """Convert 32-bit integer back to IP address string."""
    return ".".join(str((num >> (8 * (3 - i))) & 255) for i in range(4))


def is_ip_in_pool(ip, pool_start, pool_end):
    """Check if an IP address is within the specified pool range."""
    ip_int = ip_to_int(ip)
    start_int = ip_to_int(pool_start)
    end_int = ip_to_int(pool_end)
    return start_int <= ip_int <= end_int


# Test 1: Basic IP conversion
print("Test 1: IP to integer conversion")
test_ip = "192.168.1.1"
test_int = ip_to_int(test_ip)
print(f"  IP: {test_ip} -> Integer: {test_int}")
assert test_int == 3232235777, f"Expected 3232235777, got {test_int}"
print("  ✓ Passed")

# Test 2: Integer to IP conversion
print("\nTest 2: Integer to IP conversion")
test_int = 3232235777
test_ip = int_to_ip(test_int)
print(f"  Integer: {test_int} -> IP: {test_ip}")
assert test_ip == "192.168.1.1", f"Expected 192.168.1.1, got {test_ip}"
print("  ✓ Passed")

# Test 3: IP in pool validation
print("\nTest 3: IP in pool validation")
pool_start = "10.97.235.100"
pool_end = "10.97.235.200"
test_ip1 = "10.97.235.150"
test_ip2 = "10.97.235.50"
test_ip3 = "10.97.235.250"
print(f"  Pool: {pool_start} - {pool_end}")
print(f"  IP {test_ip1} in pool: {is_ip_in_pool(test_ip1, pool_start, pool_end)}")
print(f"  IP {test_ip2} in pool: {is_ip_in_pool(test_ip2, pool_start, pool_end)}")
print(f"  IP {test_ip3} in pool: {is_ip_in_pool(test_ip3, pool_start, pool_end)}")
assert is_ip_in_pool(test_ip1, pool_start, pool_end) == True, "IP should be in pool"
assert is_ip_in_pool(test_ip2, pool_start, pool_end) == False, "IP should not be in pool"
assert is_ip_in_pool(test_ip3, pool_start, pool_end) == False, "IP should not be in pool"
print("  ✓ Passed")

# Test 4: Sequential IP allocation simulation
print("\nTest 4: Sequential IP allocation simulation")
pool_start = "10.97.235.100"
pool_end = "10.97.235.105"
assigned_ips = set()

# Simulate allocating 3 IPs
for i in range(3):
    current_ip_int = ip_to_int(pool_start)
    end_ip_int = ip_to_int(pool_end)

    while current_ip_int <= end_ip_int:
        current_ip = int_to_ip(current_ip_int)
        if current_ip not in assigned_ips:
            assigned_ips.add(current_ip)
            print(f"  Allocated IP {i+1}: {current_ip}")
            break
        current_ip_int += 1

print(f"  Total allocated IPs: {len(assigned_ips)}")
print(f"  Allocated IPs: {sorted(assigned_ips)}")
assert len(assigned_ips) == 3, f"Expected 3 allocated IPs, got {len(assigned_ips)}"
print("  ✓ Passed")

# Test 5: Pool exhaustion
print("\nTest 5: Pool exhaustion handling")
pool_start = "10.97.235.100"
pool_end = "10.97.235.102"
assigned_ips = set()

# Allocate all IPs in pool
for i in range(4):  # Try to allocate 4 IPs from a pool of 3
    current_ip_int = ip_to_int(pool_start)
    end_ip_int = ip_to_int(pool_end)
    allocated = False

    while current_ip_int <= end_ip_int:
        current_ip = int_to_ip(current_ip_int)
        if current_ip not in assigned_ips:
            assigned_ips.add(current_ip)
            print(f"  Allocated IP {i+1}: {current_ip}")
            allocated = True
            break
        current_ip_int += 1

    if not allocated:
        print(f"  Attempt {i+1}: No available IPs (pool exhausted)")

print(f"  Total allocated IPs: {len(assigned_ips)}")
assert len(assigned_ips) == 3, f"Expected 3 allocated IPs, got {len(assigned_ips)}"
print("  ✓ Passed")

print("\n" + "="*50)
print("All tests passed! ✓")
print("="*50)
