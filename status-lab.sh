#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

echo ""
print_status "ML Lab Status Check"
echo "========================================"
echo ""

# Check container status
print_status "Container Status:"
docker-compose ps
echo ""

# Check service endpoints
print_status "Service Health:"
echo ""

check_endpoint() {
    local url=$1
    local name=$2
    if curl -s -f -o /dev/null "$url"; then
        echo -e "  ${GREEN}✓${NC} $name - $url"
    else
        echo -e "  ${RED}✗${NC} $name - $url"
    fi
}

check_endpoint "http://localhost:5000/health" "MLflow UI      "
check_endpoint "http://localhost:9001" "MinIO Console  "
check_endpoint "http://localhost:8000" "Model API      "
check_endpoint "http://localhost:7860" "Gradio UI      "

echo ""
print_status "To view logs for a specific service:"
echo "  docker-compose logs -f [service-name]"
echo ""
print_status "Available services: postgres, minio, mlflow, model-server, gradio-ui"
echo ""
