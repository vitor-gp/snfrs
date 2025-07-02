#!/bin/bash

# Setup script for creating .env file
echo "Setting up environment variables..."

if [ ! -f .env ]; then
    echo "Creating .env file..."
    cat > .env << EOF
# Database Configuration
DATABASE_URL=sqlite:///./data/app.db

# JWT Configuration
SECRET_KEY=dev-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Discord Bot Configuration
DISCORD_TOKEN=your-discord-bot-token-here
DISCORD_GUILD=your-discord-server-id-here

# API Configuration
API_BASE_URL=http://localhost:8000

# Environment
ENVIRONMENT=development
EOF
    echo "✓ .env file created successfully!"
    echo ""
    echo "⚠️  IMPORTANT: Please update the following variables in .env:"
    echo "   - DISCORD_TOKEN: Your Discord bot token"
    echo "   - DISCORD_GUILD: Your Discord server ID"
    echo "   - SECRET_KEY: Change this for production"
    echo ""
else
    echo "✓ .env file already exists"
fi

echo "Environment setup complete!" 