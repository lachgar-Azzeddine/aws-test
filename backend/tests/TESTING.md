# Testing Guide: Ansible Roles Test Suite

## Overview

This guide provides comprehensive instructions for testing Ansible roles in a controlled test environment. The test infrastructure includes Docker services, Kubernetes clusters, databases, and all necessary dependencies.

## Table of Contents

- [Quick Start](#quick-start)
- [Test Scripts](#test-scripts)
- [Detailed Workflow](#detailed-workflow)
- [Testing Different Roles](#testing-different-roles)
- [Prerequisites](#prerequisites)
- [Environment Components](#environment-components)
- [Cleanup Procedures](#cleanup-procedures)
- [Troubleshooting](#troubleshooting)
- [Advanced Usage](#advanced-usage)
- [CI/CD Integration](#cicd-integration)

## Quick Start

### One-Command Test Execution

The fastest way to test a role is to use the orchestration script:

```bash
cd /home/mrabbah/Documents/srm-cs/runner-src/backend
./tests/setup_test_env.sh && ./tests/run_test.sh
```

Or in two steps:

```bash
# Step 1: Set up the complete test environment
./tests/setup_test_env.sh

# Step 2: Run the test
./tests/run_test.sh
```

### Testing a Specific Role

```bash
# Test install-gravitee-lan (default)
./tests/run_test.sh

# Test a different role
./tests/run_test.sh --role install-keycloak

# Skip image operations (faster for reruns)
./tests/run_test.sh --role install-gravitee-lan --skip-images
```

## Test Scripts

### setup_test_env.sh

**Purpose:** Initialize the complete test environment

**What it does:**
1. Checks prerequisites (docker, python3, kubeconfig)
2. Creates necessary directories and certificates
3. Starts Docker Compose services (registry, Gogs, Vault)
4. Sets up Vault
5. Initializes Kubernetes clusters
6. Initializes Gogs repository
7. Creates and seeds test database
8. Downloads ArgoCD images as prerequisite
9. Runs install-argocd role (prerequisite)

**Usage:**
```bash
./setup_test_env.sh
```

**Environment Variables Set:**
- `DATABASE_URL`: Points to test database
- `SQLHOSTS_FILE`: Path to SQL hosts file
- `KUBECONFIG`: Kubernetes config path
- `PYTHONPATH`: Backend directory added to Python path
- `TEST_ENVIRONMENT`: Set to true

### run_test.sh

**Purpose:** Orchestrate role testing workflow

**What it does:**
1. Checks prerequisites
2. Downloads Docker images (unless --skip-images)
3. Pushes images to test registry
4. Executes the specified Ansible role
5. Reports results

**Usage:**
```bash
./run_test.sh [options]

Options:
  -r, --role ROLE_NAME    Specify the role to test (default: install-gravitee-lan)
  -s, --skip-images       Skip image download and push operations
  -h, --help              Show help message
```

**Examples:**
```bash
# Default test (install-gravitee-lan)
./run_test.sh

# Test specific role
./run_test.sh --role install-keycloak

# Skip image operations
./run_test.sh --skip-images

# Combined flags
./run_test.sh --role install-gravitee-lan --skip-images
```

### cleanup.sh

**Purpose:** Clean up all test resources

**What it does:**
1. Shuts down all Docker containers
2. Deletes Kubernetes clusters (test-cluster, test-cluster-mw)
3. Removes test database and SQL hosts file
4. Removes generated directories (vault, registry, gogs data)

**Usage:**
```bash
./cleanup.sh
```

**Example Output:**
```bash
==========================================
1- Shutdown docker containers
==========================================

==========================================
2- Deleting K8s Clusters
==========================================

==========================================
3- Removing database
==========================================

==========================================
4- Removing Directories
==========================================
```

## Detailed Workflow

### Step 1: Environment Setup

The `setup_test_env.sh` script performs a complete environment initialization:

**Prerequisites Check:**
```bash
- Docker installed and available
- Python 3.7+ installed
- Valid kubeconfig at ~/.kube/config
```

**Directory Creation:**
```bash
mkdir -p dataregistry vault/file vault/logs
```

**Docker Compose Services:**
Starts three services via `docker compose up -d`:

1. **Registry** (localhost:8443)
   - Docker registry with TLS
   - Basic authentication (testuser/testpassword)
   - Stores all role-specific images

2. **Gogs** (localhost)
   - Git service for storing playbooks
   - HTTPS enabled with self-signed certificate

3. **Vault** (localhost:8200)
   - HashiCorp Vault for secrets management
   - Used for secret injection in roles

**Kubernetes Setup:**
- Creates k3d clusters (test-cluster, test-cluster-mw)
- Configures kubeconfig

**Database Initialization:**
- Creates SQLite test database
- Seeds with test data via `test_database.py`
- Additional seeding via `seed_test_db.py`

**Prerequisite Installation:**
- Downloads ArgoCD images
- Pushes to test registry
- Runs `install-argocd` role as prerequisite

### Step 2: Image Management

The test framework automatically handles Docker images:

**Download (via tar_images.py):**
```bash
python tar_images.py --role <ROLE_NAME> ./tests/data/images
```

**Push to Registry (via push_images_to_registry.sh):**
```bash
./push_images_to_registry.sh ./tests/data/images <ROLE_NAME>
```

**Skip Images Option:**
Use `--skip-images` flag to avoid re-downloading and pushing:
```bash
./run_test.sh --role install-gravitee-lan --skip-images
```

This is useful for:
- Rerunning tests after fixing issues
- Multiple test runs in development
- When images are already available

### Step 3: Role Execution

The role is executed via `install.py` in the backend directory:

```bash
python install.py --role <ROLE_NAME>
```

**Role Requirements:**

Each role must have:
1. **images.txt** - Lists required Docker images
2. **prepare_inputs.py** - Prepares role-specific variables
3. **main.yml** or other playbook files

**Example images.txt:**
```
alpine:latest
graviteeio/apim-management-ui:3.15.9
graviteeio/apim-portal-ui:3.15.9
graviteeio/apim-gateway:3.15.9
```

**Example prepare_inputs.py:**
```python
def get_inputs():
    return {
        'apim_base_domain': 'apim.test.local',
        'base_domain': 'test.local',
        'registry_url': 'test-registry.test.local:8443',
        'gogs_url': 'test-gogs.test.local',
        'gogs_ip': '10.97.235.87',
        'lblan_ip': '10.97.235.86',
        'gravitee_username': 'admin',
        'gravitee_password': 'admin',
        'prefix': 'test-'
    }
```

## Testing Different Roles

### Testing install-gravitee-lan (Default)

```bash
./setup_test_env.sh
./run_test.sh
```

### Testing Other Roles

```bash
# Test install-argocd (already installed as prerequisite)
./run_test.sh --role install-argocd

# Test any other role
./run_test.sh --role <ROLE_NAME>
```

### Adapting for New Roles

To add a new role to the test suite:

1. **Create role directory structure:**
   ```
   project/roles/<your-role-name>/
   ├── tasks/
   ├── templates/
   ├── files/
   ├── images.txt
   ├── prepare_inputs.py
   └── post_install.py (optional)
   ```

2. **Define images in images.txt:**
   ```
   image1:tag
   image2:tag
   ```

3. **Create prepare_inputs.py:**
   ```python
   def get_inputs():
       return {
           # Role-specific variables
       }
   ```

4. **Test the role:**
   ```bash
   ./run_test.sh --role <your-role-name>
   ```

## Prerequisites

### System Requirements

- **Docker** (version 20.0+)
- **Docker Compose** (v2.0+)
- **Python** (3.7+)
- **Git**
- **Valid kubeconfig** at `~/.kube/config`

### Verify Prerequisites

```bash
# Check Docker
docker --version

# Check Python
python3 --version

# Check kubeconfig
ls -l ~/.kube/config

# Check Docker Compose
docker compose version
```

### Directory Structure

```
backend/
├── tests/                          # Test environment
│   ├── test_database.py           # Database initialization
│   ├── seed_test_db.py            # Database seeding
│   ├── push_images_to_registry.sh # Image registry setup
│   ├── run_test.sh                # Orchestration script
│   ├── setup_test_env.sh          # Environment setup
│   ├── cleanup.sh                 # Cleanup script
│   ├── docker-compose.yml         # Test services
│   ├── TESTING.md                 # This file
│   └── data/                      # Downloaded images
├── project/roles/<role-name>/      # Roles to test
├── tar_images.py                  # Image download utility
└── install.py                     # Role execution
```

## Environment Components

### Docker Services

**Registry** (`localhost:8443`)
- Purpose: Store Docker images
- Authentication: testuser/testpassword
- TLS enabled

**Gogs** (`localhost`)
- Purpose: Git service
- HTTPS with self-signed certificate
- Stores Ansible playbooks

**Vault** (`localhost:8200`)
- Purpose: Secrets management
- Used for secret injection
- Token-based authentication

### Kubernetes Clusters

**test-cluster**
- Primary cluster for testing
- Used by roles requiring K8s

**test-cluster-mw**
- Middleware cluster
- For middleware-specific roles

### Database

**SQLite Database** (`test_runner.db`)
- Created during setup
- Contains test data
- Seeded via test_database.py and seed_test_db.py

## Cleanup Procedures

### Full Cleanup

Remove all test resources:

```bash
./cleanup.sh
```

### What Gets Removed

- Docker containers and networks
- Kubernetes clusters
- Test database
- Generated directories:
  - `vault/logs`
  - `vault/file`
  - `dataregistry`
  - `gogs-data/gogs.db`
  - `gogs-data/data`
  - `gogs-data/log`

### Partial Cleanup

Remove only specific components:

```bash
# Stop containers only
docker compose down

# Remove database only
rm -f test_runner.db test_sqlhosts

# Remove images only
rm -rf data/images
```

### Reset Everything

Complete reset for troubleshooting:

```bash
./cleanup.sh
./setup_test_env.sh
./run_test.sh
```

## Troubleshooting

### Common Issues

#### 1. Prerequisites Missing

**Symptom:**
```
[ERROR] Docker not found
[ERROR] Python 3 not found
[ERROR] Kubeconfig not found
```

**Solution:**
```bash
# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Install Python 3
sudo apt-get update
sudo apt-get install python3

# Ensure kubeconfig exists
ls -l ~/.kube/config
```

#### 2. Database Locked

**Symptom:**
```
[ERROR] database is locked
```

**Solution:**
```bash
# Check for running processes
ps aux | grep python

# Remove stale database
rm -f test_runner.db

# Reinitialize
python3 test_database.py
```

#### 3. Registry Not Accessible

**Symptom:**
```
[ERROR] Registry is not accessible
```

**Solution:**
```bash
# Check if registry is running
docker compose ps registry

# Start services
docker compose up -d

# Wait for startup
sleep 10

# Verify
curl -k -u testuser:testpassword https://localhost:8443/v2/_catalog
```

#### 4. Port Conflicts

**Symptom:**
```
Error: Port 8443 is already in use
```

**Solution:**
```bash
# Find process using port
lsof -i :8443

# Stop conflicting service
docker compose down

# Or kill the process
kill <PID>
```

#### 5. Image Download Fails

**Symptom:**
```
[ERROR] No tar files found
```

**Solution:**
```bash
# Check images directory
ls -la data/images/

# Download images
python tar_images.py --role install-gravitee-lan data/images

# Retry
./run_test.sh
```

#### 6. Role Execution Fails

**Symptom:**
```
[ERROR] Role execution failed
```

**Solution:**
```bash
# Run with verbose output
./run_test.sh --role install-gravitee-lan 2>&1 | tee test.log

# Check role requirements
ls -la project/roles/install-gravitee-lan/

# Verify images.txt
cat project/roles/install-gravitee-lan/images.txt

# Check prepare_inputs.py
cat project/roles/install-gravitee-lan/prepare_inputs.py
```

### Debug Mode

Enable verbose logging:

```bash
# Export debug level
export PYTHONLOGLEVEL=DEBUG

# Run test with verbose output
./run_test.sh --role install-gravitee-lan --skip-images 2>&1 | tee debug.log
```

### View Logs

```bash
# View all service logs
docker compose logs

# View specific service
docker compose logs -f registry
docker compose logs -f gogs
docker compose logs -f vault

# View Kubernetes logs
kubectl logs -n default test-cluster

# View test execution logs
./run_test.sh 2>&1 | tee test.log
```

### Verify Environment

```bash
# Check running containers
docker compose ps

# Check Kubernetes clusters
k3d cluster list

# Check registry
curl -k -u testuser:testpassword https://localhost:8443/v2/_catalog

# Check database
python3 -c "
import sqlite3
conn = sqlite3.connect('test_runner.db')
cursor = conn.cursor()
cursor.execute('SELECT name FROM sqlite_master WHERE type=\"table\";')
print(cursor.fetchall())
conn.close()
"
```

## Advanced Usage

### Custom Database Path

```bash
# Set custom database location
export DATABASE_URL="sqlite:///./custom/test.db"
export SQLHOSTS_FILE="./custom/test_sqlhosts"
./setup_test_env.sh
```

### Custom Images Directory

```bash
# Use custom location for images
./run_test.sh --role install-gravitee-lan --images-dir /custom/path
```

### Skipping Setup

When environment is already set up:

```bash
# Just run the test
./run_test.sh --skip-images
```

### Testing with Modified Variables

Edit the role's `prepare_inputs.py` to customize test variables:

```python
def get_inputs():
    return {
        'base_domain': 'custom.test.local',
        'apim_base_domain': 'apim.custom.test.local',
        'prefix': 'custom-',
        # ... other variables
    }
```

### CI/CD Integration

**GitHub Actions:**

```yaml
name: Test Ansible Roles

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2

      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: "3.9"

      - name: Set up Docker
        run: |
          sudo apt-get update
          sudo apt-get install -y docker-compose

      - name: Run Tests
        run: |
          cd backend
          ./tests/setup_test_env.sh
          ./tests/run_test.sh --role install-gravitee-lan
```

**Jenkins Pipeline:**

```groovy
pipeline {
    agent any
    stages {
        stage('Test Role') {
            steps {
                sh '''
                    cd backend
                    ./tests/setup_test_env.sh
                    ./tests/run_test.sh --role install-gravitee-lan
                '''
            }
            post {
                always {
                    archiveArtifacts artifacts: 'backend/tests/**/*.log', allowEmptyArchive: true
                }
            }
        }
    }
}
```

## Best Practices

1. **Always run from backend directory**
   ```bash
   cd /home/mrabbah/Documents/srm-cs/runner-src/backend
   ./tests/setup_test_env.sh
   ```

2. **Use --skip-images for faster iterations**
   ```bash
   ./run_test.sh --role install-gravitee-lan --skip-images
   ```

3. **Check prerequisites before running**
   ```bash
   docker --version
   python3 --version
   ls -l ~/.kube/config
   ```

4. **Clean up before starting fresh**
   ```bash
   ./cleanup.sh
   ./setup_test_env.sh
   ```

5. **Save logs for debugging**
   ```bash
   ./run_test.sh 2>&1 | tee test-$(date +%Y%m%d-%H%M%S).log
   ```

6. **Verify images exist before running**
   ```bash
   ls -la data/images/*.tar
   ```

## Support

For issues or questions:

1. Check this troubleshooting guide
2. Review test logs
3. Check Docker Compose logs: `docker compose logs`
4. Verify prerequisites
5. Check role requirements (images.txt, prepare_inputs.py)
6. Review the actual script code in `setup_test_env.sh`, `run_test.sh`, `cleanup.sh`

## References

- [Ansible Runner Documentation](https://ansible-runner.readthedocs.io/)
- [Docker Registry Documentation](https://docs.docker.com/registry/)
- [Vault Documentation](https://www.vaultproject.io/docs)
- [Gogs Documentation](https://gogs.io/docs)
- [k3d Documentation](https://k3d.io/)

---

**Test Framework Version:** 2.0
**Last Updated:** 2025-11-10
