"""
Main Discord Bot Entry Point for SNFRS Event Attendance System

This module contains the main Discord bot implementation for the 
RolêDeQuinta event attendance system.
"""

import asyncio
import logging
import sys

import aiohttp
import discord
from discord.ext import commands

from bot.cogs.events import EventsCog
from bot.config import BotConfig, setup_logging


async def main():
    """Main entry point for the Discord bot."""
    # Initialize configuration and logging
    config = BotConfig()
    logger = setup_logging()

    # Create and run the bot
    bot = SNFRSBot()
    try:
        logger.info("🚀 Starting Discord bot application...")
        await bot.start(config.token)
    except KeyboardInterrupt:
        logger.info("🛑 Bot stopped by user (KeyboardInterrupt)")
    except Exception as e:
        logger.error(f"❌ Fatal error: {e}")
        sys.exit(1)


class SNFRSBot(commands.Bot):
    """Main Discord Bot class for SNFRS Event Attendance System."""
    
    def __init__(self):
        """Initialize the Discord bot with proper configuration."""
        self.config = BotConfig()
        self.logger = setup_logging()
        
        intents = discord.Intents.default()
        intents.message_content = True
        
        super().__init__(command_prefix="!", intents=intents)
        
        self.logger.info("🚀 Starting Discord Bot...")
        self.logger.info(f"API Base URL: {self.config.api_base_url}")
        self.logger.info(f"Token configured: {bool(self.config.token)}")
        
        if not self.config.token:
            self.logger.error("❌ DISCORD_BOT_TOKEN environment variable is required")
            raise ValueError("DISCORD_BOT_TOKEN environment variable is required")

    async def setup_hook(self):
        """Set up the bot with cogs and sync commands."""
        self.logger.info("🔧 Adding EventsCog to bot...")
        await self.add_cog(EventsCog(self))
        self.logger.info("✅ Cog added successfully")

    async def on_ready(self):
        """Event handler for when the bot is ready."""
        self.logger.info(f"🎉 Bot logged in as {self.user} (ID: {self.user.id})")
        self.logger.info("------ RolêDeQuinta tá online, gerenciado pelo grupo sinforoso lifestyle ------")
        
        # Log guild information
        self.logger.info(f"📊 Connected to {len(self.guilds)} guild(s):")
        for guild in self.guilds:
            self.logger.info(f"  - {guild.name} (ID: {guild.id}) - {guild.member_count} members")
        
        # Test API connection
        await self._test_api_connection()
        
        # Sync slash commands
        await self._sync_commands()
        
        self.logger.info("🚀 Discord bot is ready and running!")
        self.logger.info("📝 Note: Slash commands should now be available immediately in your server!")
        self.logger.info("🔑 Try using /make_admin <password> where password is '123'")

    async def _test_api_connection(self):
        """Test the connection to the API."""
        try:
            self.logger.info("🔗 Testing API connection...")
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.config.api_base_url}/health") as resp:
                    if resp.status == 200:
                        self.logger.info("✅ API connection successful")
                    else:
                        self.logger.warning(f"⚠️ API connection issue: HTTP {resp.status}")
        except Exception as e:
            self.logger.error(f"❌ API connection failed: {e}")

    async def _sync_commands(self):
        """Sync slash commands to guilds and globally."""
        try:
            self.logger.info("⚙️ Syncing slash commands...")
            
            # Sync to all guilds for immediate availability
            for guild in self.guilds:
                try:
                    synced_guild = await self.tree.sync(guild=guild)
                    self.logger.info(f"✅ Synced {len(synced_guild)} commands to guild: {guild.name}")
                except Exception as guild_e:
                    self.logger.error(f"❌ Failed to sync to guild {guild.name}: {guild_e}")
            
            # Also sync globally (takes up to 1 hour to propagate)
            synced_global = await self.tree.sync()
            self.logger.info(f"✅ Global slash commands synchronized: {len(synced_global)} commands")
            
            for cmd in synced_global:
                self.logger.info(f"  - /{cmd.name}: {cmd.description}")
                
        except Exception as e:
            self.logger.error(f"❌ Error syncing slash commands: {e}")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("🛑 Bot stopped by user")
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        sys.exit(1) 