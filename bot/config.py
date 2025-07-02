"""
Configuration module for the Discord Bot.

This module handles all environment variable configuration for the bot.
"""

import logging
import os
import sys
from dataclasses import dataclass


@dataclass
class BotConfig:
    """Configuration class for Discord bot settings."""

    def __init__(self):
        """Initialize bot configuration from environment variables."""
        self.token = os.getenv("DISCORD_TOKEN")
        self.api_base_url = os.getenv("API_BASE_URL", "http://localhost:8000")
        self.guild_id = os.getenv("DISCORD_GUILD")

        if not self.token:
            logging.error("❌ DISCORD_TOKEN environment variable is required")
            raise ValueError("DISCORD_TOKEN environment variable is required")


def setup_logging() -> logging.Logger:
    """Set up logging configuration for the Discord bot."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler('/tmp/discord_bot.log')
        ]
    )
    return logging.getLogger(__name__) 