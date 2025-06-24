# SNFRS Discord Bot

This directory contains the Discord bot implementation for the SNFRS Event Attendance System (RolêDeQuinta).

## Structure

```
bot/
├── __init__.py          # Package initialization
├── main.py              # Main bot class and setup
├── config.py            # Configuration management
├── run.py               # Entry point script
├── cogs/                # Command groups (cogs)
│   ├── __init__.py      # Cogs package init
│   └── events.py        # Event-related commands
└── README.md            # This file
```

## Architecture

The bot is organized using Discord.py's **Cogs** system for better code organization:

- **`main.py`**: Contains the main `SNFRSBot` class that extends `commands.Bot`
- **`config.py`**: Centralized configuration management using environment variables
- **`cogs/events.py`**: All event-related slash commands organized in the `EventsCog` class
- **`run.py`**: Simple entry point that can be run directly

## Features

### Slash Commands

- `/register [nome]` - Register for event attendance
- `/events` - Show currently active events
- `/attend <event_id>` - Mark attendance for an event
- `/status` - Check your attendance history
- `/create_event` - Create a new event (admin only)
- `/event_status <event_id>` - Show event status
- `/event_attendees <event_id>` - List event attendees
- `/user_info` - Show user profile
- `/make_admin <password>` - Become admin (password: "123")
- `/bothelp` - Show help information

### Admin Features

- Event creation with time validation
- Database-based admin permissions (not Discord roles)
- User management and statistics

## Configuration

The bot uses environment variables for configuration:

- `DISCORD_BOT_TOKEN` - Discord bot token (required)
- `API_BASE_URL` - Base URL for the SNFRS API (default: http://api:8000)
- `DISCORD_ADMIN_ROLE` - Discord role name for admins (default: Admin)
- `ADMIN_API_TOKEN` - API token for admin operations (optional)

## Running the Bot

### Docker (Recommended)

```bash
# Build and run with docker-compose
docker compose up discord-bot

# Development mode with hot reload
docker compose up discord-bot-dev
```

### Direct Python

```bash
# From the project root
python bot/run.py

# Or using the module
python -m bot.main
```

## Development

### Adding New Commands

1. Add the command to the appropriate cog in `cogs/`
2. Use the `@app_commands.command()` decorator
3. Follow the existing pattern for API calls and error handling

### Adding New Cogs

1. Create a new file in `cogs/`
2. Create a class that inherits from `commands.Cog`
3. Add the cog to `main.py` in the `setup_hook()` method

## API Integration

The bot communicates with the SNFRS FastAPI backend through HTTP requests:

- **Registration**: `POST /discord/users/register`
- **Events**: `GET /discord/events/active`
- **Attendance**: `POST /discord/attend/{event_id}`
- **Admin**: `POST /discord/admin/make-admin`
- **Event Creation**: `POST /discord/events/create`

All API calls include proper error handling and user feedback. 