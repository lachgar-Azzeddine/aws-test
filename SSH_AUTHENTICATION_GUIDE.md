# SSH Authentication Guide - How Ansible Connects to VMs

**Purpose:** Understand how Ansible authenticates to VMs throughout the deployment lifecycle.

---

## 🎯 Quick Answer

**Ansible uses TWO authentication methods:**

1. **Password** (`devops/devops`) - Used ONCE during initial setup
2. **SSH Keys** - Used for ALL subsequent connections (secure & permanent)

**Why both?** New VMs need password auth initially, then we transition to SSH keys for security.

---

## 🔐 Complete Authentication Flow

### Phase 1: VM Creation (Cloud-Init) 🏗️

**What happens when VMs are provisioned:**

```yaml
# File: provisionnement-vms-*/files/cloud-init/userdata.yaml
hostname: "${vm_name}.${base_domain}"
ssh_pwauth: True   # ← Enables password authentication initially
```

**VM initial state:**
- ✅ User: `devops`
- ✅ Password: `devops` (hardcoded in cloud-init)
- ✅ SSH password authentication: **ENABLED**
- ❌ SSH keys: **NOT YET CONFIGURED**

**Why enable password auth?**
- Brand new VMs have no SSH keys yet
- Need some way to connect for first time
- Password provides bootstrap access

---

### Phase 2: Initial Ansible Connection (Password) 🔑

**Role:** `prepare-vms` (First role executed)

**How it connects:**

```python
# File: backend/project/roles/prepare-vms/prepare_inputs.py (lines 102-119)

inventory["RKE"]["hosts"][vm_name] = {
    "ansible_host": vm_ip,
    "ansible_user": "devops",
    "ansible_ssh_pass": "devops",  # ← Uses PASSWORD for first connection
}
```

**What happens:**
1. Ansible Runner executes `prepare-vms` role
2. Connects to each VM using username/password: `devops`/`devops`
3. This is the **ONLY time** password authentication is used
4. All VMs are fresh and have no SSH keys yet

**Connection command (conceptual):**
```bash
# Equivalent to:
sshpass -p 'devops' ssh devops@10.1.10.10
```

---

### Phase 3: SSH Key Setup (prepare-vms role) 🔐

**Now the `prepare-vms` role does the heavy lifting:**

#### Step 1: Read SSH Keys from Database

```python
# File: backend/project/roles/prepare-vms/prepare_inputs.py (lines 19-70)

def get_inputs(Session):
    security = get_security(Session)  # Query database

    # Get SSH keys uploaded by user via frontend
    ssh_public_key_string = security.ssh_pulic_key    # ← From database!
    ssh_private_key_string = security.ssh_private_key # ← From database!

    # Write to temp files for Ansible to use
    with tempfile.NamedTemporaryFile(delete=False, mode="w") as public_key_file:
        public_key_file.write(ssh_public_key_string)
        public_key_file_path = public_key_file.name

    with tempfile.NamedTemporaryFile(delete=False, mode="w") as private_key_file:
        private_key_file.write(ssh_private_key_string)
        private_key_file_path = private_key_file.name

    extra_vars = {
        "public_key_file_path": public_key_file_path,
        "private_key_file_path": private_key_file_path,
        # ...
    }

    return extra_vars, inventory
```

**Where SSH keys come from:**
```
User generates SSH key pair (ssh-keygen)
            ↓
User uploads via Frontend → Security settings
            ↓
Stored in PostgreSQL → security table
            ↓
prepare_inputs.py reads from database
            ↓
Writes to temp files for Ansible
```

#### Step 2: Ensure devops User Exists

```yaml
# File: backend/project/roles/prepare-vms/tasks/main.yml (lines 2-29)

- name: Ensure the devops user exists
  become: true
  user:
    name: devops
    home: /home/devops
    state: present
    create_home: yes

- name: Add devops user to sudoers
  become: true
  copy:
    dest: /etc/sudoers.d/devops
    content: "devops ALL=(ALL) NOPASSWD:ALL"  # ← No password needed for sudo
    owner: root
    group: root
    mode: '0440'

- name: Ensure home directory ownership is correct
  become: true
  file:
    path: /home/devops
    owner: devops
    group: devops
    state: directory
    mode: '0755'
```

