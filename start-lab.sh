#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if a service is responding
check_service() {
    local url=$1
    local name=$2
    local max_attempts=30
    local attempt=0

    while [ $attempt -lt $max_attempts ]; do
        if curl -s -f -o /dev/null "$url"; then
            print_success "$name is responding at $url"
            return 0
        fi
        attempt=$((attempt + 1))
        sleep 2
    done

    print_error "$name failed to respond at $url"
    return 1
}

echo ""
print_status "Starting ML Lab environment..."
echo ""

# Check if docker-compose is available
if ! command -v docker-compose &> /dev/null; then
    print_error "docker-compose is not installed or not in PATH"
    exit 1
fi

# Check if .env file exists
if [ ! -f .env ]; then
    print_warning ".env file not found"
    if [ -f .env.example ]; then
        print_status "Creating .env from .env.example"
        cp .env.example .env
        print_success ".env file created"
    else
        print_warning "No .env.example file found, using default values"
    fi
fi

# Stop any existing containers
print_status "Stopping any existing containers..."
docker-compose down 2>/dev/null

echo ""
print_status "Starting infrastructure services (PostgreSQL, MinIO)..."
docker-compose up -d postgres minio

echo ""
print_status "Waiting for infrastructure to be healthy..."
sleep 5

# Wait for PostgreSQL
print_status "Checking PostgreSQL..."
while ! docker-compose exec -T postgres pg_isready -U mlflow &>/dev/null; do
    echo -n "."
    sleep 1
done
print_success "PostgreSQL is ready"

# Wait for MinIO
print_status "Checking MinIO..."
while ! curl -s -f http://localhost:9000/minio/health/live &>/dev/null; do
    echo -n "."
    sleep 1
done
print_success "MinIO is ready"

# Initialize MinIO bucket
echo ""
print_status "Initializing MinIO bucket..."
docker-compose up -d minio-init
sleep 3
print_success "MinIO bucket initialized"

# Start MLflow server
echo ""
print_status "Starting MLflow tracking server..."
docker-compose up -d mlflow

print_status "Waiting for MLflow to be ready..."
sleep 5
while ! curl -s -f http://localhost:5000/health &>/dev/null; do
    echo -n "."
    sleep 2
done
print_success "MLflow server is ready"

# Start model server
echo ""
print_status "Starting model server..."
docker-compose up -d model-server

print_status "Waiting for model server to be ready..."
sleep 5
if check_service "http://localhost:8000" "Model API"; then
    :
else
    print_warning "Model server may not be fully ready. Check logs with: docker-compose logs model-server"
fi

# Start Gradio UI
echo ""
print_status "Starting Gradio UI..."
docker-compose up -d gradio-ui

print_status "Waiting for Gradio UI to be ready..."
sleep 5
if check_service "http://localhost:7860" "Gradio UI"; then
    :
else
    print_warning "Gradio UI may have issues. Check logs with: docker-compose logs gradio-ui"
fi

# Print final status
echo ""
echo "========================================"
print_success "ML Lab startup complete!"
echo "========================================"
echo ""

# Show service status
print_status "Service Status:"
docker-compose ps

echo ""
print_status "Available Services:"
echo ""
echo "  📊 MLflow UI:      http://localhost:5000"
echo "  🗄️  MinIO Console:  http://localhost:9001"
echo "     Credentials:   minioadmin / minioadmin"
echo "  🚀 Model API:      http://localhost:8000"
echo "     API Docs:      http://localhost:8000/docs"
echo "  🎮 Gradio UI:      http://localhost:7860"
echo ""

print_status "Useful Commands:"
echo "  - View logs:       docker-compose logs -f [service-name]"
echo "  - Stop services:   docker-compose down"
echo "  - Restart service: docker-compose restart [service-name]"
echo ""

# Check if model exists
print_status "Checking for trained model..."
if docker-compose exec -T mlflow sh -c "curl -s http://localhost:5000/api/2.0/mlflow/registered-models/get?name=dnd-character-classifier" 2>/dev/null | grep -q "dnd-character-classifier"; then
    print_success "Model 'dnd-character-classifier' found in registry"
else
    print_warning "No model found in registry"
    echo ""
    print_status "To train a model, run:"
    echo "  cd src && python train.py"
    echo "  OR"
    echo "  docker-compose run --rm model-server python src/train.py"
fi

echo ""
