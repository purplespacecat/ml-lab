#!/bin/bash
set -e

# Install dependencies
echo "Installing dependencies..."
apt-get update > /dev/null 2>&1
apt-get install -y curl > /dev/null 2>&1
pip install mlflow==2.9.2 psycopg2-binary boto3 > /dev/null 2>&1

echo "Starting MLflow server..."
# Start MLflow server with host binding
exec mlflow server \
    --backend-store-uri "${MLFLOW_BACKEND_STORE_URI}" \
    --default-artifact-root "${MLFLOW_DEFAULT_ARTIFACT_ROOT}" \
    --host 0.0.0.0 \
    --port 5000 \
    --workers 4