#### Step 3: Create SSH Directory

```yaml
# File: backend/project/roles/prepare-vms/tasks/main.yml (lines 49-56)

- name: Ensure the remote user's .ssh directory exists
  file:
    path: /home/devops/.ssh
    state: directory
    mode: '0700'  # ← Secure permissions
  become: yes
  become_user: devops
```

#### Step 4: Copy SSH Public Key to VM 🔑

**THIS IS THE KEY STEP!**

```yaml
# File: backend/project/roles/prepare-vms/tasks/main.yml (lines 70-77)

- name: Copy the public key to the remote machine
  authorized_key:
    user: devops
    state: present
    key: "{{ lookup('file', public_key_file_path) }}"  # ← Reads from temp file
  become: yes
  become_user: devops
```

**What this does:**
```bash
# Equivalent to:
echo "ssh-rsa AAAAB3NzaC1yc2E..." >> /home/devops/.ssh/authorized_keys
chmod 600 /home/devops/.ssh/authorized_keys
```

**Result on VM:**
```bash
# /home/devops/.ssh/authorized_keys now contains:
ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAACAQDe... user@machine
```

---

### Phase 4: Disable Password Authentication 🔒

**Now that SSH keys are set up, DISABLE password auth for security:**

```yaml
# File: backend/project/roles/prepare-vms/tasks/main.yml (lines 96-124)

- name: Disable root SSH login and SSH password authentication
  become: true
  lineinfile:
    path: /etc/ssh/sshd_config
    state: present
    regexp: '^#?(PermitRootLogin|PasswordAuthentication)'
    line: "{{ item }}"
    backrefs: yes
  loop:
    - "PermitRootLogin no"           # ← Root can't login at all
    - "PasswordAuthentication no"     # ← Password auth DISABLED!

- name: Disable in cloud-init config too
  become: true
  copy:
    dest: /etc/ssh/sshd_config.d/50-cloud-init.conf
    content: |
      PermitRootLogin no
      PasswordAuthentication no
    force: yes

- name: Restart the SSHD service
  become: true
  service:
    name: sshd
    state: restarted  # ← Apply changes
```

**Result on VM:**
```bash
# /etc/ssh/sshd_config
PermitRootLogin no
PasswordAuthentication no

# SSH password authentication is now DISABLED
# Only SSH key authentication works
```

**Security improvements:**
- 🚫 Can't login with password anymore
- 🔐 Must have private key to connect
- 🔒 Root account disabled
- ✅ Brute-force attacks impossible

---

### Phase 5: All Subsequent Roles (SSH Keys Only) 🔐

**Every role AFTER prepare-vms uses SSH keys automatically:**

```python
# Example: backend/project/roles/install-argocd/prepare_inputs.py

def get_inputs(Session):
    vault_vm = get_vms_by_group("vault", Session)[0]

    inventory = {
        "all": {
            "hosts": {
                "vault_vm": {
                    "ansible_host": vault_vm.ip,
                    "ansible_user": "devops"
                    # ← No password specified!
                    # Ansible automatically uses SSH key
                }
            }
        }
    }

    return extra_vars, inventory
```

**How Ansible finds the private key:**
1. Backend container has private key from database
2. Written to `/home/devops/.ssh/id_rsa` (Ansible default location)
3. Ansible automatically uses it when connecting
4. VM checks `/home/devops/.ssh/authorized_keys` (has matching public key)
5. Connection succeeds! 🎉

**SSH handshake (simplified):**
```
Backend Container                      Remote VM
─────────────────                      ─────────
Has: Private key        →  SSH  →     Has: Public key
(/home/devops/.ssh/id_rsa)            (/home/devops/.ssh/authorized_keys)

                     ← Challenge →

Signs with private key → Response →   Verifies with public key

                     ← Success! →      Connection established
```

