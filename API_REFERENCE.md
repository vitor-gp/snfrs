# API Reference - Event Attendance API

Complete API reference for the Event Attendance API with Discord integration.

**Base URL**: `http://localhost:8000`

## Authentication

Most endpoints require JWT authentication. Include the token in the Authorization header:
```
Authorization: Bearer <your_jwt_token>
```

Discord-specific endpoints (`/discord/*`) do not require authentication.

---

## Authentication Endpoints

### POST /auth/register
Register a new user account.

**Request Body:**
```json
{
    "email": "user@example.com",
    "name": "John Doe",
    "password": "securepassword123",
    "discord_user_id": "123456789012345678",  // Optional
    "discord_username": "johndoe#1234"        // Optional
}
```

**Response (201):**
```json
{
    "id": 1,
    "email": "user@example.com",
    "name": "John Doe",
    "discord_user_id": "123456789012345678",
    "discord_username": "johndoe#1234",
    "is_active": true,
    "created_at": "2024-06-20T10:00:00",
    "updated_at": null
}
```

### POST /auth/login
Login and receive JWT token.

**Authentication:** Basic Auth (email:password)

**Response (200):**
```json
{
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer"
}
```

---

## User Management Endpoints

### GET /users/me
Get current user profile.

**Authentication:** Required

**Response (200):**
```json
{
    "id": 1,
    "email": "user@example.com",
    "name": "John Doe",
    "discord_user_id": "123456789012345678",
    "discord_username": "johndoe#1234",
    "is_active": true,
    "created_at": "2024-06-20T10:00:00",
    "updated_at": null
}
```

### GET /users/me/events
Get current user's attended events.

**Authentication:** Required

**Response (200):**
```json
[
    {
        "id": 1,
        "title": "Thursday Tech Meetup",
        "description": "Weekly technical discussion",
        "start_time": "2024-06-20T19:00:00",
        "end_time": "2024-06-20T21:00:00",
        "discord_channel_id": "123456789012345678",
        "is_active": true,
        "created_at": "2024-06-20T10:00:00",
        "updated_at": null,
        "attendees": []
    }
]
```

### PUT /users/me
Update current user profile.

**Authentication:** Required

**Request Body:**
```json
{
    "email": "newemail@example.com",    // Optional
    "name": "New Name",                 // Optional
    "discord_user_id": "987654321",     // Optional
    "discord_username": "newuser#5678", // Optional
    "is_active": true                   // Optional
}
```

**Response (200):** Updated user object

---

## Event Management Endpoints

### POST /events/
Create a new event.

**Authentication:** Required

**Request Body:**
```json
{
    "title": "Thursday Tech Meetup",
    "description": "Weekly technical discussion", // Optional
    "start_time": "2024-06-20T19:00:00",
    "end_time": "2024-06-20T21:00:00",
    "discord_channel_id": "123456789012345678"  // Optional
}
```

**Response (201):**
```json
{
    "id": 1,
    "title": "Thursday Tech Meetup",
    "description": "Weekly technical discussion",
    "start_time": "2024-06-20T19:00:00",
    "end_time": "2024-06-20T21:00:00",
    "discord_channel_id": "123456789012345678",
    "is_active": true,
    "created_at": "2024-06-20T10:00:00",
    "updated_at": null,
    "attendees": []
}
```

### GET /events/
List events with optional filtering.

**Authentication:** Required

**Query Parameters:**
- `skip` (int): Number of records to skip (default: 0)
- `limit` (int): Number of records to return (default: 100)
- `active_only` (bool): Only return active events (default: true)

**Response (200):** Array of event objects

### GET /events/active
Get currently active events (can be attended now).

**Authentication:** Required

**Response (200):** Array of active event objects

### GET /events/upcoming
Get upcoming events.

**Authentication:** Required

**Query Parameters:**
- `limit` (int): Number of events to return (default: 10)

