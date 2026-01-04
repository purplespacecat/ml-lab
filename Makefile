.PHONY: help setup up down train serve ui logs clean

help:
	@echo "Available commands:"
	@echo "  make setup    - Create .env file from template"
	@echo "  make up       - Start all services"
	@echo "  make down     - Stop all services"
	@echo "  make train    - Train the model locally"
	@echo "  make logs     - View all service logs"
	@echo "  make clean    - Stop services and remove volumes"
	@echo "  make status   - Check service health"

setup:
	@if [ ! -f .env ]; then \
		cp .env.example .env; \
		echo "✓ Created .env file"; \
	else \
		echo "✓ .env file already exists"; \
	fi

up: setup
	@echo "Starting all services..."
	docker-compose up -d
	@echo "Waiting for services to be healthy..."
	@sleep 5
	@echo ""
	@echo "Services started!"
	@echo "  MLflow UI:    http://localhost:5000"
	@echo "  MinIO Console: http://localhost:9001"
	@echo "  Model API:    http://localhost:8000"
	@echo "  Gradio UI:    http://localhost:7860"

down:
	@echo "Stopping all services..."
	docker-compose down

train:
	@echo "Training model locally..."
	@if [ ! -d "venv" ]; then \
		echo "Creating virtual environment..."; \
		python3 -m venv venv; \
		./venv/bin/pip install -r requirements.txt; \
	fi
	./venv/bin/python src/train.py

logs:
	docker-compose logs -f

status:
	@echo "Service Status:"
	@docker-compose ps

clean:
	@echo "Stopping services and removing volumes..."
	docker-compose down -v
	@echo "Cleaned!"

restart:
	@make down
	@make up