---

## 📊 Authentication Timeline Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│ PHASE 1: VM PROVISIONING                                            │
│ ─────────────────────────────────────────────────────────────────── │
│ Terraform + Cloud-Init creates VMs                                  │
│                                                                      │
│ VM State:                                                            │
│   • User: devops                                                     │
│   • Password: devops (temporary)                                     │
│   • SSH password auth: ENABLED                                       │
│   • SSH keys: NONE                                                   │
└─────────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────────┐
│ PHASE 2: FIRST ANSIBLE CONNECTION (prepare-vms role)                │
│ ─────────────────────────────────────────────────────────────────── │
│ Authentication: PASSWORD (devops/devops)                             │
│                                                                      │
│ Ansible inventory:                                                   │
│   ansible_user: devops                                               │
│   ansible_ssh_pass: devops  ← Uses password                         │
└─────────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────────┐
│ PHASE 3: SSH KEY SETUP (prepare-vms role continues)                 │
│ ─────────────────────────────────────────────────────────────────── │
│ 1. Read SSH keys from database (security table)                     │
│ 2. Create /home/devops/.ssh directory on VM                         │
│ 3. Copy public key → /home/devops/.ssh/authorized_keys              │
│ 4. Set proper permissions (700 for .ssh, 600 for authorized_keys)   │
└─────────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────────┐
│ PHASE 4: DISABLE PASSWORD AUTH (prepare-vms role continues)         │
│ ─────────────────────────────────────────────────────────────────── │
│ 1. Edit /etc/ssh/sshd_config                                        │
│    • PasswordAuthentication no                                       │
│    • PermitRootLogin no                                              │
│ 2. Restart SSH daemon                                                │
│                                                                      │
│ VM State NOW:                                                        │
│   • SSH password auth: DISABLED ✓                                    │
│   • SSH key auth: ENABLED ✓                                          │
│   • Root login: DISABLED ✓                                           │
└─────────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────────┐
│ PHASE 5: ALL OTHER ROLES (install-vault, install-argocd, etc.)      │
│ ─────────────────────────────────────────────────────────────────── │
│ Authentication: SSH KEYS ONLY                                        │
│                                                                      │
│ Ansible inventory:                                                   │
│   ansible_user: devops                                               │
│   (no password needed - automatic SSH key auth)                      │
│                                                                      │
│ Backend container:                                                   │
│   Private key: /home/devops/.ssh/id_rsa                             │
│                                                                      │
│ Remote VMs:                                                          │
│   Public key: /home/devops/.ssh/authorized_keys                     │
│                                                                      │
│ Connection: Secure, no passwords transmitted!                        │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 🔑 SSH Key Management

### Where SSH Keys Come From

**Method 1: User Generates Keys (Recommended)**

```bash
# On user's machine
ssh-keygen -t rsa -b 4096 -f ~/infra_deployment_key -N ""

# This creates:
# ~/infra_deployment_key       (private key - keep secret!)
# ~/infra_deployment_key.pub   (public key - safe to share)

# View keys
cat ~/infra_deployment_key.pub
cat ~/infra_deployment_key
```

**Method 2: Use Existing Keys**

```bash
# If you already have SSH keys
cat ~/.ssh/id_rsa.pub   # Public key
cat ~/.ssh/id_rsa       # Private key
```

### Upload to Platform

**Via Frontend (Security Settings page):**

1. Navigate to: `http://localhost/runner/` → Security Settings
2. Upload **Public Key**: Paste contents of `.pub` file
3. Upload **Private Key**: Paste contents of private key file
4. Click Save

**Stored in database:**

