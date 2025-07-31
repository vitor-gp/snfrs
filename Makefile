.PHONY: help build run dev test lint clean install docker-build docker-run docker-dev

# Default target
help:
	@echo "Available commands:"
	@echo "  install     - Install dependencies"
	@echo "  dev         - Run development server"
	@echo "  test        - Run tests"
	@echo "  lint        - Run linting tools"
	@echo "  clean       - Clean up temporary files"
	@echo "  db-reset    - Reset database files"
	@echo "  setup-env   - Setup environment variables (.env file)"
	@echo "  setup-dev   - Setup development environment"
	@echo "  setup-docker- Setup Docker environment"
	@echo "  docker-build- Build Docker images"
	@echo "  docker-run  - Run production containers (API + Discord bot)"
	@echo "  docker-dev  - Run development containers (API + Discord bot)"
	@echo "  docker-run-api - Run only API container"
	@echo "  docker-run-discord - Run only Discord bot container"

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
	docker compose build

docker-run: docker-build
	docker compose up api discord-bot

docker-dev: docker-build
	docker compose up api-dev discord-bot-dev

docker-run-api:
	docker compose up api

docker-run-discord:
	docker compose up discord-bot

docker-down:
	docker compose down

# Database commands
db-reset:
	rm -f data/*.db
	@echo "Database files removed. The application will create new ones on startup."

# Environment setup
setup-env:
	./setup-env.sh

# Setup development environment
setup-dev: install setup-env db-reset
	mkdir -p data
	@echo "Development environment setup complete!"
	@echo "Run 'make dev' to start the development server"

# Setup Docker environment
setup-docker: docker-build setup-env
	mkdir -p data
	@echo "Docker environment setup complete!"
	@echo "Run 'make docker-run' to start production containers"
	@echo "Run 'make docker-dev' to start development containers"