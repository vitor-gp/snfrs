#!/usr/bin/env python3
"""
Discord Bot Example for Event Attendance API
This bot allows Discord users to check and attend events through Discord commands.
"""

import asyncio
import aiohttp
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional

# Mock Discord.py classes for demonstration
class Message:
    def __init__(self, content: str, author_id: str, author_name: str, channel_id: str):
        self.content = content
        self.author = type('Author', (), {'id': author_id, 'name': author_name})()
        self.channel = type('Channel', (), {'id': channel_id})()

class DiscordBot:
    def __init__(self, api_base_url: str = "http://localhost:8000"):
        self.api_base_url = api_base_url
        
    async def register_user(self, discord_user_id: str, discord_username: str, name: str = None) -> Dict:
        """Register a Discord user with the API"""
        user_data = {
            "name": name or discord_username.split("#")[0],
            "discord_user_id": discord_user_id,
            "discord_username": discord_username
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.api_base_url}/discord/users/register",
                json=user_data
            ) as response:
                if response.status in [200, 201]:
                    return await response.json()
                else:
                    error_text = await response.text()
                    raise Exception(f"Registration failed: {error_text}")
    
    async def get_active_events(self) -> List[Dict]:
        """Get all currently active events"""
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{self.api_base_url}/discord/events/active") as response:
                if response.status == 200:
                    return await response.json()
                return []
    
    async def get_event_status(self, event_id: int) -> Optional[Dict]:
        """Get the status of a specific event"""
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{self.api_base_url}/discord/event/{event_id}/status") as response:
                if response.status == 200:
                    return await response.json()
                return None
    
    async def attend_event(self, discord_user_id: str, event_id: int) -> Dict:
        """Mark attendance for an event"""
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.api_base_url}/discord/attend/{event_id}",
                params={"discord_user_id": discord_user_id}
            ) as response:
                return await response.json()
    
    async def get_user_attendance(self, discord_user_id: str) -> Optional[Dict]:
        """Get user's attendance history"""
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{self.api_base_url}/discord/attendance/{discord_user_id}") as response:
                if response.status == 200:
                    return await response.json()
                return None
    
    async def handle_command(self, message: Message) -> str:
        """Handle Discord bot commands"""
        content = message.content.lower().strip()
        user_id = str(message.author.id)
        username = message.author.name
        
        try:
            if content.startswith("!register"):
                # Register user
                parts = content.split()
                display_name = " ".join(parts[1:]) if len(parts) > 1 else username
                
                await self.register_user(user_id, username, display_name)
                return f"✅ {display_name}, you've been registered for event attendance!"
            
            elif content == "!events":
                # List active events
                events = await self.get_active_events()
                if not events:
                    return "🔍 No events are currently active. Check back during event times!"
                
                response = "🎉 **Active Events** (You can attend these now!):\n"
                for event in events:
                    start_time = datetime.fromisoformat(event["start_time"].replace("Z", "+00:00"))
                    end_time = datetime.fromisoformat(event["end_time"].replace("Z", "+00:00"))
                    response += f"• **{event['title']}** (ID: {event['id']})\n"
                    response += f"  📅 Until: {end_time.strftime('%I:%M %p')}\n"
                    response += f"  📝 {event.get('description', 'No description')}\n\n"
                
                response += "Use `!attend <event_id>` to mark your attendance!"
                return response
            
            elif content.startswith("!attend"):
                # Attend an event
                parts = content.split()
                if len(parts) != 2:
                    return "❌ Usage: `!attend <event_id>`\nUse `!events` to see available events."
                
                try:
                    event_id = int(parts[1])
                except ValueError:
                    return "❌ Invalid event ID. Please use a number."
                
                result = await self.attend_event(user_id, event_id)
                
                if result.get("success"):
                    event_info = result.get("event", {})
                    return f"🎉 {result['message']}\n📋 Event: **{event_info.get('title', 'Unknown')}**"
                else:
                    message = result.get("message", "Unknown error")
                    event_status = result.get("event_status", {})
                    
                    if event_status:
                        status = event_status.get("status", "unknown")
                        if status == "upcoming":
                            time_until = event_status.get("time_until_start", 0)
                            minutes = time_until // 60
                            return f"⏰ {message}\nEvent starts in {minutes} minutes. Come back then!"
                        elif status == "ended":
                            return f"⏰ {message}\nYou missed this one, but there will be more events!"
                    
                    return f"❌ {message}"
            
            elif content == "!status":
                # Check user's attendance status
                attendance = await self.get_user_attendance(user_id)
                if not attendance:
                    return "❌ You're not registered yet! Use `!register` first."
                
                user_info = attendance["user"]
                attended_events = attendance["attended_events"]
                total = attendance["total_attended"]
                
                response = f"📊 **Attendance Status for {user_info['name']}**\n"
                response += f"🏆 Total Events Attended: **{total}**\n\n"
                
                if attended_events:
                    response += "📅 **Your Attended Events:**\n"
                    for event in attended_events[-5:]:  # Show last 5
                        date = datetime.fromisoformat(event["start_time"].replace("Z", "+00:00"))
                        response += f"• {event['title']} - {date.strftime('%m/%d/%Y')}\n"
                    
                    if len(attended_events) > 5:
                        response += f"... and {len(attended_events) - 5} more events"
                else:
                    response += "📝 No events attended yet. Use `!events` to see active events!"
                
                return response
            
            elif content == "!help":
                return self.get_help_message()
            
            else:
                return None  # Not a bot command
                
        except Exception as e:
            return f"❌ An error occurred: {str(e)}\nTry `!help` for available commands."
    
    def get_help_message(self) -> str:
        """Get help message with all available commands"""
        return """🤖 **Event Attendance Bot Commands**

📝 **!register [name]** - Register for event attendance
🎉 **!events** - List currently active events (only during event times)
✅ **!attend <event_id>** - Mark attendance for an event (only during event time)
📊 **!status** - Check your attendance history
❓ **!help** - Show this help message

**How it works:**
• Events can only be attended during their scheduled time
• Use `!events` to see what's happening right now
• Events typically run on Thursdays during meeting times
• Your attendance is automatically tracked!

**Example:**
```
!register John Doe
!events
!attend 1
!status
```
"""


