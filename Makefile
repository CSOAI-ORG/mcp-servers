# MEOK AI Labs - Makefile
# Common development and deployment commands

.PHONY: help install dev test test-smoke test-stress test-e2e build up down logs clean deploy

# Default target
help:
	@echo "MEOK AI Labs - Available Commands"
	@echo "=================================="
	@echo ""
	@echo "Development:"
	@echo "  make install      - Install dependencies"
	@echo "  make dev         - Run development server"
	@echo "  make test        - Run all tests"
	@echo ""
	@echo "Testing:"
	@echo "  make test-smoke  - Run smoke tests"
	@echo "  make test-stress - Run stress tests"
	@echo "  make test-e2e    - Run E2E tests"
	@echo ""
	@echo "Infrastructure:"
	@echo "  make up          - Start infrastructure"
	@echo "  make down        - Stop infrastructure"
	@echo "  make logs        - View logs"
	@echo "  make clean       - Clean up containers/volumes"
	@echo ""
	@echo "Deployment:"
	@echo "  make build       - Build Docker images"
	@echo "  make deploy      - Deploy to Kubernetes"
	@echo ""

# Installation
install:
	@echo "Installing dependencies..."
	pip install -r api/requirements.txt
	pip install -r workers/requirements.txt
	cd packages/python/meokai && pip install -e .

# Development
dev:
	@echo "Starting development server..."
	uvicorn api.server:app --reload --host 0.0.0.0 --port 8000

dev-workers:
	@echo "Starting workers..."
	python -m workers.cli worker --workers 4

# Testing
test:
	@echo "Running all tests..."
	python scripts/smoke_test.py
	python scripts/stress_test.py --duration 10

test-smoke:
	@echo "Running smoke tests..."
	python scripts/smoke_test.py

test-stress:
	@echo "Running stress tests..."
	python scripts/stress_test.py --duration 30

test-e2e:
	@echo "Running E2E tests..."
	cd tests/playwright && npx playwright test

# Infrastructure
up:
	@echo "Starting infrastructure..."
	docker-compose -f docker-compose.infra.yml up -d

down:
	@echo "Stopping infrastructure..."
	docker-compose -f docker-compose.infra.yml down

logs:
	docker-compose -f docker-compose.infra.yml logs -f

clean:
	@echo "Cleaning up..."
	docker-compose -f docker-compose.infra.yml down -v
	docker system prune -f

# Docker
build:
	@echo "Building Docker images..."
	docker build -t meokai/api:latest ./api
	docker build -t meokai/workers:latest ./workers

# Deployment
deploy:
	@echo "Deploying to Kubernetes..."
	./scripts/deploy.sh production

# Monitoring
monitor:
	@echo "Starting health monitor..."
	python scripts/health-monitor.py

# Code quality
lint:
	@echo "Linting..."
	ruff check api/ workers/ scripts/
	ruff format --check api/ workers/ scripts/

format:
	@echo "Formatting..."
	ruff format api/ workers/ scripts/

# Database
db-migrate:
	@echo "Running migrations..."
	cd api && alembic upgrade head

db-reset:
	@echo "Resetting database..."
	docker-compose -f docker-compose.infra.yml exec postgres psql -U meok -d meokai -c "DROP SCHEMA public CASCADE; CREATE SCHEMA public;"
	cd api && alembic upgrade head

# Documentation
docs:
	@echo "Serving documentation..."
	@echo "See docs/ directory for documentation files"
