#!/bin/bash
set -e

echo "Running database initialization script..."

python /home/devops/initial_db.py

exec "$@"

