# VM Hostname Double Prefix Bug Fix

## Problem

Virtual machine hostnames were being prefixed twice with the environment prefix. For example, when `env_prefix="test"`, instead of getting `test-vault1`, the system was generating `test-test-vault1`.

## Root Cause

The issue occurred in multiple places where VM names were being concatenated with the environment prefix:

1. **Database (repository.py)** - The `scaffold_architecture` function generates VM names with the prefix already included
2. **Terraform (main.tf)** - The VM provisioning code was concatenating `machine_prefix` + VM name
3. **Cloud-Init (userdata.yaml)** - The hostname was being set using `machine_prefix` + VM name

Since the VM names in the database already included the prefix (e.g., "test-vault1"), the Terraform and cloud-init templates were adding it again, resulting in double prefixes.

## Solution

### 1. Terraform main.tf Files (3 files)

Fixed the VM name assignment in all three provisioning roles:

**Files:**
- `project/roles/provisionnement-vms-apps/files/main.tf` (line 73-81)
- `project/roles/provisionnement-vms-infra/files/main.tf` (line 73-81)
- `project/roles/provisionnement-vms-dmz/files/main.tf` (line 73-81)

**Change:**
```terraform
# Before (buggy):
name = "${var.machine_prefix}${var.machines[count.index].name}"

# After (fixed):
name = (
  # Check if machine_prefix is not empty and vm name starts with it
  var.machine_prefix != "" && substr(var.machines[count.index].name, 0, length(var.machine_prefix)) == var.machine_prefix
  # If yes, use the VM name as-is (already has prefix)
  ? var.machines[count.index].name
  # If no, prepend the prefix
  : "${var.machine_prefix}${var.machines[count.index].name}"
)
```

### 2. Cloud-Init Userdata Files (3 files)

Fixed the hostname assignment in all three cloud-init templates:

**Files:**
- `project/roles/provisionnement-vms-apps/files/cloud-init/userdata.yaml` (line 2)
- `project/roles/provisionnement-vms-infra/files/cloud-init/userdata.yaml` (line 2)
- `project/roles/provisionnement-vms-dmz/files/cloud-init/userdata.yaml` (line 2)

**Change:**
```yaml
# Before (buggy):
hostname: "${machine_prefix}${vm_name}.${base_domain}"

# After (fixed):
# Use VM name directly as it already includes the environment prefix
hostname: "${vm_name}.${base_domain}"
```

### 3. Database Code (repository.py)

The database code in `scaffold_architecture` (lines 3856-3867) already had a fix to prevent double prefixes when generating VM names. This fix checks if the hostname prefix from the map already starts with the environment prefix and strips it before adding it:

```python
# Strip any existing environment prefix from hostname_prefix to prevent duplication
base_hostname = hostname_prefix
if (
    prefix
    and prefix.endswith("-")
    and hostname_prefix.startswith(prefix)
):
    base_hostname = hostname_prefix[len(prefix) :]

hostname = f"{prefix}{base_hostname}{i}"
```

## Testing

A test suite was created in `test_hostname_fix.py` that validates the fix handles all scenarios correctly:

- Normal case: VM name without prefix + environment prefix
- Bug case: VM name already with prefix (the main fix scenario)
- Empty prefix cases
- Different prefix scenarios
- Edge cases (prefix in middle, partial matches, etc.)

All 18 main tests + 4 edge case tests pass successfully.

## Impact

This fix ensures that:
1. VM names in vSphere will not have duplicate prefixes
2. VM hostnames will be set correctly without duplicate prefixes
3. DNS records will point to the correct hostnames
4. All Ansible inventory and orchestration will use the correct hostnames

## Files Modified

1. `/project/roles/provisionnement-vms-apps/files/main.tf`
2. `/project/roles/provisionnement-vms-infra/files/main.tf`
3. `/project/roles/provisionnement-vms-dmz/files/main.tf`
4. `/project/roles/provisionnement-vms-apps/files/cloud-init/userdata.yaml`
5. `/project/roles/provisionnement-vms-infra/files/cloud-init/userdata.yaml`
6. `/project/roles/provisionnement-vms-dmz/files/cloud-init/userdata.yaml`

**Note:** The fix in `repository.py` was already present (lines 3856-3867), but the Terraform and cloud-init fixes were missing, which is where the actual VM provisioning happens.
