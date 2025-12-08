# Ansible Roles Audit Report - Genericization Issues

**Date:** 2025-12-04
**Audited:** 31 Ansible roles in `backend/project/roles/`

---

## Executive Summary

The Ansible roles have been audited for genericization. While most roles query configuration from the database (good practice), there are **several hardcoded values and client-specific references** that need to be addressed for the platform to be truly generic and reusable.

### Issues Severity:

- 🔴 **CRITICAL** (4 issues): Breaks functionality or requires immediate fix
- 🟡 **MEDIUM** (5 issues): Works but not generic, should be parameterized
- 🟢 **LOW** (3 issues): Cosmetic or test-only, low priority

---

## 🔴 CRITICAL ISSUES

### 1. Hardcoded Vault Mount Point "harmonisation"

**Impact:** HIGH - Prevents multi-tenant or renamed deployments

**Locations Found:**
```
backend/project/roles/install-argocd/tasks/main.yml
backend/project/roles/install-gogs/prepare_inputs.py
backend/project/roles/install-docker-registry/prepare_inputs.py (commented out)
backend/project/roles/install-vault/post_install.py
```

**Example (install-argocd/tasks/main.yml:line ~200):**
```yaml
docker exec -e VAULT_SKIP_VERIFY=true vault vault kv put harmonisation/argocd_apps username="admin" password="{{ ... }}"
```

**Example (install-gogs/prepare_inputs.py:line 45):**
```python
secret_response = client.secrets.kv.v2.read_secret_version(
    mount_point='harmonisation',  # ❌ Hardcoded!
    path='gogs/credentials'
)
```

**Recommendation:**
- Add `vault_mount_point` field to `Security` table in `models.py`
- Default value: `"harmonisation"` for backwards compatibility
- Update all roles to use: `mount_point=security.vault_mount_point`

---

### 2. Hardcoded Default Credentials

**Impact:** HIGH - Security risk, not production-ready

**Locations:**

| Role | File | Credential | Line |
|------|------|-----------|------|
| install-vault | post_install.py | `gogs_username = "devops"` / `gogs_password = "devops"` | 208-209 |
| install-vault | post_install.py | `apim_username = "admin"` / `apim_password = "admin"` | 220-221 |
| install-vault | post_install.py | `registry_user = "devops"` / `registry_password = "devops"` | 263-264 |
| install-vault | post_install.py | `rancher_user = "devops"` / `rancher_password = "devops"` | 274-275 |
| install-vault | post_install.py | `minio_user = "devops"` / `minio_password = "aq9rj9R1"` | 305-306 |
| install-vault | post_install.py | `keycloak_user = "admin_user"` / `keycloak_password = "Admin_Password"` | 343-344 |
| install-vault | post_install.py | `neuvector_user = "admin"` / `neuvector_password = "admin"` | 294-295 |
| install-docker-registry | prepare_inputs.py | `password = "devops"` | 92 |
| install-gogs | prepare_inputs.py | `ansible_ssh_pass: "devops"` | 71 |

**Recommendation:**
- Generate random passwords during installation
- Option 1: Use Python `secrets.token_urlsafe(16)` to generate secure passwords
- Option 2: Add password fields to Configuration/Security table (user-provided)
- Store all generated passwords in Vault immediately
- **Never use default passwords like "admin/admin" or "devops/devops"**

**Example Fix:**
```python
# Instead of:
gogs_username = "devops"
gogs_password = "devops"

# Do this:
import secrets
gogs_username = "devops"
gogs_password = secrets.token_urlsafe(16)  # Generates random password
```

---

### 3. Hardcoded Git Repository Name "harmonisation"

**Impact:** MEDIUM-HIGH - Prevents renaming or multi-instance deployments

**Locations:**
```
backend/project/roles/install-cert-manager/prepare_inputs.py:4
backend/project/roles/install-cert-manager/tasks/main.yml (multiple lines)
backend/project/roles/install-gravitee-dmz/tasks/main.yml
backend/project/roles/install-gravitee-lan/tasks/main.yml
backend/project/roles/install-gogs/tasks/main.yml
```

**Example (install-cert-manager/tasks/main.yml):**
```yaml
- name: Clone Harmonisation Repo
  shell:
    cmd: git clone https://{{ gogs_ip }}/devops/harmonisation.git  # ❌ Hardcoded!
    chdir: /tmp
```

**Example (install-gogs/tasks/main.yml):**
```yaml
- name: Create Gogs repository
  uri:
    url: "https://localhost/api/v1/admin/users/{{ admin_user }}/repos"
    body_format: json
    body:
      name: harmonisation  # ❌ Hardcoded!
```

**Recommendation:**
- Add `git_repository_name` field to `Security` table
- Default value: `"harmonisation"` for backwards compatibility
- Update all roles to use: `{{ git_repo_name }}` from variables

---

### 4. Client-Specific Function Calls (Removed Functions)

**Impact:** CRITICAL - **This will cause runtime errors!**

**Location:** `install-vault/post_install.py`