**Response (200):** Array of upcoming event objects

### GET /events/{event_id}
Get specific event with attendees.

**Authentication:** Required

**Response (200):**
```json
{
    "id": 1,
    "title": "Thursday Tech Meetup",
    "description": "Weekly technical discussion",
    "start_time": "2024-06-20T19:00:00",
    "end_time": "2024-06-20T21:00:00",
    "discord_channel_id": "123456789012345678",
    "is_active": true,
    "created_at": "2024-06-20T10:00:00",
    "updated_at": null,
    "attendees": [
        {
            "id": 1,
            "email": "user@example.com",
            "name": "John Doe",
            "discord_user_id": "123456789012345678",
            "discord_username": "johndoe#1234",
            "is_active": true,
            "created_at": "2024-06-20T10:00:00",
            "updated_at": null
        }
    ]
}
```

### GET /events/{event_id}/status
Get event status with timing information.

**Authentication:** Required

**Response (200):**
```json
{
    "id": 1,
    "title": "Thursday Tech Meetup",
    "status": "active",               // "upcoming", "active", or "ended"
    "start_time": "2024-06-20T19:00:00",
    "end_time": "2024-06-20T21:00:00",
    "can_attend": true,
    "time_until_start": null,         // seconds until start (if upcoming)
    "time_until_end": 3600           // seconds until end (if active)
}
```

### PUT /events/{event_id}
Update an event.

**Authentication:** Required

**Request Body:**
```json
{
    "title": "Updated Title",                    // Optional
    "description": "Updated description",        // Optional
    "start_time": "2024-06-20T19:30:00",       // Optional
    "end_time": "2024-06-20T21:30:00",         // Optional
    "discord_channel_id": "987654321",          // Optional
    "is_active": false                          // Optional
}
```

**Response (200):** Updated event object

### POST /events/{event_id}/attend
Mark attendance for an event (time-validated).

**Authentication:** Required

**Response (200) - Success:**
```json
{
    "message": "Attendance marked successfully",
    "event": {
        "id": 1,
        "title": "Thursday Tech Meetup",
        "description": "Weekly technical discussion",
        "start_time": "2024-06-20T19:00:00",
        "end_time": "2024-06-20T21:00:00",
        "discord_channel_id": "123456789012345678",
        "is_active": true,
        "created_at": "2024-06-20T10:00:00",
        "updated_at": null,
        "attendees": []
    },
    "user": {
        "id": 1,
        "email": "user@example.com",
        "name": "John Doe",
        "discord_user_id": "123456789012345678",
        "discord_username": "johndoe#1234",
        "is_active": true,
        "created_at": "2024-06-20T10:00:00",
        "updated_at": null
    },
    "attended_at": "2024-06-20T19:30:00"
}
```

**Response (400) - Time Validation Error:**
```json
{
    "detail": {
        "error": "Event hasn't started yet. Starts in 30 minutes",
        "event_status": {
            "id": 1,
            "title": "Thursday Tech Meetup",
            "status": "upcoming",
            "start_time": "2024-06-20T19:00:00",
            "end_time": "2024-06-20T21:00:00",
            "can_attend": false,
            "time_until_start": 1800,
            "time_until_end": null
        }
    }
}
```

### GET /events/{event_id}/attendees
Get list of event attendees.

**Authentication:** Required

**Response (200):** Array of user objects

### GET /events/{event_id}/check-attendance
Check if current user attended the event.

**Authentication:** Required

**Response (200):**
```json
{
    "attended": true,
    "user_id": 1,
    "event_id": 1
}
```

---

## Discord Integration Endpoints

### POST /discord/users/register
Register a Discord user (no authentication required).

**Request Body:**
```json
{
    "name": "John Doe",
    "discord_user_id": "123456789012345678",
    "discord_username": "johndoe#1234",
    "email": "user@example.com"  // Optional
}
```

**Response (201):** User object

