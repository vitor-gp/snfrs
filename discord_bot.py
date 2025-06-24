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

API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")
TOKEN = os.getenv("DISCORD_BOT_TOKEN")
if not TOKEN:
    raise ValueError("DISCORD_BOT_TOKEN environment variable is required")

ADMIN_ROLE = os.getenv("DISCORD_ADMIN_ROLE", "Admin")
ADMIN_API_TOKEN = os.getenv("ADMIN_API_TOKEN", "")

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

async def api_post(endpoint, json=None, params=None):
    async with aiohttp.ClientSession() as session:
        async with session.post(f"{API_BASE_URL}{endpoint}", json=json, params=params) as resp:
            return await resp.json(), resp.status

async def api_get(endpoint, params=None):
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{API_BASE_URL}{endpoint}", params=params) as resp:
            return await resp.json(), resp.status

@bot.event
async def on_ready():
    print(f"Logado como {bot.user} (ID: {bot.user.id})")
    print("------ RolêDeQuinta tá online, gerenciado pelo grupo sinforoso lifestyle ------")
    try:
        synced = await bot.tree.sync()
        print(f"Slash commands sincronizados: {len(synced)} comandos.")
    except Exception as e:
        print(f"Erro ao sincronizar slash commands: {e}")

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
            await interaction.response.send_message(f"✅ {user_data['name']}, tu tá registrado no rolê! Bora marcar presença, hein?", ephemeral=True)
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
        if ADMIN_ROLE not in [role.name for role in interaction.user.roles]:
            await interaction.response.send_message("❌ Só ADM do sinforoso lifestyle pode criar evento, malandro!", ephemeral=True)
            return
        headers = {"Authorization": f"Bearer {ADMIN_API_TOKEN}"} if ADMIN_API_TOKEN else {}
        event_data = {
            "title": title,
            "description": description,
            "start_time": start_time,
            "end_time": end_time
        }
        async with aiohttp.ClientSession() as session:
            async with session.post(f"{API_BASE_URL}/events/", json=event_data, headers=headers) as resp:
                data = await resp.json()
                if resp.status in (200, 201):
                    await interaction.response.send_message(f"✅ Evento '{title}' criado com sucesso! Agora é só avisar a galera!", ephemeral=True)
                else:
                    await interaction.response.send_message(f"❌ Deu ruim pra criar o evento: {data.get('detail', data)}", ephemeral=True)

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

    @app_commands.command(name="bothelp", description="Mostra essa ajuda")
    async def slash_bothelp(self, interaction: discord.Interaction):
        help_text = '''🤖 **Comandos do RolêDeQuinta** (powered by sinforoso lifestyle)

📝 /register [nome] - Se registra no rolê
🎉 /events - Mostra os eventos que tão rolando agora
✅ /attend <id_do_evento> - Marca presença no evento
📊 /status - Vê quantos rolês tu já colou
➕ /create_event "Título" "Descrição" "AAAA-MM-DDTHH:MM:SS" "AAAA-MM-DDTHH:MM:SS" - Cria evento (só ADM sinforoso)
📋 /event_status <id_do_evento> - Mostra status do evento
👥 /event_attendees <id_do_evento> - Lista quem tá no evento
👤 /user_info - Mostra teu perfil
❓ /bothelp - Mostra essa ajuda

**Dúvida? Fala com o grupo sinforoso lifestyle!**'''
        await interaction.response.send_message(help_text, ephemeral=True)

if __name__ == "__main__":
    async def main():
        await bot.add_cog(RoleDeQuinta(bot))
        await bot.start(TOKEN)

    asyncio.run(main()) 