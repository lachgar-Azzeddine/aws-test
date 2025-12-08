#!/bin/bash

# Exit immediately if a command exits with a non-zero status.
set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# --- Configuration ---
TEST_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$(dirname "$TEST_DIR")"
DB_PATH="${TEST_DIR}/test_runner.db"
IMAGES_DIR="${TEST_DIR}/data/images"

# --- Environment Variables for Test ---
export DATABASE_URL="sqlite:///${DB_PATH}"
export SQLHOSTS_FILE="${TEST_DIR}/test_sqlhosts"
export KUBECONFIG="${HOME}/.kube/config"
export PYTHONPATH="${PYTHONPATH}:${BACKEND_DIR}"
export TEST_ENVIRONMENT=true

# --- Helper Functions ---
print_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
print_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
print_error() { echo -e "${RED}[ERROR]${NC} $1"; }
print_warning() { echo -e "${YELLOW}[WARN]${NC} $1"; }
print_header() { echo -e "\n${YELLOW}==========================================${NC}\n$1\n${YELLOW}==========================================${NC}"; }

check_prerequisites() {
  print_header "1. Checking Prerequisites"
  command -v docker &>/dev/null || {
    print_error "Docker not found"
    exit 1
  }
  command -v python3 &>/dev/null || {
    print_error "Python 3 not found"
    exit 1
  }
  # command -v openssl &>/dev/null || {
  #   print_error "openssl not found"
  #   exit 1
  # }
  [ -f "${KUBECONFIG}" ] || {
    print_error "Kubeconfig not found at ${KUBECONFIG}"
    exit 1
  }
  print_success "All prerequisites met."
}

init_and_seed_database() {
  print_header "8. Initializing and Seeding Test Database"

  print_info "Initializing database schema at: ${DB_PATH}"
  python3 "${TEST_DIR}/test_database.py" --db-path "${DB_PATH}"

  print_info "Seeding database with Gogs IP..."
  python3 "${TEST_DIR}/seed_test_db.py" --db-path "${DB_PATH}"

  print_success "Database is ready."
}

check_prerequisites

print_header "2- Creating the necessary directories"
# Create directories
mkdir -p dataregistry vault/file vault/logs
print_header "3- Creating the necessary certificate"
# Create htpasswd for registry
# docker run --rm --entrypoint htpasswd httpd:2 -Bbn devops devops >auth/htpasswd
# Set ownership for gogs data
# subjectAltName=DNS:harmonisation.docker, DNS:host.k3d.internal, DNS:test-registry.test.local, DNS:localhost
# openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout gogs-data/ssl/gogs.key -out gogs-data/ssl/gogs.crt -subj "/C=US/ST=State/L=City/O=Organization/OU=OrgUnit/CN=localhost"
chown -R 1000:1000 gogs-data 2>/dev/null || true

print_header "4- Strating containers"
cd "${TEST_DIR}"
docker compose up -d

print_header "5- Vault Setup"
./setup-vault.sh

print_header "6- Starting Kubernetes clusters"
./setup_k3d.sh

print_header "7- Initializing Gogs Registry"
./init_gogs_repo.sh

init_and_seed_database

print_header "9- Installing ArgoCD"
# Download for prerequisite role
python3 "${BACKEND_DIR}/tar_images.py" --role "install-argocd" "${IMAGES_DIR}"
chmod +x "${TEST_DIR}/push_images_to_registry.sh"
# Push for prerequisite role
"${TEST_DIR}/push_images_to_registry.sh" "${IMAGES_DIR}" "install-argocd"
print_info "Running prerequisite role: install-argocd"
python3 "${BACKEND_DIR}/install.py" --role install-argocd
if [ $? -ne 0 ]; then
  print_error "Prerequisite role 'install-argocd' failed. Aborting."
  return 1
fi
print_success "Prerequisite role finished successfully."

echo "Test environment setup complete."
