#!/bin/bash

# A script to initialize and unseal a persistent development Vault server

# --- Configuration ---
VAULT_CONTAINER_NAME="vault"
CREDENTIALS_FILE=".vault-credentials"
DATA_DIR="./vault/file" # The directory mapped to /vault/file

# Check if Vault is already initialized by looking for data files
if [ "$(ls -A $DATA_DIR 2>/dev/null)" ]; then
  echo "Vault data found in '$DATA_DIR'. Vault appears to be already initialized."
  echo "To re-initialize, stop the container, delete everything in '$DATA_DIR', delete '$CREDENTIALS_FILE', and run this script again."
  # Optional: Automatically unseal if already initialized
  if [ -f "$CREDENTIALS_FILE" ]; then
    echo "Unsealing existing Vault..."
    UNSEAL_KEY=$(grep 'VAULT_UNSEAL_KEY' $CREDENTIALS_FILE | cut -d'=' -f2)
    docker compose exec $VAULT_CONTAINER_NAME vault operator unseal "$UNSEAL_KEY"
  fi
  exit 0
fi

echo "No Vault data found. Initializing a new Vault server..."
echo "Starting Vault container..."
docker compose up -d

# Wait for Vault to become available
echo "Waiting for Vault to start..."
sleep 5

echo "Initializing Vault..."
# Initialize with 1 key share and a threshold of 1 for simplicity in dev
# Output the result in JSON format for easy parsing
init_output=$(docker compose exec $VAULT_CONTAINER_NAME vault operator init -key-shares=1 -key-threshold=1 -format=json)

if [ $? -ne 0 ]; then
  echo "Failed to initialize Vault. Please check the container logs."
  exit 1
fi

# Parse the JSON to get the unseal key and root token
unseal_key=$(echo "$init_output" | jq -r .unseal_keys_b64[0])
root_token=$(echo "$init_output" | jq -r .root_token)

if [ -z "$unseal_key" ] || [ -z "$root_token" ]; then
  echo "Error parsing initialization output. Could not find unseal key or root token."
  exit 1
fi

echo "Unsealing Vault..."
docker compose exec $VAULT_CONTAINER_NAME vault operator unseal "$unseal_key"

# Save the credentials to a file for easy access
echo "Saving credentials to $CREDENTIALS_FILE"
echo "VAULT_ROOT_TOKEN=$root_token" >$CREDENTIALS_FILE
echo "VAULT_UNSEAL_KEY=$unseal_key" >>$CREDENTIALS_FILE

echo "------------------------------------------"
echo "✅ Vault setup complete!"
echo "Your root token is: $root_token"
echo "It has been saved to the '$CREDENTIALS_FILE' file."
echo "------------------------------------------"
