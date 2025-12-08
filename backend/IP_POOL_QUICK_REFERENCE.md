# IP Pool Quick Reference

## Key Functions

### `get_next_available_ip(zone_id, Session)`
**Purpose:** Get next free IP from zone's pool

**Returns:** Next available IP address (string)

**Raises:** Exception if pool is exhausted

**Example:**
```python
ip = get_next_available_ip(zone_id, Session)
print(f"Allocated: {ip}")
```

---

### `ip_to_int(ip)`
**Purpose:** Convert IP string to integer

**Example:**
```python
ip_to_int("192.168.1.1")  # Returns: 3232235777
```

---

### `int_to_ip(num)`
**Purpose:** Convert integer to IP string

**Example:**
```python
int_to_ip(3232235777)  # Returns: "192.168.1.1"
```

---

### `is_ip_in_pool(ip, start, end)`
**Purpose:** Check if IP is in range

**Returns:** True/False

**Example:**
```python
is_ip_in_pool("10.0.0.50", "10.0.0.1", "10.0.0.100")
# Returns: True
```

---

## Zone Creation

### Old Signature (Broken)
```python
add_zone(
    name="lan",
    sub_network="10.97.235.65",
    # ... other params ...
)
```

### New Signature (Required)
```python
add_zone(
    name="lan",
    sub_network="10.97.235.65",
    # ... other params ...
    ip_pool_start="10.97.235.100",  # REQUIRED
    ip_pool_end="10.97.235.200",    # REQUIRED
    Session=Session,
)
```

---

## Common Patterns

### Allocating Multiple IPs
```python
# Get 3 consecutive IPs from pool
ip1 = get_next_available_ip(zone.id, Session)
ip2 = get_next_available_ip(zone.id, Session)
ip3 = get_next_available_ip(zone.id, Session)

print(f"IPs: {ip1}, {ip2}, {ip3}")
# Output: 10.97.235.100, 10.97.235.101, 10.97.235.102
```

### Pool Exhaustion Handling
```python
try:
    ip = get_next_available_ip(zone.id, Session)
    # Use the IP...
except Exception as e:
    print(f"IP pool exhausted: {e}")
    # Handle error...
```

### Validating IP Pool
```python
# Check if IP is within zone's pool
zone = session.query(Zone).filter(Zone.id == zone_id).first()
if is_ip_in_pool(vm_ip, zone.ip_pool_start, zone.ip_pool_end):
    print("IP is valid")
else:
    print("IP is outside pool")
```

---

## Testing

### Run Test Suite
```bash
python3 test_ip_pool.py
```

### Expected Output
```
Test 1: IP to integer conversion
  ✓ Passed
Test 2: Integer to IP conversion
  ✓ Passed
Test 3: IP in pool validation
  ✓ Passed
Test 4: Sequential IP allocation simulation
  ✓ Passed
Test 5: Pool exhaustion handling
  ✓ Passed

All tests passed! ✓
```

---

## Migration Checklist

- [ ] Update all `add_zone()` calls to include `ip_pool_start` and `ip_pool_end`
- [ ] Update all `update_zone()` calls to include `ip_pool_start` and `ip_pool_end`
- [ ] Replace `increment_ip()` calls with `get_next_available_ip()`
- [ ] Run test suite: `python3 test_ip_pool.py`
- [ ] Verify syntax: `python3 -m py_compile models.py repository.py`

---

## Example Zone Configurations

### Development Environment
```python
add_zone(
    name="dev-lan",
    sub_network="192.168.100.0",
    network_mask=24,
    gateway="192.168.100.1",
    ip_pool_start="192.168.100.10",
    ip_pool_end="192.168.100.100",
    # ... other params ...
)
```

### Production Environment
```python
add_zone(
    name="prod-lan",
    sub_network="10.50.0.0",
    network_mask=16,
    gateway="10.50.0.1",
    ip_pool_start="10.50.100.1",
    ip_pool_end="10.50.200.254",
    # ... other params ...
)
```

### DMZ Zone
```python
add_zone(
    name="dmz",
    sub_network="172.16.0.0",
    network_mask=24,
    gateway="172.16.0.1",
    ip_pool_start="172.16.0.100",
    ip_pool_end="172.16.0.200",
    # ... other params ...
)
```

---

## Troubleshooting

### "Zone does not have IP pool configured"
**Cause:** Zone created without `ip_pool_start`/`ip_pool_end`

**Solution:**
```python
update_zone(
    id=zone_id,
    # ... existing params ...
    ip_pool_start="10.0.0.100",
    ip_pool_end="10.0.0.200",
    Session=Session,
)
```

### "No available IP addresses in zone"
**Cause:** IP pool is full

**Solution:**
- Expand the pool range
- Delete unused VMs
- Create additional zones

### TypeError: missing required arguments
**Cause:** Calling `add_zone()` or `update_zone()` without IP pool params

**Solution:** Add `ip_pool_start` and `ip_pool_end` to function call

---

## Quick Tips

1. **Pool Size:** Always reserve more IPs than current need
2. **Documentation:** Comment your IP pool ranges
3. **Segmentation:** Use different pools for different purposes
4. **Testing:** Run test suite after changes
5. **Validation:** Check IPs are in pool before allocation
