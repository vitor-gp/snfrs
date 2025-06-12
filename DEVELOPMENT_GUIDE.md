# Development Guide - Event Attendance API

**For AI Assistants:** This guide provides context and patterns for continuing development on this Event Attendance API with Discord integration.

## 🎯 System Overview

This is a **FastAPI-based event attendance tracking system** with these core features:
- **Time-based attendance**: Users can only attend events during their scheduled time window
- **Discord bot integration**: Native support for Discord bots with dedicated endpoints
- **Dual user types**: Regular web users (JWT auth) and Discord users (no auth required)
- **Real-time event status**: Events have dynamic status (upcoming/active/ended)

## 📁 Current Project Structure

```
app/
├── main.py              # FastAPI app with router inclusion
├── config.py            # Pydantic settings (JWT, DB config)
├── database.py          # SQLAlchemy setup and session management
├── models.py            # Database models (User, Event, attendance)
├── schemas.py           # Pydantic request/response models
├── auth.py              # JWT auth, password hashing
├── crud.py              # Database operations with business logic
└── routers/
    ├── auth.py          # Registration, login endpoints
    ├── users.py         # User profile management
    ├── events.py        # Event CRUD with time validation
    └── discord.py       # Discord-specific endpoints (no auth)
```

## 🗄️ Database Design Patterns

### Core Models
```python
# User model supports both web and Discord users
User:
    - id (PK)
    - email (unique, but can be temp for Discord users)
    - name
    - hashed_password (temp generated for Discord users)
    - discord_user_id (nullable, unique)
    - discord_username (nullable)
    - Many-to-many with Events via attendance table

# Event model with time-based validation
Event:
    - id (PK)
    - title, description
    - start_time, end_time (datetime fields for time validation)
    - discord_channel_id (nullable)
    - Many-to-many with Users via attendance table

# Attendance tracking with timestamp
user_event_attendance:
    - user_id, event_id (composite PK)
    - attended_at (auto-timestamp)
```

### Key Design Decisions
1. **Dual User Support**: Same User model handles web and Discord users
2. **Time Windows**: Events have start/end times for attendance validation
3. **Soft Deletes**: `is_active` fields instead of hard deletes
4. **Timestamping**: All models have created_at/updated_at

## 🔄 Business Logic Patterns

### Time-Based Attendance Validation
**Core Pattern**: Always validate time before allowing attendance

```python
def can_attend_event(event_id: int) -> tuple[bool, Optional[str]]:
    now = datetime.now()
    if now < event.start_time:
        return False, f"Event hasn't started yet. Starts in {minutes} minutes"
    if now > event.end_time:
        return False, "Event has already ended"
    return True, None
```

**Usage Pattern**: 
1. Check `can_attend_event()` first
2. Return user-friendly error messages with timing info
3. Include event status in error responses

### Event Status Management
**Pattern**: Dynamic status calculation, not stored

```python
def get_event_status(event_id: int) -> EventStatus:
    now = datetime.now()
    if now < start_time: return "upcoming"
    elif now > end_time: return "ended"
    else: return "active"
```

## 🎨 API Design Patterns

### Authentication Patterns
1. **Web endpoints** (`/auth/*`, `/users/*`, `/events/*`): Require JWT
2. **Discord endpoints** (`/discord/*`): No authentication required
3. **Mixed endpoints**: Some event endpoints work for both user types

### Response Patterns
1. **Success responses**: Return full object + relationships
2. **Error responses**: Include helpful context (event status, timing)
3. **Discord responses**: Simplified, bot-friendly format

### Endpoint Naming Conventions
- `/events/` - Standard CRUD operations
- `/events/active` - Filtered collections
- `/events/{id}/status` - Resource status/metadata
- `/discord/` - Discord-specific variants

## 🔧 Common Development Tasks

### Adding New Database Field

**Step 1: Update Model**
```python
# app/models.py
class Event(Base):
    new_field: str = Column(String, nullable=True)
```

**Step 2: Update Schemas**
```python
# app/schemas.py
class EventBase(BaseModel):
    new_field: Optional[str] = None
```

**Step 3: Update CRUD (if needed)**
```python
# app/crud.py - usually automatic via **event.dict()
```

**Step 4: Recreate DB (development)**
```bash
rm -f app.db
python -c "from app.database import engine; from app import models; models.Base.metadata.create_all(bind=engine)"
```

### Adding New API Endpoint

**Standard Pattern:**
```python
@router.get("/events/new-endpoint")
def new_endpoint(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)  # If auth required
):
    # Business logic here
    return {"result": "data"}
```

**Discord Pattern:**
```python
@router.get("/discord/new-endpoint")
def discord_new_endpoint(db: Session = Depends(get_db)):  # No auth
    # Discord-friendly logic
    return {"success": True, "data": "simple_format"}
```

### Adding Time-Based Features

