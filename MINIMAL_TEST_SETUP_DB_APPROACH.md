# Minimal Test Setup - Database Seeding Approach (Recommended)

**Purpose:** Configure 5-VM minimal setup by modifying the database seeding function instead of replacing core business logic.

**Why This Approach is Better:**
- ✅ **Non-invasive** - Doesn't modify core business logic
- ✅ **Database-driven** - Follows the platform's architecture
- ✅ **Reversible** - Easy to revert by re-running seed function
- ✅ **Proper pattern** - Uses existing database seeding mechanism

---

## 🎯 Target: 5 VMs

```
LAN_APPS Zone (3 VMs):
├── rkeapp-master1   (1 master)
├── rkeapp-worker1   (worker)
└── rkeapp-worker2   (worker)

LAN_INFRA Zone (2 VMs):
├── vault1           (Vault)
└── gitops1          (Registry + ArgoCD + Gogs)
```

---

## 📊 How It Works

### The Three-Layer Flow

```
1. seed_vm_configurations(Session)
   └─> Inserts data into vm_configurations table
        (VM templates for different user counts)

2. get_vm_configurations(user_count, Session)
   └─> Queries vm_configurations table
        Returns templates for specified user_count

3. scaffold_architecture(Session)
   └─> Uses templates from get_vm_configurations()
        Creates actual VMs in virtual_machines table
```

**What we modify:** Only step 1 (seed_vm_configurations)
**What stays unchanged:** Steps 2 & 3

---

## 🔍 Understanding seed_vm_configurations()

**Location:** `backend/repository.py` - Line 2083

**What it does:**
- Seeds the `vm_configurations` table with predefined VM templates
- Creates configurations for multiple user counts: 100, 500, 1000, 10000
- Each configuration defines: VM type, count, CPU, RAM, disk sizes, roles

**Current behavior for 100 users:**
- RKEAPPS_CONTROL: 3 VMs (master,worker,cns)
- RKEMIDDLEWARE_CONTROL: 3 VMs
- RKEDMZ: 3 VMs
- LBLAN, LBDMZ, LBINTEGRATION: 2 VMs each
- GITOPS, MONITORING, VAULT: 1 VM each
- **Total: ~18 VMs**

**Target behavior for 100 users:**
- RKEAPPS_CONTROL: 1 VM (master only)
- RKEAPPS_WORKER: 2 VMs (workers)
- VAULT: 1 VM
- GITOPS: 1 VM
- **Everything else: 0 VMs**
- **Total: 5 VMs**

---

## ✏️ The Modification

### File to Edit

**`backend/repository.py`**

### Find the Section

Search for: `# Configuration for 100 users` (around line 2107)

You'll see:
```python
# Configuration for 100 users
configs_100 = [
    # RKEAPPS - Control Plane (3 master nodes with combined roles)
    {
        "user_count": 100,
        "vm_type": "RKEAPPS_CONTROL",
        "node_count": 3,  # ← Currently 3 VMs
        # ...
    },
    # ... many more configs
]
```

### Replace configs_100 List

**Replace the entire `configs_100` list with this minimal configuration:**

