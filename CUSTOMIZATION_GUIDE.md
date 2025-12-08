# Platform Customization Guide for Client Projects

**Purpose:** This guide explains how to customize and deploy the SRM-CS Automation Platform for different client projects **without modifying code**.

---

## 🎯 Overview - What Can You Customize?

The platform is designed to be **100% configurable via the database and frontend**. When you get a new client project, you customize through:

1. **Frontend Configuration** (no code changes)
2. **Database Configuration** (data only)
3. **Ansible Variable Overrides** (per-client values)
4. **Optional: New Roles** (if client needs new services)

---

## 📋 Pre-Project Checklist

Before starting a new client project, gather this information:

### Infrastructure Details
- [ ] Hypervisor type: VMware vSphere or Nutanix AHV?
- [ ] vCenter/Prism Central URL and credentials
- [ ] Datacenter/Cluster names
- [ ] Datastore names
- [ ] Network/VLAN information
- [ ] IP addressing scheme

### Network Configuration
- [ ] How many network zones? (Typical: 3 - INFRA, APPS, DMZ)
- [ ] IP ranges for each zone
- [ ] Gateway IPs
- [ ] DNS servers
- [ ] Proxy settings (if required)

### External Services
- [ ] LDAP/Active Directory details (if integrating)
- [ ] External databases (PostgreSQL, Informix, etc.)
- [ ] SMTP server for emails
- [ ] SMS provider (if needed)

### Security & Certificates
- [ ] Domain name (e.g., client.com)
- [ ] SSL certificates (wildcard or specific)
- [ ] SSH key pair for VM access
- [ ] Environment prefix (e.g., "prod", "dev", "staging")

### Application Requirements
- [ ] Number of concurrent users (sizing)
- [ ] Which applications to deploy? (Generic: MinIO, Keycloak, Kafka, etc.)
- [ ] Custom applications? (will need new Ansible roles)

---

## 🔧 Customization Scenarios

### Scenario 1: Standard Deployment (No Code Changes)

**Client:** "We want the standard platform with our infrastructure"

**What you do:**
1. Access the frontend: `http://your-server/runner/`
2. Configure via wizard (steps 1-8):

**Step 1: Hypervisor Configuration**
- Add VMware vCenter or Nutanix Prism Central
- Provide credentials
- Select datacenter, cluster, datastore

**Step 2: Network Zones**
- Define 3 zones (INFRA, APPS, DMZ)
- Set IP ranges, VLANs, gateways
- Assign to hypervisor

**Step 3: Security Settings**
- Upload SSH public/private key
- Upload SSL certificate
- Set base domain (e.g., `client.com`)
- Set environment prefix (e.g., `prod-`)
- Configure proxy (if needed)

**Step 4: External Services** (optional)
- Add LDAP server
- Add external databases
- Add SMTP server
- Add SMS provider

**Step 5: Resource Sizing**
- Set number of concurrent users
- Platform auto-calculates VM sizes

**Step 6: Review Architecture**
- See generated VM list
- Verify IP assignments
- Adjust if needed

**Step 7: Start Deployment**
- Click "Deploy"
- Monitor progress

**Result:** Fully deployed platform with:
- VMs created on client infrastructure
- Kubernetes clusters (RKE2)
- Core services (Vault, Registry, Gogs, etc.)
- Middleware (MinIO, Keycloak, Kafka, etc.)
- All configured with client's settings

**Code changes:** ZERO ✅

---

### Scenario 2: Custom Domain and Branding

**Client:** "Use our domain `acme.com` and prefix `prod-`"

**Configuration:**

In **Security** settings:
```
Base Domain: acme.com
Environment Prefix: prod
```

**Result:**
- Gogs: `https://prod-gogs.acme.com`
- Registry: `https://prod-registry.acme.com:8443`
- ArgoCD: `https://prod-argocd-apps.acme.com`
- MinIO: `https://prod-minio.acme.com`
- Keycloak: `https://prod-keycloak.acme.com`

