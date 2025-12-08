#!/bin/bash

# Define container name
CONTAINER_NAME="backend"

# Define Terraform directories
INFRA_DIR="/home/devops/terraform/infra"
APPS_DIR="/home/devops/terraform/apps"
DMZ_DIR="/home/devops/terraform/dmz"

# Function to execute Terraform destroy inside the container
terraform_destroy() {
  local dir=$1
  echo "Executing terraform destroy in $dir..."
  docker compose exec -it "$CONTAINER_NAME" bash -c "cd $dir && terraform destroy"
}

docker compose up -d backend
# Run terraform destroy on both directories
terraform_destroy "$INFRA_DIR"
terraform_destroy "$APPS_DIR"
terraform_destroy "$DMZ_DIR"

echo "Terraform destroy completed for both directories."
docker compose down -v
sudo rm -Rf data