```python
# Configuration for 100 users - MINIMAL TEST SETUP
configs_100 = [
    # ================================================================
    # RKE2 KUBERNETES CLUSTER - 3 VMs TOTAL
    # ================================================================

    # RKE2 Master Node (1 VM instead of 3)
    {
        "user_count": 100,
        "vm_type": "RKEAPPS_CONTROL",
        "node_count": 1,           # ← Changed from 3 to 1
        "cpu_per_node": 4,
        "ram_per_node": 8192,
        "os_disk_size": 100,
        "data_disk_size": 50,
        "roles": "master,etcd,controlplane",  # Master roles only
    },

    # RKE2 Worker Nodes (2 VMs)
    {
        "user_count": 100,
        "vm_type": "RKEAPPS_WORKER",
        "node_count": 2,           # ← Changed from 0 to 2
        "cpu_per_node": 4,
        "ram_per_node": 8192,
        "os_disk_size": 100,
        "data_disk_size": 50,
        "roles": "worker",
    },

    # CNS Nodes - DISABLED for minimal setup
    {
        "user_count": 100,
        "vm_type": "RKEAPPS_CNS",
        "node_count": 0,           # ← Stays at 0
        "cpu_per_node": 4,
        "ram_per_node": 8192,
        "os_disk_size": 80,
        "data_disk_size": 0,
        "roles": "worker,cns",
    },

    # ================================================================
    # MIDDLEWARE CLUSTER - DISABLED (0 VMs)
    # ================================================================

    {
        "user_count": 100,
        "vm_type": "RKEMIDDLEWARE_CONTROL",
        "node_count": 0,           # ← Changed from 3 to 0
        "cpu_per_node": 4,
        "ram_per_node": 8192,
        "os_disk_size": 80,
        "data_disk_size": 0,
        "roles": "master,worker,cns",
    },

    {
        "user_count": 100,
        "vm_type": "RKEMIDDLEWARE_CNS",
        "node_count": 0,           # ← Stays at 0
        "cpu_per_node": 4,
        "ram_per_node": 8192,
        "os_disk_size": 80,
        "data_disk_size": 0,
        "roles": "worker,cns",
    },

    {
        "user_count": 100,
        "vm_type": "RKEMIDDLEWARE_WORKER",
        "node_count": 0,           # ← Stays at 0
        "cpu_per_node": 4,
        "ram_per_node": 8192,
        "os_disk_size": 80,
        "data_disk_size": 0,
        "roles": "worker",
    },

    # ================================================================
    # DMZ CLUSTER - DISABLED (0 VMs)
    # ================================================================

    {
        "user_count": 100,
        "vm_type": "RKEDMZ",
        "node_count": 0,           # ← Changed from 3 to 0
        "cpu_per_node": 4,
        "ram_per_node": 4096,
        "os_disk_size": 80,
        "data_disk_size": 0,
        "roles": "master,worker,cns",
    },

    # ================================================================
    # LOAD BALANCERS - DISABLED (0 VMs)
    # ================================================================

    {
        "user_count": 100,
        "vm_type": "LBLAN",
        "node_count": 0,           # ← Changed from 2 to 0
        "cpu_per_node": 2,
        "ram_per_node": 2048,
        "os_disk_size": 60,
        "data_disk_size": 0,
        "roles": "loadbalancer",
    },

    {
        "user_count": 100,
        "vm_type": "LBDMZ",
        "node_count": 0,           # ← Changed from 2 to 0
        "cpu_per_node": 2,
        "ram_per_node": 2048,
        "os_disk_size": 60,
        "data_disk_size": 0,
        "roles": "loadbalancer",
    },

    {
        "user_count": 100,
        "vm_type": "LBINTEGRATION",
        "node_count": 0,           # ← Changed from 2 to 0
        "cpu_per_node": 2,
        "ram_per_node": 2048,
        "os_disk_size": 60,
        "data_disk_size": 0,
        "roles": "loadbalancer",
    },

    # ================================================================
    # INFRASTRUCTURE SERVICES - 2 VMs TOTAL
    # ================================================================

    # GitOps VM (Registry + ArgoCD + Gogs combined)
    {
        "user_count": 100,
        "vm_type": "GITOPS",
        "node_count": 1,           # ← Stays at 1
        "cpu_per_node": 4,
        "ram_per_node": 8192,
        "os_disk_size": 100,
        "data_disk_size": 100,
        "roles": "gogs,docker-registry,argocd",  # ← Added argocd
    },

    # Monitoring - DISABLED for minimal setup
    {
        "user_count": 100,
        "vm_type": "MONITORING",
        "node_count": 0,           # ← Changed from 1 to 0
        "cpu_per_node": 4,
        "ram_per_node": 16384,
        "os_disk_size": 60,
        "data_disk_size": 0,
        "roles": "admin,monitoring",
    },

    # Vault VM
    {
        "user_count": 100,
        "vm_type": "VAULT",
        "node_count": 1,           # ← Stays at 1
        "cpu_per_node": 2,         # ← Reduced from 4 to 2
        "ram_per_node": 4096,      # ← Reduced from 16384 to 4096
        "os_disk_size": 50,
        "data_disk_size": 20,
        "roles": "vault,docker",
    },
]
```