**Code changes:** ZERO ✅

---

### Scenario 3: Different Network Layout

**Client:** "We need 4 zones, not 3"

**Configuration:**

In **Zones** section, add zones:
1. `LAN_INFRA` - Core infrastructure (10.1.10.0/24)
2. `LAN_APPS` - Business applications (10.1.20.0/24)
3. `LAN_DATA` - Databases (10.1.30.0/24) ← NEW
4. `DMZ` - External access (10.1.200.0/24)

**What happens:**
- Platform automatically distributes VMs across zones
- Creates separate Kubernetes clusters per zone
- Configures network flows

**Code changes:** ZERO ✅

---

### Scenario 4: Air-Gapped Environment (No Internet)

**Client:** "Our servers have no internet access"

**Preparation (on internet-connected machine):**
1. Download Docker images:
   ```bash
   cd backend
   python tar_images.py  # Creates .tar files of all images
   ```

2. Transfer to client site:
   - Copy `*.tar` files
   - Copy entire project folder

**On-site deployment:**
1. Load images:
   ```bash
   bash setup.sh  # Loads all .tar images
   ```

2. Configure to use local registry:
   - Set `registry_url` in prepare_inputs.py files
   - Point to client's internal registry

3. Deploy normally through frontend

**Code changes:** Minimal (registry URLs in prepare_inputs.py) ⚠️

---

### Scenario 5: Different Hypervisor

**Client A:** "We use VMware vSphere"
**Client B:** "We use Nutanix AHV"

**Configuration:**

Both supported! Just select during wizard:
- VMware: Provide vCenter details
- Nutanix: Provide Prism Central details

**How it works:**
- `provisionnement-vms-*` roles detect hypervisor type
- Use appropriate API calls
- Same VMs, different provisioning method

**Code changes:** ZERO ✅

---

### Scenario 6: Custom VM Sizing

**Client:** "We have very large workloads"

**Option 1: Via Frontend** (Recommended)
- Set "Number of Concurrent Users" to higher value
- Platform auto-scales VMs

**Option 2: Manual Override**
After scaffolding, edit VMs via frontend:
- Go to Virtual Machines page
- Click edit on any VM
- Adjust CPU/RAM/Disk

**Code changes:** ZERO ✅

---

### Scenario 7: Additional LDAP Integration

**Client:** "We have internal AD and external LDAP"

**Configuration:**

Add multiple LDAP servers:
1. Internal Users:
   ```
   Type: internal_users
   URL: ldap://ad.client.internal
   Port: 389
   Bind DN: CN=svc_ldap,OU=Service Accounts,DC=client,DC=internal
   ```

2. External Users:
   ```
   Type: external_users
   URL: ldap://public.ldap.com
   Port: 636
   ```

**How it works:**
- Both stored in database
- Ansible roles configure applications to use both
- Keycloak federated authentication

**Code changes:** ZERO ✅

---

## 🆕 When You NEED Code Changes

### Scenario 8: Client Needs Custom Application

**Client:** "Deploy our proprietary app 'ClientApp'"

**Steps:**

1. **Create new Ansible role:**
   ```bash
   mkdir -p backend/project/roles/install-clientapp/{tasks,templates,files}
   ```

2. **Create `prepare_inputs.py`:**
   ```python
   from repository import get_security, get_vms_by_group, get_databases

   def get_inputs(Session):
       security = get_security(Session)
       app_vms = get_vms_by_group("clientapp", Session)
       client_db = next(db for db in get_databases(Session) if db.alias == "clientapp_db")

       extra_vars = {
           "app_domain": f"{security.env_prefix}clientapp.{security.base_domain}",
           "db_host": client_db.host,
           "db_name": client_db.name,
           "db_user": base64.b64decode(client_db.login).decode(),
           "db_pass": base64.b64decode(client_db.password).decode(),
       }

       inventory = {
           "all": {
               "hosts": {
                   vm.hostname: {
                       "ansible_host": vm.ip,
                       "ansible_user": "devops"
                   }
                   for vm in app_vms
               }
           }
       }

       return extra_vars, inventory
   ```

