"""
Configuration module for the Discord Bot.

This module handles all environment variable configuration for the bot.
"""

import os
from typing import Optional


class BotConfig:
    """Configuration class for Discord Bot environment variables."""
    
    def __init__(self):
        """Initialize configuration from environment variables."""
        self.api_base_url = os.getenv("API_BASE_URL", "http://api:8000")
        self.token = os.getenv("DISCORD_BOT_TOKEN")
        self.admin_role = os.getenv("DISCORD_ADMIN_ROLE", "Admin")
        self.admin_api_token = os.getenv("ADMIN_API_TOKEN", "")
        
    @property
    def is_configured(self) -> bool:
        """Check if the bot is properly configured."""
        return bool(self.token)
    
    def validate(self) -> None:
        """Validate that required configuration is present."""
        if not self.token:
            raise ValueError("DISCORD_BOT_TOKEN environment variable is required")
            
    def __repr__(self) -> str:
        """String representation of the configuration."""
        return (
            f"BotConfig("
            f"api_base_url='{self.api_base_url}', "
            f"token_configured={bool(self.token)}, "
            f"admin_role='{self.admin_role}'"
            f")"
        ) 