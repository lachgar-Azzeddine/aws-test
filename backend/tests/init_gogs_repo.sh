#!/bin/bash
#
# Gogs Repository Initialization Script
# This script creates the required repository in Gogs for testing
#

set -e

GOGS_CONTAINER="dev-gogs"
GOGS_URL="https://localhost:443"
ADMIN_USER="devops"
ADMIN_PASSWORD="devops"
REPO_NAME="harmonisation"

echo "=========================================="
echo "Initializing Gogs Repository"
echo "=========================================="

# Wait for Gogs to be ready
echo "Waiting for Gogs to be ready..."
for i in {1..30}; do
  if docker exec "${GOGS_CONTAINER}" /app/gogs/gogs admin --help >/dev/null 2>&1; then
    echo "✓ Gogs CLI is accessible"
    break
  fi
  if [ $i -eq 30 ]; then
    echo "✗ Gogs CLI not responding after 30 attempts"
    exit 1
  fi
  echo "  Waiting... ($i/30)"
  sleep 2
done

# Give Gogs a moment to fully initialize
sleep 3

# Create admin user via CLI (this initializes the database if empty)
echo "Creating admin user via Gogs CLI..."
docker exec -u git "${GOGS_CONTAINER}" /app/gogs/gogs admin create-user \
  --admin \
  --name="${ADMIN_USER}" \
  --email="admin@test.local" \
  --password="${ADMIN_PASSWORD}" \
  --admin=true 2>/dev/null || echo "  Admin user may already exist"

sleep 2

# Retrieve Gogs API token
echo "Retrieving Gogs API token..."
TOKEN_NAME="apitoken-$(date +%s)"
RETRY_COUNT=0
MAX_RETRIES=10
while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
  # Use a temporary file for the response to avoid polluting stdout
  API_RESPONSE_FILE=$(mktemp)
  HTTP_CODE=$(curl -k -s -w "%{http_code}" -X POST "${GOGS_URL}/api/v1/users/${ADMIN_USER}/tokens" \
    -H "Content-Type: application/json" \
    -u "${ADMIN_USER}:${ADMIN_PASSWORD}" \
    -d '''{"name": "'''"${TOKEN_NAME}"'''"}''' \
    -o "${API_RESPONSE_FILE}")

  API_RESPONSE=$(cat "${API_RESPONSE_FILE}")
  rm -f "${API_RESPONSE_FILE}"

  if [ "$HTTP_CODE" -eq 201 ] || [ "$HTTP_CODE" -eq 200 ]; then
    GOGS_API_TOKEN=$(echo "$API_RESPONSE" | grep -o '''"sha1": *"[^"]*"''' | cut -d'"' -f4)
    if [ -n "$GOGS_API_TOKEN" ]; then
      echo "✓ Gogs API token retrieved"
      break
    fi
  fi

  RETRY_COUNT=$((RETRY_COUNT + 1))
  echo "  Waiting for API to be ready... ($RETRY_COUNT/$MAX_RETRIES)"
  echo "  HTTP Code: $HTTP_CODE"
  echo "  Response: $(echo $API_RESPONSE | head -c 200)"
  sleep 3
done

if [ -z "$GOGS_API_TOKEN" ]; then
  echo "✗ Failed to retrieve Gogs API token"
  exit 1
fi

# Create the repository
echo "Creating harmonisation repository..."
RETRY_COUNT=0
MAX_RETRIES=10
while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
  RESPONSE=$(curl -k -s -X POST "${GOGS_URL}/api/v1/user/repos" \
    -H "Content-Type: application/json" \
    -H "Authorization: token ${GOGS_API_TOKEN}" \
    -d "{
        \"name\": \"${REPO_NAME}\",
        \"description\": \"Harmonisation repository for SRM-CS\",
        \"private\": false
      }" 2>&1)

  if echo "$RESPONSE" | grep -q "already exists\|duplicate"; then
    echo "  Repository already exists"
    break
  elif echo "$RESPONSE" | grep -q "name\|id\|full_name"; then
    echo "✓ Repository created"
    break
  else
    RETRY_COUNT=$((RETRY_COUNT + 1))
    echo "  Waiting for API... ($RETRY_COUNT/$MAX_RETRIES)"
    echo "  Response: $(echo $RESPONSE | head -c 200)"
    sleep 2
  fi
done

# Verify repository exists
sleep 2
echo "Verifying repository..."
HTTP_CODE=$(curl -k -s -o /dev/null -w "%{http_code}" "${GOGS_URL}/${ADMIN_USER}/${REPO_NAME}")
if [ "$HTTP_CODE" = "200" ]; then
  echo "✓ Repository ${ADMIN_USER}/${REPO_NAME} is accessible (HTTP $HTTP_CODE)"
elif [ "$HTTP_CODE" = "404" ]; then
  echo "⚠ Repository not found (HTTP $HTTP_CODE)"
else
  echo "⚠ Repository returned HTTP $HTTP_CODE"
fi

# Test git clone
echo "Testing git clone..."
# We need to provide credentials for cloning
if git clone --config http.sslVerify=false "https://${ADMIN_USER}:${ADMIN_PASSWORD}@localhost:443/${ADMIN_USER}/${REPO_NAME}.git" /tmp/test-gogs-clone; then
  echo "✓ Git clone successful"
  rm -rf /tmp/test-gogs-clone
else
  echo "⚠ Git clone failed"
fi


echo ""
echo "=========================================="
echo "Gogs Repository Initialization Complete!"
echo "=========================================="
echo "Repository URL: ${GOGS_URL}/${ADMIN_USER}/${REPO_NAME}"
echo "Clone URL (HTTPS): https://localhost:443/${ADMIN_USER}/${REPO_NAME}.git"
echo ""