# Local Testing Setup (No Real Infrastructure Needed)

**Purpose:** Test and learn the platform without VMware/Nutanix infrastructure.

---

## 🎯 What You Can Test Locally

✅ **Backend API** - All endpoints work
✅ **Frontend** - Complete wizard flow
✅ **Database** - Configuration storage
✅ **Architecture Scaffolding** - VM generation logic
✅ **Ansible prepare_inputs.py** - Variable loading
❌ **Actual VM provisioning** - Requires real hypervisor
❌ **Kubernetes deployment** - Requires real VMs

---

## 🚀 Quick Start (5 minutes)

### 1. Start the Platform

```bash
# Navigate to project
cd runner-srm-cs-genric

# Start all services
docker compose up -d

# Check status
docker compose ps
```

**Access:**
- Frontend: http://localhost/runner/
- Backend API: http://localhost/runner/api/docs
- Corteza: http://localhost/
- PostgreSQL: localhost:5432

---

### 2. Create Test Configuration

**Access the frontend:** http://localhost/runner/

**Step through the wizard with dummy data:**

#### Step 1: Add Hypervisor
```
Type: VMware vSphere
Alias: test-vcenter
Login: administrator@vsphere.local
Password: TestPassword123
API URL: vcenter.test.local
Datacenter: DC1
Cluster: Cluster1
Datastore: datastore1
Resource Pool: Resources
```

*Note: These won't connect to anything - just testing the database storage*

#### Step 2: Configure Zones
```
Zone 1:
  Name: LAN_INFRA
  Subnet: 10.1.10.0
  Network Mask: 24
  Gateway: 10.1.10.1
  DNS: 8.8.8.8
  VLAN: VLAN10
  IP Pool: 10.1.10.10 - 10.1.10.50

Zone 2:
  Name: LAN_APPS
  Subnet: 10.1.20.0
  Network Mask: 24
  Gateway: 10.1.20.1
  DNS: 8.8.8.8
  VLAN: VLAN20
  IP Pool: 10.1.20.10 - 10.1.20.50

Zone 3:
  Name: DMZ
  Subnet: 10.1.200.0
  Network Mask: 24
  Gateway: 10.1.200.1
  DNS: 8.8.8.8
  VLAN: VLAN200
  IP Pool: 10.1.200.10 - 10.1.200.50
```

#### Step 3: Security Settings
```
SSH Public Key: [Generate with: ssh-keygen -t rsa -b 4096]
SSH Private Key: [Copy from ~/.ssh/id_rsa]
Base Domain: test.local
Environment Prefix: dev
SSL Certificate: [Self-signed is fine for testing]
```

#### Step 4: Set User Count
```
Number of Concurrent Users: 100
```

#### Step 5: Review Architecture
- Click "Generate VMs"
- See the platform auto-generate VM architecture
- Verify IP assignments
- Check VM sizing

---

## 🧪 What to Test

### Test 1: Database Operations

**Test CRUD operations via API:**

```bash
# Get configuration
curl http://localhost/runner/api/configuration

# Get zones
curl http://localhost/runner/api/zones

# Get virtual machines (triggers scaffold)
curl http://localhost/runner/api/virtual-machines

# Get hypervisors
curl http://localhost/runner/api/hypervisors
```

---

### Test 2: Architecture Scaffolding

**Verify VM generation logic:**

1. Go to http://localhost/runner/api/virtual-machines
2. See auto-generated VMs based on user count
3. Verify:
   - Correct number of VMs
   - Proper IP assignments
   - Appropriate sizing (CPU/RAM/Disk)
   - Correct zone assignments

**Example output:**
```json
[
  {
    "id": 1,
    "hostname": "vault-01",
    "ip": "10.1.10.10",
    "zone_id": 1,
    "group": "vault",
    "roles": "vault,docker",
    "nb_cpu": 4,
    "ram": 8,
    "os_disk_size": 100
  },
  ...
]
```

---

### Test 3: Ansible prepare_inputs.py

**Test variable loading without execution:**

```bash
# Enter backend container
docker exec -it backend bash

# Test a prepare_inputs.py function
cd /home/devops/project/roles/install-vault
python3 << EOF
import sys
sys.path.insert(0, '/home/devops')
from repository import get_session
from prepare_inputs import get_inputs

_, Session = get_session()
extra_vars, inventory = get_inputs(Session)

print("Variables loaded:")
print(extra_vars)
print("\nInventory generated:")
print(inventory)
EOF
```

**Expected:** Variables and inventory printed (using database config)

---

### Test 4: Frontend Workflow

**Test complete wizard flow:**

1. ✅ Add hypervisor
2. ✅ Configure zones
3. ✅ Set security settings
4. ✅ Add external services (LDAP, SMTP - dummy data)
5. ✅ Set user count
6. ✅ Generate VMs
7. ✅ Review architecture
8. ⚠️ Don't click "Deploy" (will fail without real infrastructure)

---

### Test 5: Database Inspection

**Verify data storage:**

```bash
# Access PostgreSQL
docker exec -it postgres psql -U harmonisation

# Check tables
\dt

# View configuration
SELECT * FROM configurations;

# View zones
SELECT id, name, sub_network, gateway FROM zones;

# View VMs
SELECT hostname, ip, nb_cpu, ram, zone_id FROM virtual_machines;

# View hypervisors
SELECT alias, api_url, datacenter_name FROM vmware_esxi;

# Exit
\q
```

---

## 🔍 Testing Different Scenarios

### Scenario 1: Different User Counts

Test VM scaling:

```bash
# Via API
curl -X PUT http://localhost/runner/api/configuration/concurrent-users \
  -H "Content-Type: application/json" \
  -d '{"number": 200}'

# View updated VMs
curl http://localhost/runner/api/virtual-machines
```

