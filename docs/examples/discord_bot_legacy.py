"""
Discord Bot for Event Attendance API

STARTUP INSTRUCTIONS:
1. Set your bot token in the code or as an environment variable (DISCORD_BOT_TOKEN).
2. Enable 'MESSAGE CONTENT INTENT' in the Discord Developer Portal for your bot.
3. Invite the bot to your server with permissions:
   - Read Messages/View Channels
   - Send Messages
   - Read Message History
   - (Recommended) Message Content
4. Run the bot:
   $ python discord_bot.py
5. In your Discord server, use:
   !register [name]   - Register for event attendance
   !events            - List currently active events
   !attend <event_id> - Mark attendance for an event
   !status            - Check your attendance history

# NOTE: If you see import errors for 'discord' or 'aiohttp', run:
#   pip install discord.py aiohttp
"""
import os
import discord
from discord.ext import commands
import aiohttp
import asyncio
from discord import app_commands
import logging
import sys

# Configure comprehensive logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('/tmp/discord_bot.log')
    ]
)
logger = logging.getLogger(__name__)

# Set Discord library logging to INFO to see connection details
discord_logger = logging.getLogger('discord')
discord_logger.setLevel(logging.INFO)

API_BASE_URL = os.getenv("API_BASE_URL", "http://api:8000")
TOKEN = os.getenv("DISCORD_BOT_TOKEN")

logger.info("🚀 Starting Discord Bot...")
logger.info(f"API Base URL: {API_BASE_URL}")
logger.info(f"Token configured: {bool(TOKEN)}")

if not TOKEN:
    logger.error("❌ DISCORD_BOT_TOKEN environment variable is required")
    raise ValueError("DISCORD_BOT_TOKEN environment variable is required")

ADMIN_ROLE = os.getenv("DISCORD_ADMIN_ROLE", "Admin")
ADMIN_API_TOKEN = os.getenv("ADMIN_API_TOKEN", "")

logger.info(f"Admin role: {ADMIN_ROLE}")
logger.info(f"Admin API token configured: {bool(ADMIN_API_TOKEN)}")

intents = discord.Intents.default()
intents.message_content = True

logger.info("🔧 Configuring Discord bot with intents...")
bot = commands.Bot(command_prefix="!", intents=intents)
logger.info("✅ Discord bot instance created")

async def api_post(endpoint, json=None, params=None):
    url = f"{API_BASE_URL}{endpoint}"
    logger.debug(f"📤 POST {url} - Data: {json} - Params: {params}")
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=json, params=params) as resp:
            data = await resp.json()
            logger.debug(f"📥 POST {url} - Status: {resp.status} - Response: {data}")
            return data, resp.status

async def api_get(endpoint, params=None):
    url = f"{API_BASE_URL}{endpoint}"
    logger.debug(f"📤 GET {url} - Params: {params}")
    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params) as resp:
            data = await resp.json()
            logger.debug(f"📥 GET {url} - Status: {resp.status} - Response: {data}")
            return data, resp.status

@bot.event
async def on_ready():
    logger.info(f"🎉 Bot logged in as {bot.user} (ID: {bot.user.id})")
    logger.info("------ RolêDeQuinta tá online, gerenciado pelo grupo sinforoso lifestyle ------")
    
    # Log guild information
    logger.info(f"📊 Connected to {len(bot.guilds)} guild(s):")
    for guild in bot.guilds:
        logger.info(f"  - {guild.name} (ID: {guild.id}) - {guild.member_count} members")
    
    # Test API connection
    try:
        logger.info("🔗 Testing API connection...")
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{API_BASE_URL}/health") as resp:
                if resp.status == 200:
                    logger.info("✅ API connection successful")
                else:
                    logger.warning(f"⚠️ API connection issue: HTTP {resp.status}")
    except Exception as e:
        logger.error(f"❌ API connection failed: {e}")
    
    # Sync slash commands (both globally and to current guilds for immediate testing)
    try:
        logger.info("⚙️ Syncing slash commands...")
        
        # Sync to all guilds for immediate availability
        for guild in bot.guilds:
            try:
                synced_guild = await bot.tree.sync(guild=guild)
                logger.info(f"✅ Synced {len(synced_guild)} commands to guild: {guild.name}")
            except Exception as guild_e:
                logger.error(f"❌ Failed to sync to guild {guild.name}: {guild_e}")
        
        # Also sync globally (takes up to 1 hour to propagate)
        synced_global = await bot.tree.sync()
        logger.info(f"✅ Global slash commands synchronized: {len(synced_global)} commands")
        
        for cmd in synced_global:
            logger.info(f"  - /{cmd.name}: {cmd.description}")
            
    except Exception as e:
        logger.error(f"❌ Error syncing slash commands: {e}")
    
    logger.info("🚀 Discord bot is ready and running!")
    logger.info("📝 Note: Slash commands should now be available immediately in your server!")
    logger.info("🔑 Try using /make_admin <password> where password is '123'")

