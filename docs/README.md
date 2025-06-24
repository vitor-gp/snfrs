# SNFRS Documentation

Welcome to the SNFRS (Social Network for Real-world Social events) documentation. This directory contains comprehensive documentation for the project organized by category.

## 📚 Documentation Structure

### API Documentation
- **[API Reference](api/API_REFERENCE.md)** - Complete API endpoints documentation with request/response examples

### Development
- **[Development Guide](development/DEVELOPMENT_GUIDE.md)** - Setup, development workflow, and contribution guidelines
- **[System Context](development/SYSTEM_CONTEXT.md)** - Architecture overview and system design

### Deployment
- **[Deployment Guide](deployment/DEPLOYMENT_GUIDE.md)** - Production deployment, Docker, and environment setup

### Examples
- **[Discord Bot Example](examples/discord_bot_example.py)** - Example Discord bot implementation
- **[Legacy Discord Bot](examples/discord_bot_legacy.py)** - Previous monolithic implementation (for reference)

## 🚀 Quick Start

1. **For Developers**: Start with the [Development Guide](development/DEVELOPMENT_GUIDE.md)
2. **For Deployment**: Check the [Deployment Guide](deployment/DEPLOYMENT_GUIDE.md)
3. **For API Integration**: Check the [API Reference](api/API_REFERENCE.md)
4. **For System Understanding**: Read the [System Context](development/SYSTEM_CONTEXT.md)

## 📁 Project Structure

```
snfrs/
├── app/                    # FastAPI application
├── bot/                    # Discord bot package
├── tests/                  # Test suite
├── docs/                   # Documentation (this directory)
│   ├── api/               # API documentation
│   ├── development/       # Development guides
│   ├── deployment/        # Deployment and production guides
│   └── examples/          # Code examples and legacy files
├── alembic/               # Database migrations
├── data/                  # Database files
├── docker-compose.yml     # Docker services configuration
├── Dockerfile.api         # API container definition
├── Dockerfile.discord     # Discord bot container definition
├── Makefile              # Development commands
├── requirements.txt      # API dependencies
└── requirements.discord.txt # Discord bot dependencies
```

## 🔧 Development Commands

```bash
# Start development environment
make dev

# Run with Docker
make docker-run

# Run tests
make test

# Clean up
make clean
```

## 📞 Support

For questions or issues, please check the existing documentation or create an issue in the repository. 