**Expected:** More/larger VMs generated

---

### Scenario 2: Different Zone Layouts

Test 4-zone architecture:

1. Add 4th zone via frontend:
   ```
   Name: LAN_DATA
   Subnet: 10.1.30.0/24
   ```

2. Regenerate VMs
3. Verify distribution across 4 zones

---

### Scenario 3: Multiple Hypervisors

Test multi-hypervisor support:

1. Add second hypervisor (Nutanix or VMware)
2. Assign different zones to different hypervisors
3. Verify zone-hypervisor mapping

---

## 📊 Validation Checklist

After testing, verify:

- [ ] Can add/edit/delete hypervisors
- [ ] Can add/edit/delete zones
- [ ] Can configure security settings
- [ ] Can add external services (LDAP, SMTP, etc.)
- [ ] VMs auto-generate based on user count
- [ ] VMs have correct IPs within zone ranges
- [ ] VMs have appropriate sizing
- [ ] Database stores all configuration
- [ ] API endpoints return correct data
- [ ] Frontend wizard flows work end-to-end

---

## 🎓 Learning Exercises

### Exercise 1: Trace a Request

**Goal:** Understand the three-layer architecture

1. Frontend: Click "Add VMware Hypervisor"
2. Network: See POST to `/runner/api/vmware`
3. API: Check `api.py:add_vmware()` function
4. Repository: See `repository.py:add_vmware_esxi_configuration()`
5. Database: Query `SELECT * FROM vmware_esxi;`

**Result:** See data flow through all layers

---

### Exercise 2: Customize for "Client ACME"

**Goal:** Practice client customization

1. Security settings:
   - Base Domain: `acme.com`
   - Prefix: `prod-`

2. Add ACME's LDAP:
   - URL: `ldap://ad.acme.internal`
   - Port: `389`

3. Add ACME's SMTP:
   - Host: `smtp.acme.com`
   - Port: `587`

4. Generate VMs
5. Verify domains: `prod-vault.acme.com`, etc.

**Result:** See how configuration adapts

---

### Exercise 3: Create Custom Role (Dry Run)

**Goal:** Understand how to add new services

1. Create role structure:
   ```bash
   mkdir -p backend/project/roles/install-test-app/{tasks,templates}
   ```

2. Create `prepare_inputs.py`:
   ```python
   from repository import get_security, get_vms_by_group

   def get_inputs(Session):
       security = get_security(Session)

       extra_vars = {
           "app_domain": f"{security.env_prefix}testapp.{security.base_domain}"
       }

       inventory = {
           "all": {
               "hosts": {
                   "localhost": {
                       "ansible_host": "127.0.0.1",
                       "ansible_connection": "local"
                   }
               }
           }
       }

       return extra_vars, inventory
   ```

3. Test variable loading (as shown in Test 3)

**Result:** Understand role creation pattern

---

## 🐛 Troubleshooting

### Issue: Frontend won't load

```bash
# Check nginx
docker logs nginx

# Check frontend
docker logs frontend

# Restart
docker compose restart nginx frontend
```

---

### Issue: API returns errors

```bash
# Check backend logs
docker logs backend

# Check database
docker logs postgres

# Test API directly
curl http://localhost/runner/api/configuration
```

---

### Issue: Database connection fails

```bash
# Check PostgreSQL
docker exec postgres pg_isready -U harmonisation

# Check backend env
docker exec backend env | grep DATABASE_URL

# Should be:
# DATABASE_URL=postgresql://harmonisation:harmonisation@postgres:5432/harmonisation
```

---

### Issue: Cannot access on Windows

If using WSL2:
```bash
# Get WSL IP
ip addr show eth0 | grep inet

# Access via: http://<WSL_IP>/runner/
```

Or use port forwarding:
```yaml
# docker-compose.yml
nginx:
  ports:
    - "8080:80"  # Access via http://localhost:8080/runner/
```

---

## 🔄 Reset Everything

**Start fresh:**

```bash
# Stop all containers
docker compose down

# Remove all data
rm -rf data/postgres/*

# Restart
docker compose up -d

# Wait for initialization
docker logs -f postgres
# (Wait for "database system is ready to accept connections")
```

---

## 📚 What to Learn

### Master these concepts:

1. **Three-layer architecture**
   - Frontend → API → Repository → Database
   - Never skip layers

2. **Database-driven configuration**
   - Everything stored in PostgreSQL
   - No hardcoded values

3. **Ansible integration**
   - `prepare_inputs.py` loads from database
   - Roles receive variables dynamically

4. **VM scaffolding logic**
   - User count → VM sizing calculator
   - Zone distribution algorithm

5. **Customization points**
   - What's configurable (90%)
   - What needs code (10%)

---

## ✅ Success Criteria

**You're ready when you can:**

- [ ] Configure a complete test deployment via frontend
- [ ] Explain what each database table stores
- [ ] Trace a request through all layers
- [ ] Understand how Ansible roles get variables
- [ ] Know when code changes are needed vs config
- [ ] Can explain the deployment flow to a client
- [ ] Understand VM sizing calculations
- [ ] Know how to add external services

---

## 🚀 Next Steps

After mastering local testing:

1. **Deploy on cloud free tier** (Oracle, AWS, etc.)
   - Test actual VM provisioning
   - Run real Ansible roles
   - Deploy Kubernetes clusters

2. **Create client demo**
   - Prepare sample configuration
   - Show frontend wizard
   - Explain customization options

3. **Practice scenarios**
   - Different client requirements
   - Custom applications
   - Unusual network layouts

**You're ready! 🎉**

When a client comes, you'll know:
- What questions to ask
- How to configure their requirements
- When you need code vs config
- How to troubleshoot issues