```sql
-- PostgreSQL: security table
CREATE TABLE security (
    id INTEGER PRIMARY KEY,
    ssh_pulic_key TEXT NOT NULL,      -- Public key content
    ssh_private_key TEXT NOT NULL,    -- Private key content
    ssh_private_key_pwd TEXT,         -- Password (if key is encrypted)
    -- ... other fields
);
```

### How Backend Uses Keys

```python
# In any prepare_inputs.py:
from repository import get_security

def get_inputs(Session):
    security = get_security(Session)

    # Get keys from database
    public_key = security.ssh_pulic_key
    private_key = security.ssh_private_key

    # Backend container writes private key to ~/.ssh/id_rsa
    # Ansible automatically uses it for connections
```

---

## 🛡️ Security Benefits

### Why Transition from Password to SSH Keys?

| Aspect | Password Auth | SSH Key Auth |
|--------|---------------|--------------|
| **Transmission** | ❌ Password sent over network (encrypted but visible in memory) | ✅ Private key never leaves backend |
| **Brute Force** | ⚠️ Vulnerable to brute force attacks | ✅ Impossible (would take billions of years) |
| **Credential Storage** | ⚠️ Password stored in inventory files | ✅ Only public key on VMs (useless to attackers) |
| **Rotation** | ⚠️ Must change password on all VMs | ✅ Just replace authorized_keys |
| **Audit Trail** | ⚠️ Limited logging | ✅ Key fingerprints logged |
| **Key Length** | ⚠️ Typically 8-20 characters | ✅ 4096-bit keys (cryptographically secure) |

### Security Improvements After prepare-vms

**Before (Initial State):**
```bash
# VM state after provisioning
✓ Password auth: ENABLED
✓ Root login: ENABLED (via cloud-init default)
✓ SSH keys: NONE
⚠️ Risk: Anyone with password can login
⚠️ Risk: Root account accessible
```

**After (Final State):**
```bash
# VM state after prepare-vms
✓ Password auth: DISABLED
✓ Root login: DISABLED
✓ SSH key auth: ENABLED
✓ Devops user: SUDO without password
✅ Secure: Only holders of private key can access
✅ Secure: Root account inaccessible
```

---

## 🐛 Known Issues & Fixes

### Issue 1: Hardcoded Password in install-gogs Role

**Problem:**

```python
# File: backend/project/roles/install-gogs/prepare_inputs.py (line 71)

inventory = {
    "all": {
        "hosts": {
            "gogs-target": {
                "ansible_host": gitops_vm.ip,
                "ansible_user": "devops",
                "ansible_ssh_pass": "devops"  # ❌ Shouldn't use password here!
            }
        }
    }
}
```

**Why it's harmless:**
- This role runs AFTER prepare-vms
- Password auth is already disabled on VMs
- Ansible will ignore the password and use SSH key

**But still should be fixed:**

```python
# CORRECTED:
inventory = {
    "all": {
        "hosts": {
            "gogs-target": {
                "ansible_host": gitops_vm.ip,
                "ansible_user": "devops"
                # ✅ No password - uses SSH key automatically
            }
        }
    }
}
```

### Issue 2: Default Password "devops" Hardcoded

**Problem:**
- Initial VM password is hardcoded as `devops/devops`
- Used during cloud-init provisioning
- Security risk if VMs are accessible before prepare-vms runs

**Mitigation:**
- Password auth is disabled quickly (within minutes)
- VMs typically on private network during provisioning
- prepare-vms is first role to run

**Better approach:**
- Generate random password during VM creation
- Store in Vault
- Use for initial connection
- Still disable after SSH keys set up

---

## 🧪 Testing SSH Authentication

### Test 1: Verify SSH Keys on Backend

```bash
# Enter backend container
docker exec -it backend bash

# Check if SSH keys exist
ls -la ~/.ssh/
# Should see: id_rsa (private) and id_rsa.pub (public)

# View public key
cat ~/.ssh/id_rsa.pub

# Test private key permissions
ls -l ~/.ssh/id_rsa
# Should be: -rw------- (600)
```

### Test 2: Verify SSH Keys on VMs