**Lines 3-8:**
```python
from repository import (
    get_server,        # ❌ REMOVED - doesn't exist!
    get_fcm,           # ❌ REMOVED - doesn't exist!
    get_facebook,      # ❌ REMOVED - doesn't exist!
    get_firebase_db,   # ❌ REMOVED - doesn't exist!
    get_google,        # ❌ REMOVED - doesn't exist!
    query_products,    # ❌ REMOVED - doesn't exist!
    ...
)
```

**Lines 32-38, 111-142:**
```python
products = query_products(Session)  # ❌ Function doesn't exist
for product in products:
    if product.name == "GCO":        # ❌ Product table removed
        install_gco = True
    if product.name == "EService":   # ❌ Product table removed
        install_eservice = True
```

**Lines 129-142:**
```python
google_captcha_secret = get_google(Session)[0].captcha_secret  # ❌ Function removed
facebook_app_secret = get_facebook(Session)[0].app_secret       # ❌ Function removed
login_eservice = get_server("auth", Session)[0].login           # ❌ Function removed
```

**Recommendation:**
🚨 **URGENT FIX REQUIRED** - This role will crash during execution!

**Solution:**
1. Remove all references to client-specific functions
2. Remove product-based conditional logic (`if install_eservice`, `if install_gco`)
3. Only store generic credentials (Gogs, Vault, Registry, MinIO, Keycloak, etc.)
4. Remove client-specific secrets (Google Captcha, Facebook, Firebase, etc.)

---

## 🟡 MEDIUM ISSUES

### 5. Hardcoded Ansible SSH Password

**Impact:** MEDIUM - Security risk, should use SSH keys

**Location:** `install-gogs/prepare_inputs.py:line 71`

```python
inventory = {
    "all": {
        "hosts": {
            "gogs-target": {
                "ansible_host": gitops_vm.ip,
                "ansible_user": "devops",
                "ansible_ssh_pass": "devops"  # ❌ Hardcoded password!
            },
```

**Recommendation:**
- Use SSH key authentication (already loaded from `security.ssh_pulic_key`)
- Remove `ansible_ssh_pass` entirely
- Rely on: `ansible_ssh_private_key_file`

---

### 6. Client-Specific API Keys and Credentials in Vault

**Impact:** MEDIUM - Not generic, client-specific

**Location:** `install-vault/post_install.py:lines 416-540`

**Client-Specific Secrets Stored:**
```python
# Line 416-422: DIGIRADEEJ API (Morocco-specific)
"DIGIRADEEJ_API_KEY": "3M2DG-6HJR8-X02GV-V8R4V-P6K27",
"DIGIRADEEJ_PARTNER_ID": "RADEEJ2025;R62935693078;R_TEST62935693078",

# Line 470-478: GCO Proxy (client-specific)
"username": base64.b64decode("R0NCT19VU0VSX0dDTw==").decode("utf-8"),
"password": base64.b64decode("UGFzKjIwMjA=").decode("utf-8"),

# Lines 481-527: Google, Facebook, Firebase secrets (client apps)
google_captcha_secret, google_client_secret, facebook_app_secret, etc.
```

**Recommendation:**
- Remove all client-specific API keys
- Keep only generic infrastructure credentials
- If needed, make these configurable via database

---

### 7. Organization Info in Certificate Generation (Commented Out)

**Impact:** LOW - Currently commented out, but should be parameterized

**Location:** `install-docker-registry/tasks/main.yml`

```yaml
#     -subj "/C=MA/ST=MA/L=MA/O=SRM-CS/OU=SRM/CN={{ docker_registry_url }}"
```

**Recommendation:**
- Add certificate fields to `Security` table:
  - `cert_country` (default: "US")
  - `cert_state` (default: "State")
  - `cert_org` (default: "Organization")
  - `cert_ou` (default: "IT")

---

### 8. README Content Hardcoded

**Impact:** LOW - Cosmetic only

**Location:** `install-gogs/tasks/main.yml`

```yaml
- name: Create README.md
  copy:
    dest: /tmp/harmonisation/README.md
    content: |
      # Harmonisation Repository  # ❌ Hardcoded project name
      This is the repository for harmonisation project.
```

**Recommendation:**
- Use `{{ git_repo_name }}` variable
- Or make it configurable via Security table

---

### 9. Admin Email Hardcoded

**Impact:** LOW - Not critical but should be configurable

**Location:** `install-gogs/defaults/main.yml`

```yaml
admin_email: admin@example.com  # ❌ Hardcoded
```

**Recommendation:**
- Add `admin_email` field to Security or Configuration table
- Pull from database in `prepare_inputs.py`

---

## 🟢 LOW PRIORITY ISSUES

### 10. Test/Example Roles with Hardcoded IPs

**Impact:** LOW - These are test roles only

**Locations:**
- `install-bastion/prepare_inputs.py` (192.168.1.10, 192.168.1.11)
- `install-seald/prepare_inputs.py` (192.168.1.10, 192.168.1.11)
- `testrole/prepare_inputs.py` (192.168.1.10, 192.168.1.11)
- `testrolefailed/prepare_inputs.py` (192.168.1.10, 192.168.1.11)

**Recommendation:**
- These are test/example roles
- Either delete them or clearly mark as templates/examples
- If keeping, add comment: `# Example only - replace with actual VMs from database`

