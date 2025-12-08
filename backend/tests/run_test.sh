#!/bin/bash
#
# Gravitee Role Test Orchestration Script
#

set -e # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# --- Configuration ---
TEST_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$(dirname "$TEST_DIR")"
ROLE_NAME="install-gravitee-lan" # Default role to test
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

# --- Test Functions ---

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
  [ -f "${KUBECONFIG}" ] || {
    print_error "Kubeconfig not found at ${KUBECONFIG}"
    exit 1
  }
  print_success "All prerequisites met."
}

download_images() {
  print_header "2. Downloading Docker Images"
  mkdir -p "${IMAGES_DIR}"
  print_info "Downloading images for all necessary roles..."

  # Download for main role
  python3 "${BACKEND_DIR}/tar_images.py" --role "${ROLE_NAME}" "${IMAGES_DIR}"
  print_success "Image download process complete."
}

push_images_to_registry() {
  print_header "3. Pushing Images to Test Registry"
  # Push for main role
  "${TEST_DIR}/push_images_to_registry.sh" "${IMAGES_DIR}" "${ROLE_NAME}"
  print_success "Image push process complete."
}

run_role_tests() {
  print_header "4. Running Ansible Role Tests"

  print_info "Running main role: ${ROLE_NAME}"
  python3 "${BACKEND_DIR}/install.py" --role "${ROLE_NAME}"
  if [ $? -ne 0 ]; then
    print_error "Role test for '${ROLE_NAME}' failed."
    return 1
  fi

  print_success "All role tests passed for '${ROLE_NAME}'"
}

# cleanup() {
#   print_header "7. Cleaning Up"
#   cd "${TEST_DIR}"
#   # docker compose down -v --remove-orphans
#   rm -f "${DB_PATH}" "${SQLHOSTS_FILE}"
#   print_success "Cleanup complete."
# }

# --- Main Execution ---
main() {
  SKIP_IMAGES=false

  # Parse arguments
  while [[ $# -gt 0 ]]; do
    case $1 in
    -r | --role)
      ROLE_NAME="$2"
      shift 2
      ;;
    -s | --skip-images)
      SKIP_IMAGES=true
      shift
      ;;
    *)
      print_error "Unknown option: $1"
      exit 1
      ;;
    esac
  done

  print_header "Begin Ansible Role Test Suite"
  print_info "Role to test: ${ROLE_NAME}"

  # trap cleanup EXIT

  check_prerequisites

  if [ "$SKIP_IMAGES" = "false" ]; then
    download_images
  else
    print_info "Skipping image operations as requested via -s flag."
  fi

  push_images_to_registry

  run_role_tests

  print_header "Test Suite Finished Successfully!"
}

main "$@"
