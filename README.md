# Event Attendance API with Discord Integration

A FastAPI-based event attendance tracking system designed for Discord bot integration with time-based attendance validation.

## 🚀 Features

- **Time-Based Attendance Control**: Users can only attend events during their scheduled time window
- **Discord Bot Integration**: Native Discord bot support with dedicated API endpoints
- **JWT Authentication**: Secure authentication system for web users
- **Event Management**: Create, update, and manage events with timing controls
- **Attendance Tracking**: Comprehensive attendance history and reporting
- **Real-time Event Status**: Live event status (upcoming, active, ended)
- **SQLite Database**: Simple, portable database with SQLAlchemy ORM

## 📋 Table of Contents

- [Architecture](#architecture)
- [Database Models](#database-models)
- [API Endpoints](#api-endpoints)
- [Discord Integration](#discord-integration)
- [Time-Based Attendance](#time-based-attendance)
- [Setup & Installation](#setup--installation)
- [Usage Examples](#usage-examples)
- [Development Guidelines](#development-guidelines)
- [Testing](#testing)

## 🏗️ Architecture

```
app/
├── main.py              # FastAPI application entry point
├── config.py            # Configuration settings
├── database.py          # Database connection and session management
├── models.py            # SQLAlchemy database models
├── schemas.py           # Pydantic schemas for request/response validation
├── auth.py              # JWT authentication and password hashing
├── crud.py              # Database CRUD operations
└── routers/
    ├── auth.py          # Authentication endpoints
    ├── users.py         # User management endpoints
    ├── events.py        # Event management endpoints
    └── discord.py       # Discord-specific endpoints
```

## 🗄️ Database Models

### User Model
```python
class User(Base):
    id: int (PK)
    email: str (unique)
    name: str
    hashed_password: str
    discord_user_id: str (unique, nullable)  # Discord integration
    discord_username: str (nullable)         # Discord integration
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    # Relationships
    attended_events: List[Event]  # Many-to-many with events
```

### Event Model
```python
class Event(Base):
    id: int (PK)
    title: str
    description: str (nullable)
    start_time: datetime                     # Event start time
    end_time: datetime                       # Event end time
    discord_channel_id: str (nullable)       # Discord channel ID
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    # Relationships
    attendees: List[User]  # Many-to-many with users
```

### Attendance Association Table
```python
user_event_attendance:
    user_id: int (FK to users.id)
    event_id: int (FK to events.id)
    attended_at: datetime  # Timestamp when attendance was marked
```

## 🌐 API Endpoints

### Authentication Endpoints (`/auth`)
- `POST /auth/register` - Register new user
- `POST /auth/login` - Login and get JWT token

### User Management (`/users`)
- `GET /users/me` - Get current user profile
- `GET /users/me/events` - Get current user's attended events
- `PUT /users/me` - Update current user profile

### Event Management (`/events`)
- `POST /events/` - Create new event
- `GET /events/` - List events (with filtering)
- `GET /events/active` - Get currently active events
- `GET /events/upcoming` - Get upcoming events
- `GET /events/{id}` - Get specific event
- `GET /events/{id}/status` - Get event status with timing info
- `PUT /events/{id}` - Update event
- `POST /events/{id}/attend` - Mark attendance (time-validated)
- `GET /events/{id}/attendees` - Get event attendees
- `GET /events/{id}/check-attendance` - Check user's attendance

### Discord Integration (`/discord`)
- `POST /discord/users/register` - Register Discord user
- `GET /discord/users/{discord_user_id}` - Get Discord user info
- `GET /discord/events/active` - Get active events for Discord
- `GET /discord/events/channel/{channel_id}` - Get events by Discord channel
- `POST /discord/attend/{event_id}` - Attend event via Discord
- `GET /discord/attendance/{discord_user_id}` - Get user attendance history
- `GET /discord/event/{event_id}/status` - Get event status for Discord
- `GET /discord/event/{event_id}/attendees` - Get event attendees for Discord

## 🤖 Discord Integration

### Discord User Registration
Discord users can register without email/password:
```python
{
    "name": "John Doe",
    "discord_user_id": "123456789012345678",
    "discord_username": "johndoe#1234"
}
```

### Discord Bot Commands
The system supports these Discord bot commands:
- `!register [name]` - Register for event attendance
- `!events` - List currently active events
- `!attend <event_id>` - Mark attendance for an event
- `!status` - Check attendance history
- `!help` - Show available commands

### Discord Bot Integration Example
```python
# Example Discord bot integration
class DiscordBot:
    def __init__(self, api_base_url: str = "http://localhost:8000"):
        self.api_base_url = api_base_url
    
    async def attend_event(self, discord_user_id: str, event_id: int):
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.api_base_url}/discord/attend/{event_id}",
                params={"discord_user_id": discord_user_id}
            ) as response:
                return await response.json()
```

## ⏰ Time-Based Attendance

### Attendance Validation Logic
Users can only attend events during the actual event time:

```python
def can_attend_event(event_id: int) -> tuple[bool, Optional[str]]:
    now = datetime.now()
    
    if now < event.start_time:
        return False, f"Event hasn't started yet. Starts in {minutes} minutes"
    
    if now > event.end_time:
        return False, "Event has already ended"
    
    return True, None  # Can attend
```

### Event Status States
- **upcoming**: `now < start_time` - Cannot attend yet
- **active**: `start_time <= now <= end_time` - Can attend
- **ended**: `now > end_time` - Cannot attend anymore

### Time-Based Features
- Real-time event status checking
- Automatic attendance window enforcement
- Time remaining calculations
- Event scheduling validation

## 🛠️ Setup & Installation

### Prerequisites
- Python 3.8+
- pip (Python package manager)

### Installation Steps

1. **Install Dependencies**
```bash
pip install -r requirements.txt
```

2. **Install Email Validator** (for Pydantic EmailStr)
```bash
pip install "pydantic[email]"
```

3. **Environment Variables** (optional)
Create `.env` file:
```env
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///./app.db
```

4. **Initialize Database**
```bash
python -c "from app.database import engine; from app import models; models.Base.metadata.create_all(bind=engine)"
```

5. **Run the Server**
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### Docker Setup
```bash
# Build and run with Docker Compose
docker-compose up --build

# Or run individual commands
make docker-build
make docker-run
```

## 📚 Usage Examples

### Creating a Time-Based Event
```python
# Create event with specific time window
event_data = {
    "title": "Thursday Tech Meetup",
    "description": "Weekly technical discussion",
    "start_time": "2024-06-20T19:00:00",
    "end_time": "2024-06-20T21:00:00",
    "discord_channel_id": "123456789012345678"
}

response = requests.post(
    "http://localhost:8000/events/",
    json=event_data,
    headers={"Authorization": f"Bearer {token}"}
)
```

### Discord User Attendance
```python
# Register Discord user
user_data = {
    "name": "John Doe",
    "discord_user_id": "123456789012345678",
    "discord_username": "johndoe#1234"
}

response = requests.post(
    "http://localhost:8000/discord/users/register",
    json=user_data
)

# Attend event (only works during event time)
response = requests.post(
    f"http://localhost:8000/discord/attend/{event_id}",
    params={"discord_user_id": "123456789012345678"}
)
```

### Checking Event Status
```python
# Get real-time event status
response = requests.get(f"http://localhost:8000/discord/event/{event_id}/status")
status = response.json()

# Returns:
{
    "id": 1,
    "title": "Thursday Tech Meetup",
    "status": "active",  # "upcoming", "active", or "ended"
    "start_time": "2024-06-20T19:00:00",
    "end_time": "2024-06-20T21:00:00",
    "can_attend": true,
    "time_until_end": 3600  # seconds remaining
}
```

## 👨‍💻 Development Guidelines

### Code Structure Rules
1. **Models** (`models.py`): Define database structure with SQLAlchemy
2. **Schemas** (`schemas.py`): Define API request/response models with Pydantic
3. **CRUD** (`crud.py`): Database operations and business logic
4. **Routers** (`routers/`): API endpoints organized by feature
5. **Auth** (`auth.py`): Authentication and security utilities

### Adding New Features

#### 1. Adding New Database Field
```python
# 1. Update model in models.py
class Event(Base):
    new_field: str = Column(String, nullable=True)

# 2. Update schemas in schemas.py
class EventBase(BaseModel):
    new_field: Optional[str] = None

# 3. Update CRUD operations in crud.py
def create_event(db: Session, event: schemas.EventCreate) -> models.Event:
    db_event = models.Event(**event.dict())  # Automatically includes new_field
```

#### 2. Adding New API Endpoint
```python
# In appropriate router file (e.g., routers/events.py)
@router.get("/events/new-endpoint")
def new_endpoint(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    # Implementation here
    return {"result": "data"}
```

#### 3. Adding Discord Bot Command
```python
# In discord_bot_example.py
async def handle_command(self, message: Message) -> str:
    content = message.content.lower().strip()
    
    if content.startswith("!newcommand"):
        # Handle new command
        return "Response to new command"
```

### Time-Based Features Implementation
When adding time-based features, always:
1. Use `datetime.now()` for current time comparisons
2. Validate time windows in CRUD operations
3. Provide clear error messages about timing
4. Include time remaining in status responses

### Discord Integration Guidelines
1. All Discord endpoints should be under `/discord/` prefix
2. Discord user identification uses `discord_user_id` string
3. Discord endpoints should not require JWT authentication
4. Provide Discord-friendly response formats

## 🧪 Testing

### Integration Tests

1. **Run Discord Integration Test**
```bash
python discord_integration_test.py
```

2. **Run Bot Simulation**
```bash
python discord_bot_example.py
```

### Manual Testing

1. **Start Server**
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

2. **Test API Documentation**
Visit: http://localhost:8000/docs

3. **Test Health Check**
```bash
curl http://localhost:8000/health
```

### Test Scenarios to Verify

#### Time-Based Attendance
- [ ] Cannot attend events before start_time
- [ ] Can attend events during active window
- [ ] Cannot attend events after end_time
- [ ] Event status changes correctly over time

#### Discord Integration
- [ ] Discord users can register without email
- [ ] Discord attendance works during event time
- [ ] Discord bot commands respond correctly
- [ ] Attendance history tracks Discord users

#### General Functionality
- [ ] JWT authentication works for web users
- [ ] Event CRUD operations work correctly
- [ ] Database relationships maintained
- [ ] Error handling provides clear messages

## 🔧 Troubleshooting

### Common Issues

1. **Email Validator Error**
```bash
pip install "pydantic[email]"
```

2. **Database Connection Issues**
```bash
# Recreate database
rm -f app.db
python -c "from app.database import engine; from app import models; models.Base.metadata.create_all(bind=engine)"
```

3. **Port Already in Use**
```bash
# Kill existing process
pkill -f uvicorn
# Or use different port
uvicorn app.main:app --port 8001
```

4. **Discord User Not Found**
- Ensure Discord user is registered first using `/discord/users/register`
- Check `discord_user_id` format (should be string)

## 📝 Future Development Notes

### Potential Enhancements
1. **Event Reminders**: Automated Discord notifications
2. **Recurring Events**: Support for repeating events
3. **Event Categories**: Organize events by type
4. **Analytics Dashboard**: Attendance statistics and reporting
5. **Multi-Server Support**: Support multiple Discord servers
6. **Role-Based Permissions**: Event creation permissions
7. **Event Capacity**: Limit number of attendees
8. **Waitlist System**: Queue system for full events

### Database Migration Notes
- When changing models, create Alembic migrations
- Test migrations on development database first
- Backup production database before migrations

### Performance Considerations
- For high-volume usage, consider PostgreSQL over SQLite
- Add database indexes for frequently queried fields
- Implement caching for event status checks
- Consider background tasks for event status updates

## 📄 License

This project is open source and available under the MIT License.