3. **Create Ansible tasks** (`tasks/main.yml`):
   ```yaml
   ---
   - name: Deploy ClientApp
     hosts: all
     tasks:
       - name: Install dependencies
         yum:
           name:
             - java-11-openjdk
             - postgresql-client
           state: present

       - name: Deploy application
         copy:
           src: clientapp.jar
           dest: /opt/clientapp/

       - name: Configure application
         template:
           src: application.properties.j2
           dest: /opt/clientapp/application.properties

       - name: Start service
         systemd:
           name: clientapp
           state: started
           enabled: yes
   ```

4. **Add to role sequence** in `install.py`:
   ```python
   apps_roles = [
       "install-clientapp",  # ← Add here
   ]
   ```

5. **Update VM scaffolding** if needed:
   Add ClientApp VMs to `repository.py` → `scaffold_architecture()`

**Code changes:** Required (new role) ⚠️

---

### Scenario 9: Different Kubernetes Distribution

**Client:** "We want K3s instead of RKE2"

**Steps:**

1. **Modify roles:**
   - Copy `install-rke2-apps` → `install-k3s-apps`
   - Update installation commands in tasks
   - Adjust kubeconfig paths

2. **Update `install.py`:**
   ```python
   nokube_roles = [
       # "install-rke2-apps",      # ← Comment out
       # "install-rke2-middleware",
       # "install-rke2-dmz",
       "install-k3s-apps",         # ← Add new
       "install-k3s-middleware",
       "install-k3s-dmz",
   ]
   ```

**Code changes:** Required (new roles) ⚠️

---

## 📊 Configuration Matrix

| Customization | Method | Code Changes | Effort |
|---------------|--------|--------------|--------|
| **Domain name** | Frontend/DB | ❌ None | 5 min |
| **IP ranges** | Frontend/DB | ❌ None | 10 min |
| **Hypervisor** | Frontend/DB | ❌ None | 10 min |
| **LDAP/AD** | Frontend/DB | ❌ None | 15 min |
| **SSL certs** | Frontend/DB | ❌ None | 5 min |
| **VM sizing** | Frontend/DB | ❌ None | 10 min |
| **Number of zones** | Frontend/DB | ❌ None | 20 min |
| **External databases** | Frontend/DB | ❌ None | 15 min |
| **SMTP/SMS** | Frontend/DB | ❌ None | 10 min |
| **Custom app** | New Ansible role | ✅ Yes | 2-4 hours |
| **Different K8s** | Modify roles | ✅ Yes | 4-8 hours |
| **New middleware** | New Ansible role | ✅ Yes | 2-6 hours |

---

## 🧪 Testing Without Real Infrastructure

**Problem:** You don't have vSphere/Nutanix to test on.

**Solution:** Use local virtualization for development/demo:

### Option 1: Docker + k3d (Minimal Test)

**What it tests:** Backend logic, database, Ansible role execution (without real VMs)

```bash
# Already works with docker-compose.yml
docker compose up -d

# Access:
# Frontend: http://localhost/runner/
# Backend API: http://localhost/runner/api/docs
# Corteza: http://localhost/
```