**Always include:**
1. Time validation in CRUD operations
2. Clear error messages about timing
3. Status information in responses
4. Helper functions for time calculations

### Adding Discord Bot Commands

**Pattern in discord_bot_example.py:**
```python
async def handle_command(self, message: Message) -> str:
    content = message.content.lower().strip()
    
    if content.startswith("!newcommand"):
        # Handle new command
        # Call API endpoints
        # Return user-friendly response
        return "Response to user"
```

## 🧪 Testing Patterns

### Integration Testing
- Use `discord_integration_test.py` as a template
- Test time-based scenarios (past/future/active events)
- Verify both success and failure cases
- Test Discord-specific flows

### Manual Testing
1. **Start server**: `uvicorn app.main:app --reload`
2. **Check docs**: http://localhost:8000/docs
3. **Run integration tests**: `python discord_integration_test.py`
4. **Test bot simulation**: `python discord_bot_example.py`

## 🚨 Common Gotchas

### Database Issues
1. **Email validator**: Need `pip install "pydantic[email]"`
2. **Schema changes**: Recreate DB in development, use Alembic for production
3. **Discord users**: Auto-generate temp email/password if not provided

### Time Zone Handling
- Currently using naive datetime (local time)
- Consider timezone-aware datetime for production
- Validate that end_time > start_time

### Discord Integration
- Discord user IDs are strings, not integers
- Discord endpoints don't require auth
- Provide simple success/failure responses for bots

## 📊 Performance Considerations

### Current Scale
- SQLite suitable for small/medium usage
- Handles hundreds of users/events efficiently

### Future Optimizations
1. **Database**: Switch to PostgreSQL for higher load
2. **Caching**: Cache event status checks
3. **Indexing**: Add indexes on frequently queried fields
4. **Background jobs**: For event status notifications

## 🎛️ Configuration Management

### Environment Variables
```python
# app/config.py
SECRET_KEY: str = "fallback-secret"
DATABASE_URL: str = "sqlite:///./app.db" 
ALGORITHM: str = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
```

### Production Setup
- Set proper SECRET_KEY
- Configure database URL
- Set CORS origins
- Enable HTTPS

## 🔄 Extension Patterns

### Adding New Event Types
1. Add `event_type` field to Event model
2. Update schemas and validation
3. Add filtering endpoints
4. Update Discord bot commands

### Adding Notifications
1. Create notification system (email/Discord)
2. Background tasks for event reminders
3. Webhook support for real-time updates

### Adding Analytics
1. Create analytics endpoints
2. Attendance statistics
3. User engagement metrics
4. Event popularity tracking

## 🐛 Troubleshooting Common Issues

### Server Won't Start
```bash
# Email validator missing
pip install "pydantic[email]"

# Port in use
pkill -f uvicorn
# or use different port
uvicorn app.main:app --port 8001
```

### Database Errors
```bash
# Recreate database
rm -f app.db
python -c "from app.database import engine; from app import models; models.Base.metadata.create_all(bind=engine)"
```

### Discord Integration Issues
- Ensure Discord user is registered first
- Check discord_user_id format (string)
- Verify event timing for attendance

## 📝 Code Quality Guidelines

### FastAPI Best Practices
1. Use Pydantic schemas for all request/response data
2. Include proper HTTP status codes
3. Provide clear error messages
4. Use dependency injection for database sessions
5. Group endpoints in routers by feature

### Database Best Practices
1. Use SQLAlchemy relationships properly
2. Include created_at/updated_at timestamps
3. Use soft deletes (is_active flags)
4. Validate data constraints in both Pydantic and SQLAlchemy

### Discord Integration Best Practices
1. Keep Discord endpoints simple and focused
2. Provide clear success/failure indicators
3. Handle user registration automatically
4. Return bot-friendly response formats

## 🎯 Implementation Checklist for New Features

- [ ] **Database**: Update models, schemas, and CRUD operations
- [ ] **API**: Add endpoints with proper authentication
- [ ] **Discord**: Add Discord-specific endpoints if needed
- [ ] **Time validation**: Include time-based logic if relevant
- [ ] **Error handling**: Provide clear error messages
- [ ] **Testing**: Create integration tests
- [ ] **Documentation**: Update API reference
- [ ] **Bot commands**: Add Discord bot commands if applicable

## 🔮 Future Development Roadmap

### Phase 1: Core Enhancements
- Event categories and tags
- Recurring event support
- Event capacity limits
- Waitlist functionality

### Phase 2: Advanced Features
- Role-based permissions
- Multi-server Discord support
- Analytics dashboard
- Email notifications

### Phase 3: Scale & Performance
- PostgreSQL migration
- Caching layer
- Background job processing
- Monitoring and logging

---

**Remember**: This system prioritizes **time-based attendance validation** and **Discord integration**. When adding features, always consider how they interact with these core concepts. 