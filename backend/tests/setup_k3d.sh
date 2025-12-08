#!/bin/bash

set -e # Exit on any error

# Colors for output
YELLOW='\033[1;33m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Helper functions
print_header() { echo -e "\n${YELLOW}==========================================${NC}\n$1\n${YELLOW}==========================================${NC}"; }
print_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
print_info() { echo -e "${BLUE}[INFO]${NC} $1"; }

# --- Dynamically generate TLS certificate for registry ---
print_header "Generating TLS certificate for test registry"

# Wait for registry container to be running
sleep 3

# Get registry container IP
REGISTRY_IP=$(docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' dev-registry 2>/dev/null || echo "")

if [ -z "$REGISTRY_IP" ]; then
  echo "Error: dev-registry container not found or not running. Please ensure docker compose is up."
  exit 1
fi

echo "Registry IP detected: $REGISTRY_IP"

# Check if certificate already exists and matches current IP
CERT_SAN=$(openssl x509 -in certs/domain.crt -noout -text 2>/dev/null | grep -A1 "Subject Alternative Name" | grep "IP:" | cut -d: -f2 | tr -d ' ' || echo "")

if [ "$CERT_SAN" = "$REGISTRY_IP" ]; then
  echo "Certificate already exists with correct IP ($REGISTRY_IP), skipping regeneration."
else
  echo "Generating new certificate with IP $REGISTRY_IP in SAN..."

  # Ensure certs directory exists
  mkdir -p certs

  # Generate certificate with dynamic IP in SAN
  openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout certs/domain.key \
    -out certs/domain.crt \
    -subj "/C=US/ST=State/L=City/O=Organization/OU=OrgUnit/CN=test-registry.test.local" \
    -addext "subjectAltName=DNS:harmonisation.docker,DNS:host.k3d.internal,DNS:test-registry.test.local,DNS:localhost,IP:$REGISTRY_IP"

  echo "Certificate generated successfully."

  # Restart registry to load new certificate
  echo "Restarting registry container with new certificate..."
  docker restart dev-registry
  sleep 5
fi

print_success "TLS certificate ready with IP: $REGISTRY_IP"

# --- Cluster 1: APPS ---
CLUSTER_NAME_APPS="test-cluster"
CONTEXT_NAME_APPS="RKE2-APPS"
CONFIG_FILE_APPS="k3d-config.yaml"

# Check if the APPS cluster already exists
if ! k3d cluster get "$CLUSTER_NAME_APPS" >/dev/null 2>&1; then
  echo "Creating k3d cluster '$CLUSTER_NAME_APPS' for APPS..."
  k3d cluster create --config "$CONFIG_FILE_APPS" --wait --registry-config registries.yaml
else
  echo "k3d cluster '$CLUSTER_NAME_APPS' already exists."
fi

# Rename the context for the APPS cluster
echo "Renaming kubectl context for APPS cluster to '$CONTEXT_NAME_APPS'..."
kubectl config rename-context "k3d-$CLUSTER_NAME_APPS" "$CONTEXT_NAME_APPS" || echo "Warning: Could not rename context 'k3d-$CLUSTER_NAME_APPS'. It might already be named correctly."

# --- Cluster 2: MIDDLEWARE ---
CLUSTER_NAME_MW="test-cluster-mw"
CONTEXT_NAME_MW="RKE2-MIDDLEWARE"
CONFIG_FILE_MW="k3d-config-mw.yaml"

# Check if the MIDDLEWARE cluster already exists
if ! k3d cluster get "$CLUSTER_NAME_MW" >/dev/null 2>&1; then
  echo "Creating k3d cluster '$CLUSTER_NAME_MW' for MIDDLEWARE..."
  k3d cluster create --config "$CONFIG_FILE_MW" --wait --registry-config registries.yaml
else
  echo "k3d cluster '$CLUSTER_NAME_MW' already exists."
fi

# Rename the context for the MIDDLEWARE cluster
echo "Renaming kubectl context for MIDDLEWARE cluster to '$CONTEXT_NAME_MW'..."
kubectl config rename-context "k3d-$CLUSTER_NAME_MW" "$CONTEXT_NAME_MW" || echo "Warning: Could not rename context 'k3d-$CLUSTER_NAME_MW'. It might already be named correctly."

# --- Finalizing ---
echo "Setting current context to '$CONTEXT_NAME_APPS'..."
kubectl config use-context "$CONTEXT_NAME_APPS"

echo "Cluster setup complete."
echo "Current context: $(kubectl config current-context)"
echo "Available contexts:"
kubectl config get-contexts -o name

# --- Connect k3d clusters to tests_default network for registry access ---
print_header "Connecting k3d clusters to tests_default network"

# Wait for containers to be fully up
sleep 2

# Connect k3d nodes to tests_default network so they can reach the registry
echo "Connecting k3d-test-cluster-server-0 to tests_default..."
docker network connect tests_default k3d-test-cluster-server-0 2>/dev/null || true

echo "Connecting k3d-test-cluster-serverlb to tests_default..."
docker network connect tests_default k3d-test-cluster-serverlb 2>/dev/null || true

echo "Connecting k3d-test-cluster-mw-server-0 to tests_default..."
docker network connect tests_default k3d-test-cluster-mw-server-0 2>/dev/null || true

echo "Connecting k3d-test-cluster-mw-serverlb to tests_default..."
docker network connect tests_default k3d-test-cluster-mw-serverlb 2>/dev/null || true

# Add /etc/hosts entries for registry DNS resolution
echo "Adding registry DNS entries to k3d nodes..."

if [ -n "$REGISTRY_IP" ]; then
  # Add entries to all k3d nodes
  echo "Adding to k3d-test-cluster-server-0..."
  docker exec k3d-test-cluster-server-0 sh -c "echo '$REGISTRY_IP test-registry.test.local' >> /etc/hosts" 2>/dev/null || true

  echo "Adding to k3d-test-cluster-serverlb..."
  docker exec k3d-test-cluster-serverlb sh -c "echo '$REGISTRY_IP test-registry.test.local' >> /etc/hosts" 2>/dev/null || true

  echo "Adding to k3d-test-cluster-mw-server-0..."
  docker exec k3d-test-cluster-mw-server-0 sh -c "echo '$REGISTRY_IP test-registry.test.local' >> /etc/hosts" 2>/dev/null || true

  echo "Adding to k3d-test-cluster-mw-serverlb..."
  docker exec k3d-test-cluster-mw-serverlb sh -c "echo '$REGISTRY_IP test-registry.test.local' >> /etc/hosts" 2>/dev/null || true

  print_success "k3d clusters connected to tests_default network and DNS configured with IP: $REGISTRY_IP"
else
  print_warning "Registry IP not available. Network connection may need to be done manually."
fi

print_header "Setup Complete!"
print_success "All k3d clusters are ready."