**Configure dummy data:**
- Add fake VMware config (won't provision VMs but tests DB logic)
- Configure zones with fake IPs
- Test frontend wizard
- Verify database queries work

**What it doesn't test:** Actual VM provisioning

---

### Option 2: Vagrant + VirtualBox (Medium Test)

**What it tests:** VM provisioning locally

Create `Vagrantfile`:
```ruby
Vagrant.configure("2") do |config|
  config.vm.define "master" do |master|
    master.vm.box = "generic/rhel9"
    master.vm.network "private_network", ip: "192.168.56.10"
    master.vm.provider "virtualbox" do |vb|
      vb.memory = "4096"
      vb.cpus = 2
    end
  end

  config.vm.define "worker1" do |worker|
    worker.vm.box = "generic/rhel9"
    worker.vm.network "private_network", ip: "192.168.56.11"
  end
end
```

**Simulate deployment:**
- VMs created via Vagrant (instead of Ansible provisioning)
- Run `prepare-vms` role against them
- Test Kubernetes installation roles
- Test application deployment

---

### Option 3: Cloud Free Tier (Real-ish Test)

**Providers with free tier:**
- AWS: 12 months free (EC2 t2.micro)
- Azure: $200 credit
- GCP: $300 credit
- Oracle Cloud: Always free tier (4 ARM VMs!)

**Use Oracle Cloud (Best for testing):**
1. Create 4 ARM VMs (always free!)
2. Configure as if they were client VMs
3. Run actual Ansible roles
4. Deploy real Kubernetes

**Cost:** FREE ✅

---

## 📖 Client Onboarding Workflow

When you get a new client:

### Week 1: Discovery
- [ ] Gather infrastructure details (checklist above)
- [ ] Understand application requirements
- [ ] Identify integration points (LDAP, DBs, etc.)
- [ ] Document network architecture

### Week 2: Setup
- [ ] Deploy platform backend (docker compose)
- [ ] Configure hypervisor connection
- [ ] Configure network zones
- [ ] Upload SSH keys and SSL certs
- [ ] Test connectivity to infrastructure

### Week 3: Customization
- [ ] Create new roles for client apps (if needed)
- [ ] Configure external services (LDAP, SMTP, etc.)
- [ ] Adjust VM sizing based on load
- [ ] Test in staging environment

### Week 4: Deployment
- [ ] Run deployment through frontend
- [ ] Monitor Ansible role execution
- [ ] Verify all services up
- [ ] Hand over credentials
- [ ] Document client-specific settings

---

## 🔐 Client-Specific Data Storage

**Where to store client configurations:**

### Database (Primary)
All client data goes in database:
- Hypervisor credentials (encrypted)
- Network zones
- External service configs
- VM definitions

### Environment Files (Secondary)
Per-client environment configs:
```
backend/data/env/
├── client-acme/
│   ├── security.env
│   └── custom.env
├── client-beta/
│   └── security.env
```

### Ansible Inventories (Generated)
Auto-generated per deployment:
```
backend/data/inventory/
├── deployment-20250104/
│   └── hosts.yml
```

---

## 🎓 Summary - How to Be Ready

### When Client Calls:

1. **Ask the right questions** (use pre-project checklist)
2. **90% configured via frontend** (no code changes)
3. **Only write code for**:
   - Custom applications
   - Unusual requirements
   - New middleware services

### Your Platform Is:
- ✅ **Generic** - Works for any client
- ✅ **Database-driven** - All config in DB
- ✅ **Hypervisor-agnostic** - VMware or Nutanix
- ✅ **Network-flexible** - Any zone layout
- ✅ **Extensible** - Easy to add roles

### You're Ready When:
- ✅ You understand the customization points
- ✅ You know what requires code vs config
- ✅ You can explain the deployment flow
- ✅ You've tested locally (docker-compose)
- ✅ You have this documentation

---

## 📞 Quick Reference

**Most common customizations:**
1. Domain name → Security settings
2. IP ranges → Zone configuration
3. VM sizes → Concurrent users setting
4. External services → Add via frontend
5. Custom apps → New Ansible role

**Zero code changes for:**
- Different domain
- Different infrastructure
- Different network layout
- Different external services
- Different SSL certs
- Different VM sizing

**Code changes needed for:**
- Custom applications
- New middleware
- Different K8s distribution
- Unusual requirements

---

**You're ready! 🚀** When a client comes, just gather their infrastructure details and configure through the frontend. The platform handles the rest.