---

## 📝 Key Changes Explained

### What Changed

| VM Type | Original | Modified | Reason |
|---------|----------|----------|--------|
| **RKEAPPS_CONTROL** | 3 VMs | **1 VM** | Single master for testing |
| **RKEAPPS_WORKER** | 0 VMs | **2 VMs** | Need worker nodes |
| **RKEMIDDLEWARE_CONTROL** | 3 VMs | **0 VMs** | Not needed for minimal setup |
| **RKEDMZ** | 3 VMs | **0 VMs** | No DMZ for testing |
| **LBLAN/LBDMZ/LBINTEGRATION** | 2 VMs each | **0 VMs** | No load balancers needed |
| **MONITORING** | 1 VM | **0 VM** | Not essential for basic testing |
| **VAULT** | 1 VM (4 CPU, 16GB) | **1 VM (2 CPU, 4GB)** | Reduced resources |
| **GITOPS** | 1 VM | **1 VM + ArgoCD role** | Combined services |

**Total VMs: 18 → 5**

### GITOPS Role Addition

Notice we added `argocd` to the GITOPS roles:
```python
"roles": "gogs,docker-registry,argocd",  # ← argocd added
```

This combines three services on one VM:
- **Gogs**: Git server
- **Docker Registry**: Container image storage
- **ArgoCD**: GitOps deployment

---

## 📋 Step-by-Step Implementation

### Step 1: Backup Original File

```bash
cd backend
cp repository.py repository.py.backup
```

### Step 2: Edit repository.py

**Option A: Using VS Code**
```bash
code repository.py
```

**Option B: Using nano**
```bash
nano repository.py
```

**Option C: Using vim**
```bash
vim repository.py
```

### Step 3: Find and Replace

1. **Search for:** `# Configuration for 100 users` (line ~2107)

2. **Select entire `configs_100` list** (from `configs_100 = [` to the closing `]` before `configs_500`)

3. **Replace with** the minimal configuration above

### Step 4: Save and Verify Syntax

```bash
# Check Python syntax
python3 -m py_compile repository.py

# If no errors, you'll see no output
# If errors, you'll see detailed error messages
```

### Step 5: Clear Existing Database Data

```bash
# Access PostgreSQL
docker exec -it postgres psql -U harmonisation

# Clear VM configurations table
DELETE FROM vm_configurations WHERE user_count = 100;

# Exit
\q
```

### Step 6: Restart Backend and Re-seed

```bash
# Restart backend container
cd ..
docker compose restart backend

# Wait for backend to start
sleep 10

# Check logs
docker logs backend --tail 50
```

### Step 7: Re-populate Database

**Option A: Via Python (inside container)**
```bash
docker exec -it backend bash

# Inside container
python3 << EOF
from repository import get_session, seed_vm_configurations

_, Session = get_session()
seed_vm_configurations(Session)
print("VM configurations seeded successfully!")
EOF

exit
```

**Option B: Via API (if endpoint exists)**
```bash
# Check if API has seed endpoint
curl -X POST http://localhost/runner/api/seed-configurations
```

---

## 🧪 Testing Your Changes

### Test 1: Verify Database Has New Configs

```bash
docker exec -it postgres psql -U harmonisation

# Query VM configurations for 100 users
SELECT vm_type, node_count, cpu_per_node, ram_per_node, roles
FROM vm_configurations
WHERE user_count = 100
ORDER BY vm_type;

# Expected output:
# GITOPS              | 1 | 4 | 8192  | gogs,docker-registry,argocd
# LBLAN               | 0 | 2 | 2048  | loadbalancer
# LBDMZ               | 0 | 2 | 2048  | loadbalancer
# LBINTEGRATION       | 0 | 2 | 2048  | loadbalancer
# MONITORING          | 0 | 4 | 16384 | admin,monitoring
# RKEAPPS_CNS         | 0 | 4 | 8192  | worker,cns
# RKEAPPS_CONTROL     | 1 | 4 | 8192  | master,etcd,controlplane
# RKEAPPS_WORKER      | 2 | 4 | 8192  | worker
# RKEDMZ              | 0 | 4 | 4096  | master,worker,cns
# RKEMIDDLEWARE_CNS   | 0 | 4 | 8192  | worker,cns
# RKEMIDDLEWARE_CONTROL | 0 | 4 | 8192 | master,worker,cns
# RKEMIDDLEWARE_WORKER | 0 | 4 | 8192 | worker
# VAULT               | 1 | 2 | 4096  | vault,docker

\q
```

