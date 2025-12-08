#!/bin/bash

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

for image in *.tar; do
  if [ -f "$image" ]; then
    echo "Loading image: $image"
    docker load -i "$image"
  else
    echo "No .tar files found"
  fi
done

# Function to retry a command
retry_command() {
  local command="$1"
  local max_retries=20
  local retry_count=0

  while [ $retry_count -lt $max_retries ]; do
    echo "Running: $command"
    eval "$command"
    if [ $? -eq 0 ]; then
      echo "Command succeeded."
      return 0
    else
      retry_count=$((retry_count + 1))
      echo "Command failed. Retrying ($retry_count/$max_retries)..."
      sleep 2 # Add a small delay before retrying
    fi
  done

  echo "Command failed after $max_retries retries."
  return 1
}

# # Step 2: Change permissions and unzip the file
# echo "Changing permissions and unzipping the file..."
# sudo chmod 777 "$ZIP_FILE"
# unzip "$ZIP_FILE" -d "$HOME/tests/"

# # Step 3: Change permissions of the extracted directory
# echo "Changing permissions of the extracted directory..."
# sudo chmod -R 777 "$EXTRACTED_DIR"

# Step 4: Navigate to the extracted folder and create the required directories
echo "Creating required directories..."
mkdir -p data/terraform/infra
mkdir -p data/terraform/apps
mkdir -p data/terraform/dmz
mkdir -p data/.ssh
mkdir -p data/.kube
mkdir -p data/env
mkdir -p data/db
mkdir -p data/inventory
mkdir -p data/images

# Step 5: Change permissions of the data directory
echo "Changing permissions of the data directory..."
sudo chmod -R 777 data
sudo chown -R devops:devops data

# Step 6: Print the directories created
echo "Listing created directories..."
ls -a data

# # Removing existing containers...
# docker rm --force backend frontend
# # Step 7: Docker compose down with retry
# echo "Running docker-compose down..."
# docker compose down

# Step 8: Docker compose up -d with retry
echo "Running docker-compose up -d..."
docker compose up -d

echo "Script completed successfully."
