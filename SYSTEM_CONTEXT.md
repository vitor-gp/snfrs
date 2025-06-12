# System Context - Event Attendance API

**Quick Reference for AI Assistants**

## 🎯 What This System Does

**Purpose**: Track event attendance with Discord bot integration and time-based validation
**Key Constraint**: Users can only attend events during their scheduled time window (start_time to end_time)

## 🏗️ Architecture Summary

```
FastAPI + SQLAlchemy + SQLite
├── Web Users: JWT authentication, full CRUD access
├── Discord Users: No auth required, simplified endpoints
├── Time Validation: Automatic enforcement of event time windows
└── Real-time Status: Dynamic event status calculation
```

## 📊 Core Data Models

```python
User:
    id, email, name, hashed_password
    discord_user_id, discord_username  # Discord integration
    attended_events (many-to-many)

Event:
    id, title, description
    start_time, end_time              # Time validation
    discord_channel_id                # Discord integration
    attendees (many-to-many)

Attendance:
    user_id + event_id + attended_at  # When attendance marked
```

## 🔑 Key Business Rules

1. **Time-Based Attendance**: `start_time <= now <= end_time` required
2. **Event Status**: Dynamic calculation (upcoming/active/ended)
3. **Dual User Types**: Web users (auth) + Discord users (no auth)
4. **One Attendance Per Event**: Users can only attend each event once

## 🛣️ API Structure

```
/auth/*          - Registration, login (JWT required)
/users/*         - User management (JWT required)
/events/*        - Event CRUD (JWT required)
/discord/*       - Discord integration (no auth)
```

## 💡 Time Validation Pattern

```python
# Core pattern used throughout system
def can_attend_event(event_id: int) -> tuple[bool, Optional[str]]:
    now = datetime.now()
    if now < event.start_time:
        return False, "Event hasn't started yet"
    if now > event.end_time:
        return False, "Event has already ended"
    return True, None
```

## 🤖 Discord Integration

- **No authentication** for Discord endpoints
- **Auto-registration** for Discord users
- **Simplified responses** for bot consumption
- **String user IDs** (Discord snowflakes)

## 🧪 Testing Setup

```bash
# Start server
uvicorn app.main:app --reload

# Run integration test
python discord_integration_test.py

# Test bot commands
python discord_bot_example.py
```

## 🔧 Common Tasks

### Add Database Field
1. Update `app/models.py`
2. Update `app/schemas.py`
3. Recreate DB: `rm app.db && python -c "...create_all..."`

### Add API Endpoint
```python
@router.get("/endpoint")
def endpoint(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)  # If auth needed
):
    return {"data": "result"}
```

### Add Discord Command
```python
# In discord_bot_example.py
if content.startswith("!command"):
    # Call API, return response
    return "User-friendly message"
```

## 🚨 Important Notes

- **Email validator**: Requires `pip install "pydantic[email]"`
- **DateTime**: Currently naive (local time), consider timezone-aware for production
- **Discord users**: Auto-generate temp email/password
- **Time zones**: All times in server local time
- **Database**: SQLite for dev, consider PostgreSQL for production

## 📁 Key Files

- `app/main.py` - FastAPI app entry point
- `app/models.py` - Database models with relationships
- `app/crud.py` - Business logic and time validation
- `app/routers/discord.py` - Discord-specific endpoints
- `discord_integration_test.py` - Comprehensive test suite
- `discord_bot_example.py` - Bot integration example

## 🎯 System Goals

1. **Enforce time-based attendance** (only during events)
2. **Support Discord bots** (simple, no-auth endpoints)
3. **Maintain data integrity** (one attendance per user per event)
4. **Provide clear feedback** (helpful error messages with timing info)

---

**Current Status**: ✅ Fully functional with passing integration tests
**Version**: 2.0.0 with Discord integration and time-based validation 