**Key things to verify:**
- RKEAPPS_CONTROL: node_count = **1** (not 3)
- RKEAPPS_WORKER: node_count = **2** (not 0)
- RKEMIDDLEWARE_CONTROL: node_count = **0** (not 3)
- RKEDMZ: node_count = **0** (not 3)
- LBLAN/LBDMZ/LBINTEGRATION: node_count = **0** (not 2)

### Test 2: Configure Frontend for 100 Users

```bash
# Set user count to 100 via API
curl -X PUT http://localhost/runner/api/configuration/concurrent-users \
  -H "Content-Type: application/json" \
  -d '{"number": 100}'
```

Or via frontend: Set "Number of Concurrent Users" to **100**

### Test 3: Generate VMs

```bash
# Trigger VM scaffolding
curl http://localhost/runner/api/virtual-machines
```

Or via frontend: Click "Generate VMs" or "View Virtual Machines"

### Test 4: Verify Only 5 VMs Generated

```bash
# Count VMs
curl -s http://localhost/runner/api/virtual-machines | jq 'length'

# Expected output: 5
```

### Test 5: Check VM Details

```bash
# Pretty print all VMs
curl -s http://localhost/runner/api/virtual-machines | jq '.[] | {hostname, ip, group, roles, cpu: .nb_cpu, ram}'
```

**Expected output:**
```json
{
  "hostname": "rkeapp-master1",
  "ip": "10.1.20.10",
  "group": "RKEAPPS",
  "roles": "master,etcd,controlplane",
  "cpu": 4,
  "ram": 8192
}
{
  "hostname": "rkeapp-worker1",
  "ip": "10.1.20.11",
  "group": "RKEAPPS_WORKER",
  "roles": "worker",
  "cpu": 4,
  "ram": 8192
}
{
  "hostname": "rkeapp-worker2",
  "ip": "10.1.20.12",
  "group": "RKEAPPS_WORKER",
  "roles": "worker",
  "cpu": 4,
  "ram": 8192
}
{
  "hostname": "vault1",
  "ip": "10.1.10.10",
  "group": "vault",
  "roles": "vault,docker",
  "cpu": 2,
  "ram": 4096
}
{
  "hostname": "gitops1",
  "ip": "10.1.10.11",
  "group": "gitops",
  "roles": "gogs,docker-registry,argocd",
  "cpu": 4,
  "ram": 8192
}
```

---

## 🔧 Adjusting the Configuration

### Change Worker Count

Want 3 workers instead of 2?

```python
{
    "user_count": 100,
    "vm_type": "RKEAPPS_WORKER",
    "node_count": 3,           # ← Change to 3
    "cpu_per_node": 4,
    "ram_per_node": 8192,
    "os_disk_size": 100,
    "data_disk_size": 50,
    "roles": "worker",
},
```

Re-run steps 5-7 to apply changes.

### Re-enable Monitoring

Want monitoring VM back?

```python
{
    "user_count": 100,
    "vm_type": "MONITORING",
    "node_count": 1,           # ← Change from 0 to 1
    "cpu_per_node": 4,
    "ram_per_node": 8192,      # ← Can reduce from 16384
    "os_disk_size": 60,
    "data_disk_size": 100,
    "roles": "admin,monitoring",
},
```

### Separate ArgoCD from GitOps

Want ArgoCD on separate VM?

**Option 1: Modify GITOPS to remove argocd**
```python
{
    "user_count": 100,
    "vm_type": "GITOPS",
    "node_count": 1,
    "cpu_per_node": 2,         # ← Reduce resources
    "ram_per_node": 4096,
    "os_disk_size": 50,
    "data_disk_size": 50,
    "roles": "gogs,docker-registry",  # ← Removed argocd
},
```