---

### 11. Commented Out Legacy Code

**Impact:** LOW - Code hygiene issue

**Locations:**
- `install-docker-registry/prepare_inputs.py` (lines with vault read - commented)
- `provisionnement-vms-*/defaults/main.yml` (commented examples)

**Recommendation:**
- Clean up commented code
- Remove if not needed, or add comment explaining why it's kept

---

### 12. Hardcoded IPs in Comments/Examples

**Impact:** NONE - Comments only

**Locations:**
- `install-rke2-apps/tasks/main.yml`: `# delegate_to: 10.97.235.5`
- `provisionnement-vms-*/defaults/main.yml`: `# vsphere_host: "Dev_Environnement/10.97.97.10"`

**Recommendation:**
- Keep as examples or remove
- No functional impact

---

## Summary of Required Fixes

### Immediate Action Required (CRITICAL):

1. **Fix `install-vault/post_install.py`**:
   - Remove imports of non-existent functions (`get_server`, `get_fcm`, etc.)
   - Remove product-based logic (`query_products`, `install_eservice`, `install_gco`)
   - Remove client-specific secrets (Google, Facebook, Firebase, DIGIRADEEJ, etc.)
   - Keep only generic infrastructure credentials

2. **Parameterize Vault mount point**:
   - Add to database (Security table)
   - Update all roles to use variable

3. **Generate secure passwords**:
   - Replace all "devops"/"admin" defaults with generated passwords
   - Store in Vault

4. **Parameterize Git repository name**:
   - Add to database (Security table)
   - Update all clone/create commands

### Recommended Improvements (MEDIUM):

5. Remove hardcoded SSH password in install-gogs
6. Parameterize certificate organization info
7. Parameterize admin email

### Optional (LOW):

8. Clean up test roles or mark as examples
9. Remove commented legacy code
10. Clean up example IPs in comments

---

## Database Schema Changes Required

### Add to `Security` table (models.py):

```python
class Security(Base):
    __tablename__ = "security"
    # ... existing fields ...

    # NEW FIELDS:
    vault_mount_point = Column(String, nullable=False, default="harmonisation")
    git_repository_name = Column(String, nullable=False, default="harmonisation")
    admin_email = Column(String, nullable=False, default="admin@example.com")

    # Optional certificate fields:
    cert_country = Column(String, nullable=False, default="US")
    cert_state = Column(String, nullable=False, default="State")
    cert_organization = Column(String, nullable=False, default="Organization")
    cert_org_unit = Column(String, nullable=False, default="IT")
```

---

## Example Fix - install-vault/post_install.py

**BEFORE (BROKEN):**
```python
from repository import (
    get_server,        # ❌ Doesn't exist!
    get_fcm,           # ❌ Doesn't exist!
    query_products,    # ❌ Doesn't exist!
    ...
)

products = query_products(Session)  # ❌ Crash!
```

**AFTER (FIXED):**
```python
from repository import (
    get_security,
    get_vms_by_group,
    add_vault_keys,
    add_vault_token,
    get_vault_token,
    get_databases,
    get_ldaps,
    get_sms_providers,
    clear_vault_table,
)
import secrets

def post_install(Session):
    security = get_security(Session)
    vault_mount = security.vault_mount_point  # ✅ From database

    # Generate secure passwords
    gogs_password = secrets.token_urlsafe(16)  # ✅ Random
    registry_password = secrets.token_urlsafe(16)  # ✅ Random
    rancher_password = secrets.token_urlsafe(16)  # ✅ Random

    # Store only generic infrastructure credentials
    client.secrets.kv.v2.create_or_update_secret(
        mount_point=vault_mount,  # ✅ Parameterized
        path="gogs/credentials",
        secret={"username": "devops", "password": gogs_password},
    )

    # ❌ REMOVE all client-specific secrets:
    # - Google Captcha
    # - Facebook
    # - Firebase
    # - DIGIRADEEJ
    # - GCO-specific secrets
```

---

## Testing Checklist

After fixes, verify:

- [ ] `install-vault/post_install.py` runs without import errors
- [ ] All roles execute successfully
- [ ] Passwords are randomly generated (not "devops"/"admin")
- [ ] Vault mount point is read from database
- [ ] Git repository name is read from database
- [ ] No client-specific secrets are stored
- [ ] No references to removed Product table
- [ ] No references to removed get_server/get_fcm/etc. functions

---

## Conclusion

**Current Status:** ⚠️ **NOT FULLY GENERIC**

The roles are mostly well-structured and use database configuration correctly. However, there are **critical issues** that will cause runtime failures (removed function calls) and **security concerns** (hardcoded passwords).

**Priority:**
1. Fix `install-vault/post_install.py` immediately (CRITICAL - will crash)
2. Parameterize hardcoded values (MEDIUM)
3. Generate secure passwords (HIGH)
4. Clean up test roles (LOW)

**Estimated effort:**
- Critical fixes: 2-4 hours
- Medium improvements: 4-6 hours
- Low priority cleanup: 1-2 hours

---

**Report prepared by:** Claude Code Audit System
**Next review:** After implementing fixes
