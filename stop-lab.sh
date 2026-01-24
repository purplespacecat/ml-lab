#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

echo ""
print_status "Stopping ML Lab environment..."
echo ""

# Stop all services
docker-compose down

print_success "All services stopped"
echo ""

print_status "To completely remove all data (volumes), run:"
echo "  docker-compose down -v"
echo ""