**Option 2: Create new ARGOCD config**
```python
# Add this new config
{
    "user_count": 100,
    "vm_type": "ARGOCD",
    "node_count": 1,
    "cpu_per_node": 2,
    "ram_per_node": 4096,
    "os_disk_size": 50,
    "data_disk_size": 20,
    "roles": "argocd",
},
```

**Note:** You'll also need to add ARGOCD to the `zone_map` in `scaffold_architecture()` function:
```python
zone_map = {
    # ... existing mappings
    "ARGOCD": zone_infra,  # ← Add this
    # ...
}
```

---

## 🚦 Ansible Roles Compatibility

### ✅ Roles That Will Work

| Role | Target VMs | Status |
|------|-----------|--------|
| `provisionnement-vms-infra` | vault1, gitops1 | ✅ Works |
| `provisionnement-vms-apps` | 3 RKE2 VMs | ✅ Works |
| `prepare-vms` | All 5 VMs | ✅ Works |
| `install-vault` | vault1 | ✅ Works |
| `install-docker-registry` | gitops1 | ✅ Works |
| `install-gogs` | gitops1 | ✅ Works |
| `install-argocd` | gitops1 | ✅ Works |
| `install-rke2-apps` | 3 RKE2 VMs | ✅ Works |
| `install-cert-manager` | K8s cluster | ✅ Works |
| `install-longhorn` | K8s cluster | ✅ Works |

### ❌ Roles That Will Fail/Skip

| Role | Reason |
|------|--------|
| `provisionnement-vms-dmz` | No DMZ VMs (node_count=0) |
| `install-rke2-middleware` | No middleware VMs |
| `install-rke2-dmz` | No DMZ VMs |
| `install-load-balancer` | No LB VMs |
| `install-monitoring` | No monitoring VM |
| `install-kafka` | Needs middleware cluster |
| `install-keycloak` | Needs middleware cluster |
| `install-minio` | Needs middleware cluster |

**Solution:** Comment out failed roles in `backend/install.py`:

```python
noinf_roles = [
    "provisionnement-vms-infra",
    "provisionnement-vms-apps",
    # "provisionnement-vms-dmz",        # ← Comment out
    "prepare-vms",
    "install-vault",
    "install-docker-registry",
    "install-gogs",
    "install-argocd",
    "install-rke2-apps",
    # "install-rke2-middleware",        # ← Comment out
    # "install-rke2-dmz",               # ← Comment out
    "install-cert-manager",
    "install-longhorn",
    # "install-load-balancer",          # ← Comment out
    # "install-monitoring",             # ← Comment out
    # "install-kafka",                  # ← Comment out
    # "install-keycloak",               # ← Comment out
    # "install-minio",                  # ← Comment out
]
```

---

## 🐛 Troubleshooting

### Issue 1: "VMConfiguration table already has records"

**Symptom:**
```bash
docker logs backend
# Shows: "VMConfiguration table already has 13 records. Skipping seed."
```

**Cause:**
The `seed_vm_configurations()` function only runs if table is empty.

**Solution:**
```bash
# Clear the table first
docker exec -it postgres psql -U harmonisation -c \
  "DELETE FROM vm_configurations WHERE user_count = 100;"

# Then re-run seed (step 7)
```

**Alternative - Force re-seed by modifying code temporarily:**
```python
# In seed_vm_configurations() around line 2098
# Comment out this check:
# if existing_count > 0:
#     print(f"VMConfiguration table already has {existing_count} records. Skipping seed.")
#     session.close()
#     return
```

### Issue 2: Still Getting 18+ VMs

**Symptom:**
```bash
curl -s http://localhost/runner/api/virtual-machines | jq 'length'
# Output: 18
```

**Possible causes:**

1. **Database not updated:**
```bash
# Verify database configs
docker exec -it postgres psql -U harmonisation -c \
  "SELECT vm_type, node_count FROM vm_configurations WHERE user_count = 100;"

# If still showing old values (3, 3, 2, etc.), re-run step 5-7
```

2. **Wrong user count:**
```bash
# Check configuration
curl http://localhost/runner/api/configuration | jq '.number_concurrent_users'

# If not 100, update it:
curl -X PUT http://localhost/runner/api/configuration/concurrent-users \
  -H "Content-Type: application/json" \
  -d '{"number": 100}'
```

