#!/bin/bash
#
# Push Docker Images to Test Registry
#
# This script loads Docker images from tar files and pushes them to the test registry.
# The registry should be running at localhost:8443 with basic authentication.
#

set -e # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
REGISTRY_URL="localhost:8443"
REGISTRY_USER="devops"
REGISTRY_PASS="devops"
IMAGES_DIR="${1:-./tests/data/images}"
ROLE_NAME="${2:-install-gravitee-lan}"

# Get the directory of the script
SCRIPT_DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" &>/dev/null && pwd)
ROLES_DIR="${SCRIPT_DIR}/../project/roles"

# Function to print colored output
print_info() {
  echo -e "${GREEN}[INFO]${NC} $1"
}

print_error() {
  echo -e "${RED}[ERROR]${NC} $1"
}

print_warning() {
  echo -e "${YELLOW}[WARN]${NC} $1"
}

# Function to login to the registry
login_to_registry() {
  print_info "Logging into registry at ${REGISTRY_URL}..."

  # Create a temporary file for docker login output
  LOGIN_OUTPUT=$(mktemp)

  # Login to the registry
  if echo "${REGISTRY_PASS}" | docker login ${REGISTRY_URL} --username ${REGISTRY_USER} --password-stdin 2>&1 | tee ${LOGIN_OUTPUT}; then
    print_info "✓ Successfully logged into registry"
    rm -f ${LOGIN_OUTPUT}
    return 0
  else
    print_error "✗ Failed to login to registry"
    print_error "See ${LOGIN_OUTPUT} for details"
    return 1
  fi
}

# Function to check if registry is accessible
check_registry() {
  print_info "Checking if registry is accessible at ${REGISTRY_URL}..."

  if docker info --format '{{.ServerVersion}}' 2>/dev/null >/dev/null; then
    # Check if we can access the registry
    if curl -k -s -o /dev/null -w "%{http_code}" https://${REGISTRY_URL}/v2/ | grep -q "200\|401"; then
      print_info "✓ Registry is accessible"
      return 0
    else
      print_warning "Registry returned unexpected response"
      return 1
    fi
  else
    print_error "Docker is not running or not accessible"
    return 1
  fi
}

# Function to push images for a specific role
push_role_images() {
  local role=$1
  local images_file="${ROLES_DIR}/${role}/images.txt"

  print_info "Processing role: ${role}"
  echo "  Images file: ${images_file}"

  if [ ! -f "${images_file}" ]; then
    print_warning "Images file not found: ${images_file}"
    return 1
  fi

  local pushed_count=0
  local skipped_count=0
  local failed_count=0

  # Read images from the file
  while IFS= read -r image || [ -n "$image" ]; do
    # Skip empty lines
    [ -z "$image" ] && continue

    print_info "Processing image: ${image}"

    # Sanitize image name for tar file
    sanitized_name=$(echo "${image}" | tr '/' '_')
    tar_file="${IMAGES_DIR}/${sanitized_name}.tar"

    # Check if tar file exists
    if [ ! -f "${tar_file}" ]; then
      print_warning "  Tar file not found: ${tar_file}"
      failed_count=$((failed_count + 1))
      continue
    fi

    # Check if image already exists in registry
    if docker manifest inspect ${REGISTRY_URL}/${image} &>/dev/null; then
      print_info "  Image already exists in registry, skipping"
      skipped_count=$((skipped_count + 1))
      continue
    fi

    # Load the image from tar
    print_info "  Loading image from ${tar_file}..."
    if ! docker load -i "${tar_file}"; then
      print_error "  Failed to load image from ${tar_file}"
      failed_count=$((failed_count + 1))
      continue
    fi

    # Tag the image for the registry
    print_info "  Tagging image for registry..."
    if ! docker tag "${image}" "${REGISTRY_URL}/${image}"; then
      print_error "  Failed to tag image"
      failed_count=$((failed_count + 1))
      continue
    fi

    # Push the image
    print_info "  Pushing image to registry..."
    if ! docker push "${REGISTRY_URL}/${image}"; then
      print_error "  Failed to push image to registry"
      failed_count=$((failed_count + 1))
      continue
    fi

    print_info "  ✓ Successfully pushed ${image}"
    pushed_count=$((pushed_count + 1))

  done <"${images_file}"

  # Print summary
  echo ""
  print_info "Role ${role} summary:"
  echo "  Pushed: ${pushed_count}"
  echo "  Skipped: ${skipped_count}"
  echo "  Failed: ${failed_count}"
  echo ""

  return 0
}

# Function to push all role images
push_all_role_images() {
  print_info "Looking for role images in: ${IMAGES_DIR}"

  if [ ! -d "${IMAGES_DIR}" ]; then
    print_error "Images directory not found: ${IMAGES_DIR}"
    print_info "Please run tar_images.py first to download and save images"
    return 1
  fi

  if [ "${ROLE_NAME}" = "all" ]; then
    # Push images for all roles
    for images_file in ${ROLES_DIR}/*/images.txt; do
      if [ -f "${images_file}" ]; then
        role_name=$(basename $(dirname "${images_file}"))
        push_role_images "${role_name}"
      fi
    done
  else
    # Push images for specific role
    push_role_images "${ROLE_NAME}"
  fi
}

# Main execution
main() {
  echo "=========================================="
  echo "Docker Images to Registry Pusher"
  echo "=========================================="
  echo ""

  # Check if images directory exists
  if [ ! -d "${IMAGES_DIR}" ]; then
    print_error "Images directory not found: ${IMAGES_DIR}"
    echo ""
    echo "Usage: $0 [IMAGES_DIR] [ROLE_NAME]"
    echo "  IMAGES_DIR: Directory containing tarred images (default: ./tests/data/images)"
    echo "  ROLE_NAME:  Specific role to process, or 'all' for all roles (default: install-gravitee-lan)"
    echo ""
    print_info "Please run tar_images.py first to download and save images:"
    echo "  python tar_images.py --role install-gravitee-lan ./tests/data/images"
    exit 1
  fi

  # Check if registry is accessible
  if ! check_registry; then
    print_error "Registry is not accessible. Please start the test environment:"
    print_info "  cd tests && docker compose up -d"
    exit 1
  fi

  # Login to registry
  if ! login_to_registry; then
    print_error "Failed to login to registry. Check credentials."
    exit 1
  fi

  # Push images
  push_all_role_images

  echo "=========================================="
  print_info "Image pushing complete!"
  echo "=========================================="
}

# Run main function
main "$@"
