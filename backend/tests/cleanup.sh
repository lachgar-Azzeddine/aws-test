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

print_header "1- Shutdown docker containers"
cd "${TEST_DIR}"
docker compose down -v

print_header "2- Deleting K8s Clusters"
k3d cluster delete test-cluster test-cluster-mw

print_header "3- Removing database"
rm -f "${DB_PATH}" "${SQLHOSTS_FILE}"

print_header "4- Removing Directories"

sudo rm -Rf "${TEST_DIR}/vault/logs"
sudo rm -Rf "${TEST_DIR}/vault/file"
sudo rm -Rf "${TEST_DIR}/dataregistry"
sudo rm -Rf "${TEST_DIR}/gogs-data/gogs.db"
sudo rm -Rf "${TEST_DIR}/gogs-data/data"
sudo rm -Rf "${TEST_DIR}/gogs-data/log"
print_success "Cleanup complete."