class RoleDeQuinta(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="register", description="Se registra no rolê")
    async def slash_register(self, interaction: discord.Interaction, nome: str):
        user_data = {
            "name": nome or interaction.user.display_name,
            "discord_user_id": str(interaction.user.id),
            "discord_username": str(interaction.user)
        }
        data, status = await api_post("/discord/users/register", json=user_data)
        if status in (200, 201):
            # Use the message from the API response for clear feedback
            message = data.get('message', f"✅ {user_data['name']}, tu tá registrado no rolê!")
            await interaction.response.send_message(message, ephemeral=True)
        else:
            await interaction.response.send_message(f"❌ Eita, não rolou o registro: {data.get('detail', data)}", ephemeral=True)

    @app_commands.command(name="events", description="Mostra os eventos que tão rolando agora")
    async def slash_events(self, interaction: discord.Interaction):
        data, status = await api_get("/discord/events/active")
        if status != 200 or not data:
            await interaction.response.send_message("🔍 Nenhum evento rolando agora, parça. Cola mais tarde!", ephemeral=True)
            return
        response = "🎉 **Eventos rolando agora no RolêDeQuinta:**\n"
        for event in data:
            response += f"• **{event['title']}** (ID: {event['id']})\n"
            response += f"  📝 {event.get('description', 'Sem descrição')}\n"
            response += f"  ⏰ Até: {event['end_time']}\n\n"
        response += "Manda `/attend <id_do_evento>` pra marcar presença, hein!"
        await interaction.response.send_message(response, ephemeral=True)

    @app_commands.command(name="attend", description="Marca presença no evento")
    async def slash_attend(self, interaction: discord.Interaction, event_id: int):
        params = {"discord_user_id": str(interaction.user.id)}
        data, status = await api_post(f"/discord/attend/{event_id}", params=params)
        if data.get("success"):
            event_info = data.get("event", {})
            await interaction.response.send_message(f"🎉 Presença confirmada no evento **{event_info.get('title', 'Desconhecido')}**! Agora é só curtir o rolê! 😎", ephemeral=True)
        else:
            message = data.get("message", "Erro desconhecido")
            event_status = data.get("event_status", {})
            if event_status:
                status_str = event_status.get("status", "desconhecido")
                if status_str == "upcoming":
                    minutes = (event_status.get("time_until_start", 0) // 60)
                    await interaction.response.send_message(f"⏰ Calma aí, o evento começa em {minutes} minutos. Segura a ansiedade!", ephemeral=True)
                    return
                elif status_str == "ended":
                    await interaction.response.send_message(f"⏰ Ih, perdeu o timing! Mas relaxa, semana que vem tem mais rolê.", ephemeral=True)
                    return
            await interaction.response.send_message(f"❌ {message}", ephemeral=True)

    @app_commands.command(name="status", description="Vê quantos rolês tu já colou")
    async def slash_status(self, interaction: discord.Interaction):
        data, status_code = await api_get(f"/discord/attendance/{interaction.user.id}")
        if status_code != 200 or not data:
            await interaction.response.send_message("❌ Tu não tá registrado ainda, pô! Usa `/register` aí.", ephemeral=True)
            return
        user_info = data["user"]
        attended_events = data["attended_events"]
        total = data["total_attended"]
        response = f"📊 **Status de Presença do {user_info['name']}**\n"
        response += f"🏆 Total de rolês marcados: **{total}**\n\n"
        if attended_events:
            response += "📅 **Seus últimos rolês:**\n"
            for event in attended_events[-5:]:
                response += f"• {event['title']} - {event['start_time']}\n"
            if len(attended_events) > 5:
                response += f"... e mais {len(attended_events) - 5} rolês, hein!"
        else:
            response += "📝 Ainda não marcou presença em nenhum rolê. Bora começar!"
        await interaction.response.send_message(response, ephemeral=True)

    @app_commands.command(name="create_event", description="Cria evento (só ADM sinforoso)")
    async def slash_create_event(self, interaction: discord.Interaction, title: str, description: str, start_time: str, end_time: str):
        # Check if user is admin in database instead of Discord roles
        event_data = {
            "title": title,
            "description": description,
            "start_time": start_time,
            "end_time": end_time
        }
        params = {"discord_user_id": str(interaction.user.id)}
        
        data, status = await api_post("/discord/events/create", json=event_data, params=params)
        
        if status in (200, 201):
            await interaction.response.send_message(f"✅ Evento '{title}' criado com sucesso! Agora é só avisar a galera!", ephemeral=True)
        elif status == 404:
            await interaction.response.send_message("❌ Tu não tá registrado ainda! Usa `/register` primeiro.", ephemeral=True)
        elif status == 403:
            await interaction.response.send_message("❌ Só ADM pode criar evento! Usa `/make_admin 123` pra virar admin.", ephemeral=True)
        else:
            error_msg = data.get('detail', 'Erro desconhecido')
            await interaction.response.send_message(f"❌ Deu ruim pra criar o evento: {error_msg}", ephemeral=True)

    @app_commands.command(name="event_status", description="Mostra status do evento")
    async def slash_event_status(self, interaction: discord.Interaction, event_id: int):
        data, status = await api_get(f"/discord/event/{event_id}/status")
        if status == 200 and data:
            await interaction.response.send_message(f"📋 **Status do Evento:**\n{data}", ephemeral=True)
        else:
            await interaction.response.send_message(f"❌ Não consegui pegar o status desse evento, foi mal!", ephemeral=True)

    @app_commands.command(name="event_attendees", description="Lista quem tá no evento")
    async def slash_event_attendees(self, interaction: discord.Interaction, event_id: int):
        data, status = await api_get(f"/discord/event/{event_id}/attendees")
        if status == 200 and data:
            attendees = data.get("attendees", [])
            if not attendees:
                await interaction.response.send_message("Ninguém marcou presença ainda, bora ser o primeiro!", ephemeral=True)
                return
            response = f"👥 **Quem tá no rolê {event_id}:**\n"
            for attendee in attendees:
                response += f"- {attendee['name']} ({attendee['discord_username']})\n"
            await interaction.response.send_message(response, ephemeral=True)
        else:
            await interaction.response.send_message(f"❌ Não rolou pegar a lista de presença desse evento.", ephemeral=True)

    @app_commands.command(name="user_info", description="Mostra teu perfil")
    async def slash_user_info(self, interaction: discord.Interaction):
        data, status = await api_get(f"/discord/users/{interaction.user.id}")
        if status == 200 and data:
            await interaction.response.send_message(f"👤 **Teu perfil no RolêDeQuinta:**\n{data}", ephemeral=True)
        else:
            await interaction.response.send_message(f"❌ Não achei teu perfil, tenta de novo!", ephemeral=True)

    @app_commands.command(name="make_admin", description="Vira admin do rolê (precisa da senha)")
    async def slash_make_admin(self, interaction: discord.Interaction, password: str):
        admin_data = {
            "discord_user_id": str(interaction.user.id),
            "password": password
        }
        data, status = await api_post("/discord/admin/make-admin", json=admin_data)
        
        if status == 200:
            message = data.get('message', '🎉 Agora tu é admin!')
            await interaction.response.send_message(message, ephemeral=True)
        else:
            error_msg = data.get('detail', 'Erro desconhecido')
            await interaction.response.send_message(f"❌ {error_msg}", ephemeral=True)

    @app_commands.command(name="bothelp", description="Mostra essa ajuda")
    async def slash_bothelp(self, interaction: discord.Interaction):
        help_text = '''🤖 **Comandos do RolêDeQuinta** (powered by sinforoso lifestyle)

📝 /register [nome] - Se registra no rolê
🎉 /events - Mostra os eventos que tão rolando agora
✅ /attend <id_do_evento> - Marca presença no evento
📊 /status - Vê quantos rolês tu já colou
🔑 /make_admin <senha> - Vira admin do rolê (precisa da senha)
➕ /create_event "Título" "Descrição" "AAAA-MM-DDTHH:MM:SS" "AAAA-MM-DDTHH:MM:SS" - Cria evento (só ADM sinforoso)
📋 /event_status <id_do_evento> - Mostra status do evento
👥 /event_attendees <id_do_evento> - Lista quem tá no evento
👤 /user_info - Mostra teu perfil
❓ /bothelp - Mostra essa ajuda

**Dúvida? Fala com o grupo sinforoso lifestyle!**'''
        await interaction.response.send_message(help_text, ephemeral=True)

async def main():
    try:
        logger.info("🔧 Adding RoleDeQuinta cog to bot...")
        await bot.add_cog(RoleDeQuinta(bot))
        logger.info("✅ Cog added successfully")
        
        logger.info("🤖 Starting Discord bot connection...")
        await bot.start(TOKEN)
    except Exception as e:
        logger.error(f"❌ Error starting bot: {e}")
        raise

if __name__ == "__main__":
    try:
        logger.info("🚀 Initializing Discord bot application...")
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("🛑 Bot stopped by user (KeyboardInterrupt)")
    except Exception as e:
        logger.error(f"❌ Fatal error: {e}")
        exit(1) 