### GET /discord/users/{discord_user_id}
Get Discord user information.

**Response (200):** User object

### GET /discord/events/active
Get all currently active events (Discord-friendly format).

**Response (200):** Array of event objects

### GET /discord/events/channel/{channel_id}
Get events for a specific Discord channel.

**Response (200):** Array of event objects

### POST /discord/attend/{event_id}
Attend an event via Discord (time-validated).

**Query Parameters:**
- `discord_user_id` (string): Discord user ID

**Response (200) - Success:**
```json
{
    "success": true,
    "message": "Successfully attended 'Thursday Tech Meetup'!",
    "event": {
        "id": 1,
        "title": "Thursday Tech Meetup",
        "end_time": "2024-06-20T21:00:00"
    },
    "user": {
        "name": "John Doe",
        "discord_username": "johndoe#1234"
    }
}
```

**Response (200) - Time Validation Error:**
```json
{
    "success": false,
    "message": "Cannot attend: upcoming",
    "event_status": {
        "id": 1,
        "title": "Thursday Tech Meetup",
        "status": "upcoming",
        "start_time": "2024-06-20T19:00:00",
        "end_time": "2024-06-20T21:00:00",
        "can_attend": false,
        "time_until_start": 1800,
        "time_until_end": null
    }
}
```

### GET /discord/attendance/{discord_user_id}
Get attendance history for a Discord user.

**Response (200):**
```json
{
    "user": {
        "discord_user_id": "123456789012345678",
        "discord_username": "johndoe#1234",
        "name": "John Doe"
    },
    "attended_events": [
        {
            "id": 1,
            "title": "Thursday Tech Meetup",
            "start_time": "2024-06-20T19:00:00",
            "end_time": "2024-06-20T21:00:00"
        }
    ],
    "total_attended": 1
}
```

### GET /discord/event/{event_id}/status
Get event status for Discord bot.

**Response (200):** Event status object (same as `/events/{event_id}/status`)

### GET /discord/event/{event_id}/attendees
Get event attendees for Discord display (Discord users only).

**Response (200):**
```json
{
    "event": {
        "id": 1,
        "title": "Thursday Tech Meetup",
        "start_time": "2024-06-20T19:00:00",
        "end_time": "2024-06-20T21:00:00"
    },
    "attendees": [
        {
            "name": "John Doe",
            "discord_username": "johndoe#1234",
            "discord_user_id": "123456789012345678"
        }
    ],
    "total_attendees": 1
}
```

---

## Health & Info Endpoints

### GET /
Get API information and features.

**Response (200):**
```json
{
    "message": "Welcome to Event Attendance API with Discord Integration",
    "docs": "/docs",
    "version": "2.0.0",
    "features": [
        "Time-based attendance (only during events)",
        "Discord bot integration",
        "JWT authentication",
        "Event management"
    ]
}
```

### GET /health
Health check endpoint.

**Response (200):**
```json
{
    "status": "healthy"
}
```

---

## Error Responses

### Common HTTP Status Codes

- `200 OK`: Request successful
- `201 Created`: Resource created successfully
- `400 Bad Request`: Invalid request data or validation error
- `401 Unauthorized`: Authentication required or invalid token
- `403 Forbidden`: Access denied
- `404 Not Found`: Resource not found
- `422 Unprocessable Entity`: Request validation failed

### Error Response Format

```json
{
    "detail": "Error message or validation details"
}
```

### Validation Error Example

```json
{
    "detail": [
        {
            "loc": ["body", "email"],
            "msg": "field required",
            "type": "value_error.missing"
        }
    ]
}
```

---

## Rate Limiting

Currently no rate limiting is implemented, but consider adding it for production use.

## CORS

CORS is configured to allow all origins in development. Configure properly for production.

## WebSocket Support

Not currently implemented, but could be added for real-time event updates.

---

**For interactive API documentation, visit:** `http://localhost:8000/docs` 