```bash
# SSH into a VM (after prepare-vms has run)
ssh devops@10.1.10.10

# Once on VM:
ls -la ~/.ssh/
# Should see: authorized_keys

# View authorized key
cat ~/.ssh/authorized_keys
# Should match public key from backend

# Check SSH config
sudo cat /etc/ssh/sshd_config | grep -E "PasswordAuthentication|PermitRootLogin"
# Should show:
# PasswordAuthentication no
# PermitRootLogin no
```

### Test 3: Verify Password Auth is Disabled

```bash
# Try to SSH with password (should FAIL)
ssh devops@10.1.10.10
# Should NOT prompt for password
# Should require SSH key

# Try with wrong key (should FAIL)
ssh -i /tmp/wrong_key devops@10.1.10.10
# Should fail: Permission denied (publickey)
```

---

## 📚 FAQ

### Q: What if I lose the SSH private key?

**A:** You'll lose access to VMs. You'd need to:
1. Access VMs via hypervisor console (VMware/Nutanix)
2. Manually add new SSH key to `~/.ssh/authorized_keys`
3. Or re-provision VMs

**Prevention:** Backup private key securely!

---

### Q: Can I use a password-protected SSH key?

**A:** Yes!

```bash
# Generate key WITH password
ssh-keygen -t rsa -b 4096 -f ~/key -N "MySecretPassphrase"
```

Upload via frontend and set `ssh_private_key_pwd` in Security table.

Ansible will prompt for passphrase when needed (or use ssh-agent).

---

### Q: Why not use password authentication for everything?

**A:** Security reasons:
- 🔐 SSH keys are much more secure (4096-bit vs. ~128-bit password)
- 🚫 Passwords can be brute-forced
- 📝 Passwords might be logged/leaked
- 🔑 SSH keys don't transmit secrets over network

---

### Q: What happens during prepare-vms if SSH fails?

**A:** Role will fail and stop deployment:
```
TASK [Copy the public key to the remote machine] ********
fatal: [vm-1]: UNREACHABLE! => SSH connection failed
```

**Common causes:**
- VM not accessible (network/firewall)
- Wrong password (not "devops")
- SSH service not running on VM

---

### Q: Can I use different SSH keys for different zones?

**A:** Currently no - same key pair used for all VMs.

**To implement:** Would need to modify:
1. Database: Add per-zone SSH keys
2. prepare_inputs.py: Load zone-specific keys
3. prepare-vms: Deploy correct key per zone

---

## 🎓 Summary

### Key Takeaways

1. **Two-phase authentication:**
   - Phase 1: Password (bootstrap, temporary)
   - Phase 2: SSH keys (production, permanent)

2. **SSH keys come from database:**
   - User uploads via frontend
   - Stored in security table
   - Deployed by prepare-vms role

3. **Security progression:**
   - Start: Password enabled (vulnerable)
   - End: Password disabled, SSH keys only (secure)

4. **prepare-vms is critical:**
   - First role to run
   - Sets up SSH keys
   - Hardens security
   - All other roles depend on it

### Authentication Flow Summary

```
VM Created → Password Auth → prepare-vms Role → SSH Keys Deployed → Password Disabled → All Other Roles
   (devops/devops)              (connects with password)      (copies public key)    (secure now!)    (use SSH keys)
```

---

## 🔗 Related Files

**Key files to understand:**
- `backend/project/roles/provisionnement-vms-*/files/cloud-init/userdata.yaml` - VM initialization
- `backend/project/roles/prepare-vms/prepare_inputs.py` - SSH key loading
- `backend/project/roles/prepare-vms/tasks/main.yml` - SSH setup tasks
- `backend/models.py` - Security table definition (line 93)
- `backend/repository.py` - `get_security()` function

---

**Now you understand exactly how Ansible authenticates to VMs! 🎉**

The platform uses a secure two-phase approach: bootstrap with passwords, then lock down with SSH keys.
