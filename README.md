# SNFRS - Social Network for Real-world Social events

A FastAPI-based event attendance tracking system with Discord bot integration and time-based attendance validation.

## 🚀 Quick Start

```bash
# Clone and setup
git clone <repository-url>
cd snfrs

# Start development environment
make dev

# Or with Docker
make docker-run
```

## ✨ Key Features

- **⏰ Time-Based Attendance**: Users can only attend events during their scheduled time window
- **🤖 Discord Integration**: Native Discord bot with slash commands
- **🔐 JWT Authentication**: Secure authentication for web users
- **📊 Event Management**: Create, update, and track events with real-time status
- **📈 Attendance Tracking**: Comprehensive attendance history and reporting

## 🏗️ Architecture

```
snfrs/
├── app/                    # FastAPI application
│   ├── main.py            # Application entry point
│   ├── routers/           # API endpoints
│   ├── models.py          # Database models
│   └── schemas.py         # API schemas
├── bot/                    # Discord bot package
│   ├── main.py            # Bot implementation
│   ├── cogs/              # Command groups
│   └── config.py          # Bot configuration
├── tests/                  # Test suite
├── docs/                   # Comprehensive documentation
└── docker-compose.yml     # Container orchestration
```

## 📚 Documentation

For comprehensive documentation, see the **[docs/](docs/)** directory:

- **[📖 Documentation Index](docs/README.md)** - Complete documentation overview
- **[🔧 Development Guide](docs/development/DEVELOPMENT_GUIDE.md)** - Setup and development workflow
- **[🌐 API Reference](docs/api/API_REFERENCE.md)** - Complete API documentation
- **[🏛️ System Context](docs/development/SYSTEM_CONTEXT.md)** - Architecture and design

## 🔧 Development Commands

```bash
# Development
make dev                    # Start development server
make test                   # Run test suite
make clean                  # Clean up containers and cache

# Docker
make docker-build          # Build containers
make docker-run            # Run with Docker Compose
make docker-dev            # Development with Docker

# Database
make db-migrate            # Run database migrations
make db-reset              # Reset database
```

## 🤖 Discord Bot

The Discord bot provides slash commands for event management:

- `/register` - Register for events
- `/events` - List active events  
- `/attend <event_id>` - Mark attendance
- `/create_event` - Create new event (admin)
- `/status` - View attendance history

## 🌐 API Endpoints

Key API endpoints:

- `POST /auth/register` - User registration
- `GET /events/active` - Active events
- `POST /events/{id}/attend` - Mark attendance
- `POST /discord/users/register` - Discord user registration

See **[API Reference](docs/api/API_REFERENCE.md)** for complete documentation.

## 🧪 Testing

```bash
# Run all tests
make test

# Run specific test files
pytest tests/test_events.py
pytest tests/test_auth.py
```

## 📦 Requirements

- **Python 3.11+**
- **FastAPI** - Web framework
- **Discord.py** - Discord bot library
- **SQLAlchemy** - Database ORM
- **SQLite** - Database (development)

## 🚀 Deployment

The application is containerized and ready for deployment:

```bash
# Production deployment
docker-compose -f docker-compose.yml up -d

# Development
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up
```

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🤝 Contributing

1. Read the **[Development Guide](docs/development/DEVELOPMENT_GUIDE.md)**
2. Fork the repository
3. Create a feature branch
4. Make your changes
5. Add tests
6. Submit a pull request

## 📞 Support

- 📖 **Documentation**: [docs/](docs/)
- 🐛 **Issues**: Create an issue in the repository
- 💬 **Discussions**: Use GitHub Discussions for questions