3. **Old VMs cached:**
```bash
# Delete old VMs
docker exec -it postgres psql -U harmonisation -c \
  "DELETE FROM virtual_machines;"

# Regenerate
curl http://localhost/runner/api/virtual-machines
```

### Issue 3: Backend Won't Start After Editing

**Symptom:**
```bash
docker logs backend
# Shows Python syntax errors
```

**Solution:**
```bash
# Check syntax
cd backend
python3 -m py_compile repository.py

# If errors, restore backup
cp repository.py.backup repository.py

# Review your changes for:
# - Missing commas between dictionary items
# - Unmatched quotes or brackets
# - Incorrect indentation
```

### Issue 4: Seed Function Not Running

**Symptom:**
```bash
# Database still empty after running seed
docker exec -it postgres psql -U harmonisation -c \
  "SELECT COUNT(*) FROM vm_configurations WHERE user_count = 100;"
# Output: 0
```

**Solution:**

Check if `populate_db_fake_data()` is being called. This function calls `seed_vm_configurations()`:

```python
# repository.py line 3448
def populate_db_fake_data(Session):
    # Seed VM configurations first
    seed_vm_configurations(Session)  # ← This line must be present
    # ...
```

**Manual seed via Python:**
```bash
docker exec -it backend bash

python3 << 'EOF'
from repository import get_session, seed_vm_configurations

_, Session = get_session()
seed_vm_configurations(Session)
print("Seeding complete!")
EOF
```

---

## 🔄 Reverting to Original

### Quick Restore

```bash
# Stop backend
docker compose stop backend

# Restore from backup
cp backend/repository.py.backup backend/repository.py

# Clear database
docker exec -it postgres psql -U harmonisation -c \
  "DELETE FROM vm_configurations WHERE user_count = 100;"

# Start backend
docker compose start backend

# Wait 10 seconds
sleep 10

# Re-seed with original configs
docker exec -it backend python3 -c \
  "from repository import get_session, seed_vm_configurations; \
   _, Session = get_session(); \
   seed_vm_configurations(Session)"

# Verify
docker exec -it postgres psql -U harmonisation -c \
  "SELECT vm_type, node_count FROM vm_configurations WHERE user_count = 100;"
```

---

## 📚 Summary

### What You Modified

**File:** `backend/repository.py`
**Function:** `seed_vm_configurations()` (line ~2083)
**Section:** `configs_100` list (line ~2107)
**Change:** Modified VM templates for user_count=100

### Core Functions (Unchanged)

✅ `get_vm_configurations()` - Still queries database
✅ `scaffold_architecture()` - Still generates VMs from database
✅ Database-driven architecture - Fully preserved

### Benefits of This Approach

✅ **Proper architecture** - Uses database as single source of truth
✅ **Non-invasive** - No changes to business logic
✅ **Reversible** - Just re-seed database to revert
✅ **Scalable** - Can create configs for 500, 1000+ users too
✅ **Maintainable** - Changes are data, not code

### Comparison: This Approach vs Function Replacement

| Aspect | Database Approach (This Guide) | Function Replacement (Old) |
|--------|-------------------------------|---------------------------|
| **Modifies core logic** | ❌ No | ✅ Yes |
| **Database-driven** | ✅ Yes | ❌ No |
| **Reversible** | ✅ Easy (re-seed) | ⚠️ Harder (restore code) |
| **Follows platform design** | ✅ Yes | ❌ No |
| **Production-ready** | ✅ Could be | ❌ Never |
| **Risk** | 🟢 Low | 🟡 Medium |

---

## 🎓 Next Steps

After successfully seeding minimal configuration:

1. **✅ Verify database** (Test 1)
2. **✅ Set user count to 100** (Test 2)
3. **✅ Generate VMs** (Test 3)
4. **✅ Verify 5 VMs created** (Test 4-5)
5. **Configure zones and hypervisor** via frontend
6. **Comment out failed roles** in `install.py`
7. **Start deployment**
8. **Monitor progress**

---

**Congratulations! You're using the proper database-driven approach! 🎉**

This is the recommended way to customize VM generation - by modifying the data, not the code.
