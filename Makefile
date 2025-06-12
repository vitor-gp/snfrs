.PHONY: help build run dev test lint clean install docker-build docker-run docker-dev

# Default target
help:
	@echo "Available commands:"
	@echo "  install     - Install dependencies"
	@echo "  dev         - Run development server"
	@echo "  test        - Run tests"
	@echo "  lint        - Run linting tools"
	@echo "  clean       - Clean up temporary files"
	@echo "  docker-build- Build Docker image"
	@echo "  docker-run  - Run production container"
	@echo "  docker-dev  - Run development container"

# Install dependencies
install:
	pip install --upgrade pip
	pip install -r requirements.txt

# Run development server
dev:
	uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Run tests
test:
	pytest tests/ -v --cov=app --cov-report=term-missing

# Run linting
lint:
	black app/ tests/ --check
	isort app/ tests/ --check-only
	flake8 app/ tests/
	mypy app/

# Format code
format:
	black app/ tests/
	isort app/ tests/

# Clean up
clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type f -name ".coverage" -delete
	find . -type d -name "htmlcov" -exec rm -rf {} +
	find . -name "*.db" -delete

# Docker commands
docker-build:
	docker-compose build

docker-run:
	docker-compose up api

docker-dev:
	docker-compose up api-dev

docker-down:
	docker-compose down

# Setup development environment
setup-dev: install
	mkdir -p data
	@echo "Development environment setup complete!"
	@echo "Run 'make dev' to start the development server" 