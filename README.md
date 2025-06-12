# Event Attendance API

A FastAPI-based REST API for tracking event attendance, specifically designed for weekly Thursday meetups. Built with best software engineering practices, including Docker, comprehensive testing, and clean architecture.

## Features

- **User Management**: User registration, authentication with JWT tokens
- **Event Management**: Create, read, update events with full CRUD operations
- **Attendance Tracking**: Mark attendance and check attendance status
- **Database**: SQLite for simplicity (easily upgradeable to PostgreSQL)
- **Authentication**: JWT-based authentication with secure password hashing
- **Testing**: Comprehensive test suite with pytest
- **Docker**: Full containerization support
- **API Documentation**: Auto-generated OpenAPI/Swagger documentation

## Tech Stack

- **FastAPI**: Modern, fast web framework for building APIs
- **SQLAlchemy**: SQL toolkit and ORM
- **Alembic**: Database migration tool
- **SQLite**: Lightweight database (production-ready for small/medium apps)
- **Pydantic**: Data validation using Python type hints
- **JWT**: JSON Web Tokens for authentication
- **Docker**: Containerization
- **Pytest**: Testing framework

## Quick Start

### Option 1: Docker (Recommended)

1. **Clone and setup**:
   ```bash
   git clone <your-repo>
   cd event-attendance-api
   ```

2. **Build and run with Docker Compose**:
   ```bash
   # For development
   make docker-dev
   # OR
   docker-compose up api-dev
   
   # For production
   make docker-run
   # OR
   docker-compose up api
   ```

3. **Access the API**:
   - Development: http://localhost:8001
   - Production: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

### Option 2: Local Development

1. **Setup Python environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install dependencies and setup**:
   ```bash
   make setup-dev
   # OR manually:
   pip install -r requirements.txt
   mkdir -p data
   ```

3. **Run the development server**:
   ```bash
   make dev
   # OR
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

## API Endpoints

### Authentication
- `POST /auth/register` - Register a new user
- `POST /auth/login` - Login user (returns JWT token)

### Users
- `GET /users/me` - Get current user profile
- `PUT /users/me` - Update current user profile
- `GET /users/me/events` - Get user's attended events
- `GET /users/{user_id}` - Get user by ID
- `GET /users/` - List all users

### Events
- `POST /events/` - Create a new event
- `GET /events/` - List all events
- `GET /events/upcoming` - Get upcoming events
- `GET /events/{event_id}` - Get event details with attendees
- `PUT /events/{event_id}` - Update event
- `POST /events/{event_id}/attend` - Mark attendance for an event
- `GET /events/{event_id}/attendees` - Get event attendees
- `GET /events/{event_id}/check-attendance` - Check if user attended event

### Health
- `GET /health` - Health check endpoint

## Usage Examples

### 1. Register a User
```bash
curl -X POST "http://localhost:8000/auth/register" \
     -H "Content-Type: application/json" \
     -d '{
       "email": "user@example.com",
       "name": "John Doe",
       "password": "securepassword123"
     }'
```

### 2. Login
```bash
curl -X POST "http://localhost:8000/auth/login" \
     -u "user@example.com:securepassword123"
```

### 3. Create an Event (requires authentication)
```bash
curl -X POST "http://localhost:8000/events/" \
     -H "Authorization: Bearer YOUR_JWT_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{
       "title": "Thursday Meetup #1",
       "description": "Weekly Thursday meetup",
       "event_date": "2024-02-01T18:00:00"
     }'
```

### 4. Mark Attendance
```bash
curl -X POST "http://localhost:8000/events/1/attend" \
     -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

## Development

### Available Make Commands
```bash
make help           # Show all available commands
make install        # Install dependencies
make dev            # Run development server
make test           # Run tests with coverage
make lint           # Run linting tools
make format         # Format code with black and isort
make clean          # Clean up temporary files
make docker-build   # Build Docker image
make docker-dev     # Run development container
make docker-run     # Run production container
make setup-dev      # Setup development environment
```

### Running Tests
```bash
# Run all tests
make test

# Run specific test file
pytest tests/test_auth.py -v

# Run with coverage report
pytest --cov=app --cov-report=html
```

### Database Migrations
```bash
# Generate migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Downgrade
alembic downgrade -1
```

### Code Quality
```bash
# Format code
make format

# Check linting
make lint

# Type checking
mypy app/
```

## Project Structure

```
event-attendance-api/
├── app/                    # Application code
│   ├── routers/           # API route handlers
│   │   ├── auth.py        # Authentication endpoints
│   │   ├── users.py       # User management endpoints
│   │   └── events.py      # Event management endpoints
│   ├── __init__.py
│   ├── main.py            # FastAPI application
│   ├── config.py          # Configuration settings
│   ├── database.py        # Database connection
│   ├── models.py          # SQLAlchemy models
│   ├── schemas.py         # Pydantic schemas
│   ├── crud.py            # Database operations
│   └── auth.py            # Authentication utilities
├── tests/                 # Test files
│   ├── test_auth.py       # Authentication tests
│   └── test_events.py     # Event management tests
├── alembic/               # Database migrations
├── data/                  # Database files (local)
├── requirements.txt       # Python dependencies
├── Dockerfile             # Docker configuration
├── docker-compose.yml     # Docker Compose setup
├── Makefile              # Development commands
├── pytest.ini            # Pytest configuration
├── alembic.ini           # Alembic configuration
├── .gitignore            # Git ignore rules
└── README.md             # This file
```

## Database Schema

### Users Table
- `id`: Primary key
- `email`: Unique email address
- `name`: User's full name
- `hashed_password`: Bcrypt hashed password
- `is_active`: Boolean flag
- `created_at`, `updated_at`: Timestamps

### Events Table
- `id`: Primary key
- `title`: Event title
- `description`: Event description
- `event_date`: When the event occurs
- `is_active`: Boolean flag
- `created_at`, `updated_at`: Timestamps

### User-Event Attendance (Many-to-Many)
- `user_id`: Foreign key to users
- `event_id`: Foreign key to events
- `attended_at`: Timestamp when attendance was marked

## Configuration

The application uses environment variables for configuration:

- `DATABASE_URL`: Database connection string (default: SQLite)
- `SECRET_KEY`: JWT secret key (change in production!)
- `ALGORITHM`: JWT algorithm (default: HS256)
- `ACCESS_TOKEN_EXPIRE_MINUTES`: Token expiration (default: 30)

## Deployment

### Production Considerations

1. **Environment Variables**: Set proper values for production
2. **Database**: Consider upgrading to PostgreSQL for production
3. **Secret Key**: Generate a secure secret key
4. **CORS**: Configure proper CORS origins
5. **HTTPS**: Use HTTPS in production
6. **Monitoring**: Add logging and monitoring

### Example Production Docker Run
```bash
docker run -d \
  -p 8000:8000 \
  -e DATABASE_URL="postgresql://user:pass@localhost/db" \
  -e SECRET_KEY="your-super-secure-secret-key" \
  event-attendance-api
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Write tests for new functionality
5. Ensure all tests pass: `make test`
6. Check code quality: `make lint`
7. Submit a pull request

## License

This project is licensed under the MIT License.

## Support

For questions or issues, please open an issue on GitHub.
