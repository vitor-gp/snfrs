#!/usr/bin/env python3
"""
Entry point script for the SNFRS Discord Bot.

This script can be run directly to start the Discord bot.
"""

import sys
import os

# Add the parent directory to the Python path so we can import the bot package
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from bot.main import main
import asyncio
import logging

if __name__ == "__main__":
    try:
        logging.basicConfig(level=logging.INFO)
        logger = logging.getLogger(__name__)
        logger.info("🚀 Starting SNFRS Discord Bot...")
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("🛑 Bot stopped by user (KeyboardInterrupt)")
    except Exception as e:
        logger.error(f"❌ Fatal error: {e}")
        sys.exit(1) 