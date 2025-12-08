# Test Environment for Ansible Roles

This directory contains the test infrastructure for validating Ansible roles in a controlled environment.

## Quick Start

### 1. Set up the test environment:
```bash
./setup_test_env.sh
```

This will:
- Create all necessary directories and certificates
- Start Docker services (registry, Gogs, Vault)
- Initialize Kubernetes clusters
- Set up the test database
- Install ArgoCD as a prerequisite
- Verify all components are ready

**Prerequisites:**
- Docker installed and running
- Python 3.7+
- Valid kubeconfig at `~/.kube/config`

### 2. Run tests for a specific role:
```bash
# Test the default role (install-gravitee-lan)
./run_test.sh

# Test a specific role
./run_test.sh --role install-gravitee-lan

# Skip image download/push (faster reruns)
./run_test.sh --role install-gravitee-lan --skip-images
```

This will:
- Download required Docker images (unless --skip-images is used)
- Push images to the test registry
- Execute the specified Ansible role
- Validate the installation

## Testing Different Roles

To test different Ansible roles, simply specify the role name:

```bash
# Test install-gravitee-lan
./run_test.sh --role install-gravitee-lan

# Test install-keycloak (if it exists)
./run_test.sh --role install-keycloak
```

**Note:** The role must have:
- An `images.txt` file listing required Docker images
- A `prepare_inputs.py` script for role-specific variables
- A valid Ansible playbook in the role directory

## Cleanup

When you're done testing, clean up all resources:

```bash
./cleanup.sh
```

This will:
- Stop all Docker containers
- Delete Kubernetes clusters
- Remove test databases
- Clean up all generated data

## Test Environment Components

The test environment includes:

- **Docker Registry** (localhost:8443) - Stores test images
- **Gogs** (localhost) - Git service for Ansible playbooks
- **Vault** (localhost:8200) - Secrets management
- **Kubernetes Clusters** - For testing K8s-specific roles
- **Test Database** - SQLite database with test data

## Troubleshooting

### Prerequisites Check
Ensure you have all required tools:
```bash
docker --version
python3 --version
ls -l ~/.kube/config
```

### View Running Services
```bash
docker compose ps
```

### View Logs
```bash
# All services
docker compose logs

# Specific service
docker compose logs registry
docker compose logs gogs
docker compose logs vault
```

### Reset Everything
If you encounter issues, start fresh:
```bash
./cleanup.sh
./setup_test_env.sh
./run_test.sh --role install-gravitee-lan
```
