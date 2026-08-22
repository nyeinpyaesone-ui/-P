# ERP03 Makefile - Development & Production Commands

.PHONY: help bootstrap build up down logs clean test lint format install dev

# Default target
help:
	@echo "ERP03 Makefile - Available Commands:"
	@echo ""
	@echo "  bootstrap    - Run the full bootstrap orchestrator"
	@echo "  build        - Build all Docker containers"
	@echo "  up           - Start all services"
	@echo "  down         - Stop all services"
	@echo "  restart      - Restart all services"
	@echo "  logs         - View logs from all services"
	@echo "  logs-erp     - View ERP backend logs only"
	@echo "  logs-db      - View database logs only"
	@echo "  clean        - Remove containers and volumes"
	@echo "  test         - Run tests"
	@echo "  lint         - Run linter"
	@echo "  format       - Format code"
	@echo "  install      - Install Python dependencies"
	@echo "  dev          - Start development environment"
	@echo ""

# Bootstrap the entire system
bootstrap:
	python scripts/bootstrap.py

# Force re-bootstrap
bootstrap-force:
	python scripts/bootstrap.py --force

# Build all containers
build:
	docker compose build --parallel

# Build specific service
build-%:
	docker compose build $*

# Start all services
up:
	docker compose up -d

# Start with logs
up-logs:
	docker compose up

# Stop all services
down:
	docker compose down

# Restart all services
restart:
	docker compose restart

# View logs
logs:
	docker compose logs -f

# View ERP backend logs
logs-erp:
	docker compose logs -f erp-backend

# View database logs
logs-db:
	docker compose logs -f postgres redis rabbitmq

# Clean everything
clean:
	docker compose down -v --remove-orphans
	rm -f .bootstrap.completed .bootstrap.running.lock

# Run tests
test:
	docker compose run --rm erp-backend python -m pytest apps/ -v

# Run linter
lint:
	docker compose run --rm erp-backend python -m flake8 apps/

# Format code
format:
	docker compose run --rm erp-backend python -m black apps/

# Install dependencies locally
install:
	pip install -r requirements.txt

# Development mode
dev:
	docker compose up -d postgres redis rabbitmq
	python scripts/bootstrap.py --repair-packages

# Database migrations
migrate:
	docker compose run --rm erp-backend python -m alembic -c apps/erp/alembic.ini upgrade head

# Create migration
migration-%:
	docker compose run --rm erp-backend python -m alembic -c apps/erp/alembic.ini revision --autogenerate -m "$*"

# Seed database
seed:
	docker compose run --rm erp-backend python -c "from apps.erp.engine.commands.seed import seed_database; seed_database()"

# Health check
health:
	@echo "Checking service health..."
	docker compose ps
	@echo ""
	@echo "Testing endpoints..."
	@echo "ERP Backend: http://localhost:8000/healthz"
	@echo "AI Platform: http://localhost:8001/healthz"
	@echo "Admin UI:    http://localhost:3000"
	@echo "Client UI:   http://localhost:3001"