# Example usage and testing
async def simulate_discord_interaction():
    """Simulate Discord bot interactions for testing"""
    print("🤖 Discord Bot Simulation")
    print("=" * 40)
    
    bot = DiscordBot()
    
    # Simulate messages from different users
    messages = [
        Message("!help", "123456789", "TestUser#1234", "channel1"),
        Message("!register Test User", "123456789", "TestUser#1234", "channel1"),
        Message("!events", "123456789", "TestUser#1234", "channel1"),
        Message("!attend 1", "123456789", "TestUser#1234", "channel1"),
        Message("!status", "123456789", "TestUser#1234", "channel1"),
    ]
    
    for message in messages:
        print(f"\n👤 {message.author.name}: {message.content}")
        response = await bot.handle_command(message)
        if response:
            print(f"🤖 Bot: {response}")
        else:
            print("🤖 Bot: (No response - not a command)")


# Real Discord.py integration example (commented out)
"""
import discord
from discord.ext import commands

# Uncomment and modify this for actual Discord bot implementation
class EventAttendanceBot(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.api_bot = DiscordBot()
    
    @commands.command(name='register')
    async def register(self, ctx, *, name: str = None):
        response = await self.api_bot.handle_command(
            type('Message', (), {
                'content': f"!register {name or ''}",
                'author': ctx.author,
                'channel': ctx.channel
            })()
        )
        await ctx.send(response)
    
    @commands.command(name='events')
    async def events(self, ctx):
        response = await self.api_bot.handle_command(
            type('Message', (), {
                'content': "!events",
                'author': ctx.author,
                'channel': ctx.channel
            })()
        )
        await ctx.send(response)
    
    @commands.command(name='attend')
    async def attend(self, ctx, event_id: int):
        response = await self.api_bot.handle_command(
            type('Message', (), {
                'content': f"!attend {event_id}",
                'author': ctx.author,
                'channel': ctx.channel
            })()
        )
        await ctx.send(response)
    
    @commands.command(name='status')
    async def status(self, ctx):
        response = await self.api_bot.handle_command(
            type('Message', (), {
                'content': "!status",
                'author': ctx.author,
                'channel': ctx.channel
            })()
        )
        await ctx.send(response)

# Bot setup
bot = commands.Bot(command_prefix='!', intents=discord.Intents.default())

async def setup(bot):
    await bot.add_cog(EventAttendanceBot(bot))

# Run the bot
# bot.run('YOUR_BOT_TOKEN')
"""

if __name__ == "__main__":
    import discord
    from discord.ext import commands
    import asyncio

    TOKEN = os.getenv("DISCORD_BOT_TOKEN")
    if not TOKEN:
        raise ValueError("DISCORD_BOT_TOKEN environment variable is required")

    intents = discord.Intents.default()
    intents.message_content = True

    bot = commands.Bot(command_prefix="!", intents=intents)
    api_bot = DiscordBot()

    @bot.event
    async def on_ready():
        print(f"Logged in as {bot.user} (ID: {bot.user.id})")
        print("------ Bot is online and ready to receive commands ------")

    @bot.command(name='register')
    async def register(ctx, *, name: str = None):
        msg = type('Msg', (), {
            'content': f"!register {name or ''}",
            'author': ctx.author,
            'channel': ctx.channel
        })()
        response = await api_bot.handle_command(msg)
        if response:
            await ctx.send(response)

    @bot.command(name='events')
    async def events(ctx):
        msg = type('Msg', (), {
            'content': "!events",
            'author': ctx.author,
            'channel': ctx.channel
        })()
        response = await api_bot.handle_command(msg)
        if response:
            await ctx.send(response)

    @bot.command(name='attend')
    async def attend(ctx, event_id: int):
        msg = type('Msg', (), {
            'content': f"!attend {event_id}",
            'author': ctx.author,
            'channel': ctx.channel
        })()
        response = await api_bot.handle_command(msg)
        if response:
            await ctx.send(response)

    @bot.command(name='status')
    async def status(ctx):
        msg = type('Msg', (), {
            'content': "!status",
            'author': ctx.author,
            'channel': ctx.channel
        })()
        response = await api_bot.handle_command(msg)
        if response:
            await ctx.send(response)

    bot.run(TOKEN) 