"""
Events Cog for Discord Bot

This module contains all event-related Discord slash commands for the
SNFRS Event Attendance System.
"""

import json
import logging

import aiohttp
import discord
from discord import app_commands
from discord.ext import commands


class EventsCog(commands.Cog):
    """Discord Cog for handling event-related commands."""

    def __init__(self, bot):
        """Initialize the EventsCog with bot instance."""
        self.bot = bot
        self.api_base_url = bot.config.api_base_url
        self.logger = logging.getLogger(__name__)

    async def api_post(self, endpoint: str, json=None, params=None):
        """Make a POST request to the API."""
        url = f"{self.api_base_url}{endpoint}"
        self.logger.debug(f"📤 POST {url} - Data: {json} - Params: {params}")
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=json, params=params) as resp:
                try:
                    # Check content type first
                    content_type = resp.headers.get('content-type', '')
                    if 'application/json' in content_type:
                        data = await resp.json()
                    else:
                        # If not JSON, get text and try to parse it
                        text_data = await resp.text()
                        self.logger.warning(f"Non-JSON response from {url}: {text_data[:200]}...")
                        try:
                            data = json.loads(text_data)
                        except json.JSONDecodeError:
                            # If we can't parse as JSON, return the text as an error
                            data = {"error": f"API returned non-JSON response: {text_data[:100]}..."}

                    self.logger.debug(f"📥 POST {url} - Status: {resp.status} - Response: {data}")
                    return data, resp.status
                except Exception as e:
                    self.logger.error(f"Error parsing response from {url}: {e}")
                    return {"error": f"Failed to parse API response: {str(e)}"}, resp.status

    async def api_get(self, endpoint: str, params=None):
        """Make a GET request to the API."""
        url = f"{self.api_base_url}{endpoint}"
        self.logger.debug(f"📤 GET {url} - Params: {params}")
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as resp:
                try:
                    # Check content type first
                    content_type = resp.headers.get('content-type', '')
                    if 'application/json' in content_type:
                        data = await resp.json()
                    else:
                        # If not JSON, get text and try to parse it
                        text_data = await resp.text()
                        self.logger.warning(f"Non-JSON response from {url}: {text_data[:200]}...")
                        try:
                            data = json.loads(text_data)
                        except json.JSONDecodeError:
                            # If we can't parse as JSON, return the text as an error
                            data = {"error": f"API returned non-JSON response: {text_data[:100]}..."}

                    self.logger.debug(f"📥 GET {url} - Status: {resp.status} - Response: {data}")
                    return data, resp.status
                except Exception as e:
                    self.logger.error(f"Error parsing response from {url}: {e}")
                    return {"error": f"Failed to parse API response: {str(e)}"}, resp.status

    @app_commands.command(name="register", description="Se cadastra no rolê e define teu nome")
    async def slash_register(self, interaction: discord.Interaction, nome: str = None):
        """Register for event attendance and set name."""
        user_name = nome or interaction.user.display_name

        data, status_code = await self.api_post("/discord/users/register", json={
            "name": user_name,
            "discord_user_id": str(interaction.user.id),
            "discord_username": interaction.user.name
        })

        if status_code == 200:
            message = data.get("message", f"Tá ligado! Agora tu é o **{user_name}** no rolê")
            await interaction.response.send_message(f"✅ {message} 🎉", ephemeral=True)
        else:
            await interaction.response.send_message(
                f"❌ Ó, deu zebra no cadastro: {data.get('detail', data)} 😅", ephemeral=True
            )

    @app_commands.command(name="events", description="Cola os rolês que tão bombando agora")
    async def slash_events(self, interaction: discord.Interaction):
        """Show currently active events."""
        data, _ = await self.api_get("/discord/events/active")

        if not data:
            await interaction.response.send_message(
                "🤷‍♂️ Ó mano, não tem rolê bombando agora não. Volta aqui depois!", ephemeral=True
            )
            return

        events_text = "🔥 **ROLÊS QUE TÃO BOMBANDO:**\n"
        for event in data:
            events_text += f"• **{event['title']}** (ID: {event['id']})\n"
            events_text += f"  📝 {event.get('description', 'Vai ser sinforoso, confia!')}\n"
            events_text += f"  ⏰ Até: {event['end_time']}\n\n"

        await interaction.response.send_message(events_text, ephemeral=True)

    @app_commands.command(name="bater-ponto", description="Marca presença no rolê que tá rolando")
    async def slash_bater_ponto(self, interaction: discord.Interaction):
        """Mark attendance for the current event."""
        response_data, status_code = await self.api_post(
            f"/discord/attend/auto?discord_user_id={interaction.user.id}"
        )

        if status_code == 200 and response_data.get("success"):
            await interaction.response.send_message(
                f"✅ {response_data['message']} 🎊", ephemeral=True
            )
        else:
            error_msg = (
                response_data.get("message", "Algo deu errado, parça") if response_data 
                else "API tá fora do ar"
            )
            await interaction.response.send_message(
                f"❌ {error_msg} 😔", ephemeral=True
            )

    @app_commands.command(name="status", description="Vê quantos rolês tu já colou na vida")
    async def slash_status(self, interaction: discord.Interaction):
        """Check your attendance status."""
        data, status_code = await self.api_get(f"/discord/attendance/{interaction.user.id}")

        if status_code == 200:
            total = data['total_attended']
            if total == 0:
                await interaction.response.send_message(
                    "📊 Rapaz, tu ainda não colou em nenhum rolê! Bora quebrar esse jejum! 😜", ephemeral=True
                )
            elif total == 1:
                await interaction.response.send_message(
                    "📊 Tu colou em 1 rolê! Tá começando a pegar o jeito! 🚀", ephemeral=True
                )
            else:
                await interaction.response.send_message(
                    f"📊 Ó o sinforoso! Tu já colou em {total} rolês! Tá viciado mesmo! 🔥🎉", ephemeral=True
                )
        else:
            await interaction.response.send_message(
                "❌ Ó meu, tu não tá cadastrado ainda não! Manda um `/register` aí primeiro! 😉", ephemeral=True
            )

    @app_commands.command(
        name="create_event",
        description="Cria um rolê novo (só pros admins sinforosos)"
    )
    async def slash_create_event(
        self,
        interaction: discord.Interaction,
        title: str,
        description: str,
        start_time: str,
        end_time: str
    ):
        """Create an event (admin only)."""
        event_data = {
            "title": title,
            "description": description,
            "start_time": start_time,
            "end_time": end_time
        }

        data, status_code = await self.api_post(
            f"/discord/events/create?discord_user_id={interaction.user.id}", json=event_data
        )

        if status_code == 200:
            await interaction.response.send_message(
                f"✅ Show! O rolê '{title}' tá criado e pronto pra bombar! Agora avisa a galera! 🎉🔥",
                ephemeral=True
            )
        elif status_code == 404:
            await interaction.response.send_message(
                "❌ Ô meu, tu não tá cadastrado! Manda um `/register` primeiro! 😅", ephemeral=True
            )
        elif status_code == 403:
            await interaction.response.send_message(
                "❌ Só os admins sinforosos podem criar rolê! Cola no `/make_admin 123` se tu for parça! 😎",
                ephemeral=True
            )
        else:
            error_msg = data.get("detail", "Sei lá o que deu errado") if data else "API bugou"
            await interaction.response.send_message(
                f"❌ Deu ruim pra criar o rolê: {error_msg} 😔", ephemeral=True
            )

    @app_commands.command(name="event_status", description="Cola como tá o rolê")
    async def slash_event_status(self, interaction: discord.Interaction, event_id: int):
        """Show event status."""
        data, status_code = await self.api_get(f"/discord/event/{event_id}/status")
        if status_code == 200:
            await interaction.response.send_message(
                f"📋 **Como tá o rolê:**\n{data}", ephemeral=True
            )
        else:
            await interaction.response.send_message(
                "❌ Não consegui pegar info desse rolê, foi mal! Tenta outro ID! 🤔", ephemeral=True
            )

    @app_commands.command(name="event_attendees", description="Vê quem tá colando no rolê")
    async def slash_event_attendees(self, interaction: discord.Interaction, event_id: int):
        """List event attendees."""
        data, status_code = await self.api_get(f"/discord/event/{event_id}/attendees")
        if status_code == 200:
            attendees = data.get("attendees", [])
            if attendees:
                attendees_list = "\n".join([f"• {att['name']}" for att in attendees])
                await interaction.response.send_message(
                    f"👥 **Galera que tá no rolê:**\n{attendees_list}", ephemeral=True
                )
            else:
                await interaction.response.send_message(
                    "😢 Rapaz, ninguém marcou presença ainda! Bora ser o primeiro parça! 🚀", ephemeral=True
                )
        else:
            await interaction.response.send_message(
                "❌ Não rolou pegar a lista de quem tá no rolê. Verifica se o ID tá certo! 🤷‍♂️", ephemeral=True
            )

    @app_commands.command(name="user_info", description="Cola teu perfil sinforoso")
    async def slash_user_info(self, interaction: discord.Interaction):
        """Show user profile information."""
        data, status_code = await self.api_get(f"/discord/users/{interaction.user.id}")
        if status_code == 200:
            await interaction.response.send_message(
                f"👤 **Teu perfil no RolêDeQuinta:**\n{data}", ephemeral=True
            )
        else:
            await interaction.response.send_message(
                "❌ Não achei teu perfil aqui não, mano! Tenta fazer `/register` primeiro! 😉", ephemeral=True
            )

    @app_commands.command(name="make_admin", description="Vira admin sinforoso (precisa da senha secreta)")
    async def slash_make_admin(self, interaction: discord.Interaction, password: str):
        """Make user admin with password."""
        data, status_code = await self.api_post("/discord/admin/make-admin", json={
            "discord_user_id": str(interaction.user.id),
            "password": password
        })

        if status_code == 200:
            await interaction.response.send_message(
                f"✅ {data.get('message', 'Opa! Agora tu é admin sinforoso!')} 👑🔥", ephemeral=True
            )
        else:
            error_msg = data.get("detail", "Senha errada ou deu ruim no sistema") if data else "API bugou"
            await interaction.response.send_message(f"❌ {error_msg} 😅", ephemeral=True)

    @app_commands.command(name="bothelp", description="Cola como usar o bot sinforoso")
    async def slash_bothelp(self, interaction: discord.Interaction):
        """Show bot help."""
        help_text = '''🤖 **COMANDOS DO ROLÊDEQUINTA** (powered by sinforoso lifestyle)

📝 `/register [nome]` - Se cadastra no rolê e define teu nome
🔥 `/events` - Cola os rolês que tão bombando agora  
✅ `/bater-ponto` - Marca presença no rolê que tá rolando
📊 `/status` - Vê quantos rolês tu já colou na vida
🔑 `/make_admin <senha>` - Vira admin sinforoso (precisa da senha secreta)
➕ `/create_event` - Cria um rolê novo (só pros admins sinforosos)
📋 `/event_status <id>` - Cola como tá o rolê
👥 `/event_attendees <id>` - Vê quem tá colando no rolê  
👤 `/user_info` - Cola teu perfil sinforoso
🔊 `/avisar-role` - Avisa a galera sobre os próximos rolês (só ADM)
🔥 `/bater-ponto-para <nome>` - Marca presença pra outro parça (só ADM)
👥 `/listar-usuarios` - Lista toda a galera cadastrada (só ADM)
❓ `/bothelp` - Mostra essa ajuda sinforosa

**Dúvida? Fala com o grupo sinforoso lifestyle! 😎🔥**'''

        await interaction.response.send_message(help_text, ephemeral=True)

    @app_commands.command(
        name="avisar-role",
        description="Avisa a galera dos próximos rolês sinforosos (só ADM)"
    )
    async def slash_avisar_role(self, interaction: discord.Interaction):
        """Notify about upcoming events (admin only)."""
        # Check if user is admin
        admin_data, admin_status = await self.api_post(
            f"/discord/admin/check-admin?discord_user_id={interaction.user.id}"
        )

        if admin_status != 200:
            await interaction.response.send_message(
                "❌ Ô meu, tu não tá cadastrado! Manda um `/register` primeiro! 😅", ephemeral=True
            )
            return

        if not admin_data.get("is_admin", False):
            await interaction.response.send_message(
                "❌ Só admin sinforoso pode avisar a galera! Cola no `/make_admin 123` se tu for parça! 😎",
                ephemeral=True
            )
            return

        # Get upcoming events
        events_data, events_status = await self.api_get("/discord/events/upcoming")
        if events_status != 200 or not events_data:
            await interaction.response.send_message(
                "❌ Não consegui pegar os próximos rolês, foi mal! API deve tá bugada! 🤷‍♂️", ephemeral=True
            )
            return

        if not events_data:
            await interaction.response.send_message(
                "📅 Rapaz, não tem nenhum rolê marcado ainda! Bora criar um evento sinforoso? 🤔",
                ephemeral=True
            )
            return

        # Find a chat channel
        chat_channel = None
        for channel in interaction.guild.channels:
            if 'chat' in channel.name.lower() and hasattr(channel, 'send'):
                chat_channel = channel
                break

        if not chat_channel:
            await interaction.response.send_message(
                "❌ Ó, não achei o canal #chat pra mandar o aviso! "
                "Verifica se tem um canal com 'chat' no nome! 🔍",
                ephemeral=True
            )
            return

        # Create announcement message
        announcement = "🎉 **PRÓXIMOS ROLÊS CONFIRMADOS, GALERA!** 🎉\n\n"
        for event in events_data[:3]:  # Limit to 3 events
            announcement += f"📅 **{event['title']}**\n"
            announcement += f"📝 {event.get('description', 'Rolê sinforoso garantido!')}\n"
            announcement += f"⏰ {event['start_time']}\n\n"

        announcement += "🔥 **BORA QUE VAI SER SINFOROSO DEMAIS!** 🔥\n"
        announcement += "💥 Usa `/register` pra se cadastrar e `/bater-ponto` durante o rolê!"

        # Send the announcement
        try:
            await chat_channel.send(announcement)
            await interaction.response.send_message(
                f"✅ Avisei a galera toda no {chat_channel.mention}! "
                f"Mandei info sobre {len(events_data)} rolê(s). Agora é só aguardar a galera chegar! 🚀",
                ephemeral=True
            )
        except discord.Forbidden:
            await interaction.response.send_message(
                f"❌ Não tenho permissão pra mandar mensagem no {chat_channel.mention}. "
                "Verifica as permissões do bot aí! 🤖",
                ephemeral=True
            )
        except Exception as e:
            await interaction.response.send_message(
                f"❌ Deu ruim pra mandar o aviso: {str(e)} 😅", ephemeral=True
            )

    @app_commands.command(
        name="listar-usuarios",
        description="Cola toda a galera registrada (só pros admins)"
    )
    async def slash_listar_usuarios(self, interaction: discord.Interaction):
        """List all registered users (admin only)."""
        # Check if user is admin first
        admin_check_data, admin_status = await self.api_post(
            f"/discord/admin/check-admin?discord_user_id={interaction.user.id}"
        )

        if admin_status != 200:
            await interaction.response.send_message(
                "❌ Só admin sinforoso pode ver a lista da galera! 😎", ephemeral=True
            )
            return

        if not admin_check_data.get("is_admin", False):
            await interaction.response.send_message(
                "❌ Ô meu, tu não tá cadastrado! Manda um `/register` primeiro! 😅", ephemeral=True
            )
            return

        # Get user list
        users_data, status = await self.api_get(
            f"/discord/users/list?discord_user_id={interaction.user.id}"
        )

        if status != 200:
            await interaction.response.send_message(
                "❌ Deu ruim pra buscar a galera. API deve tá bugada! 🤷‍♂️", ephemeral=True
            )
            return

        users = users_data.get("users", [])
        if not users:
            await interaction.response.send_message(
                "📝 Rapaz, ninguém se cadastrou ainda! Tu é o primeiro! 🚀", ephemeral=True
            )
            return

        # Format user list
        user_list = "👥 **GALERA REGISTRADA NO ROLÊ:**\n\n"
        for user in users[:20]:  # Limit to 20 users
            admin_badge = " 👑" if user.get("is_admin") else ""
            discord_name = f" (@{user.get('discord_username', 'N/A')})" if user.get('discord_username') else ""
            user_list += f"• **{user['name']}**{admin_badge}{discord_name}\n"

        if len(users) > 20:
            user_list += f"\n... e mais {len(users) - 20} pessoa(s) sinforosa(s)! 🔥"

        await interaction.response.send_message(user_list, ephemeral=True)

    @app_commands.command(
        name="bater-ponto-para",
        description="Marca presença pra outro parça (só pros admins)"
    )
    async def slash_bater_ponto_para(
        self, interaction: discord.Interaction, nome: str, evento_id: int = None
    ):
        """Mark attendance for another user (admin only)."""
        # Make API call to mark attendance
        request_data = {"target_name": nome, "event_id": evento_id}
        params = {"admin_discord_user_id": str(interaction.user.id)}

        data, status = await self.api_post(
            "/discord/admin/attend-for-user", json=request_data, params=params
        )

        if status == 200 and data.get("success"):
            # Extract data for notifications
            admin_name = data.get("admin_user", {}).get("name", "Admin")
            target_name = data.get("target_user", {}).get("name", nome)
            target_discord = data.get("target_user", {}).get("discord_username", "")
            event_title = data.get("event", {}).get("title", "rolê")

            # Send success message to admin
            await interaction.response.send_message(
                f"✅ Show! Ponto marcado pro **{target_name}** no rolê **{event_title}**! 🎊",
                ephemeral=True
            )

            # Try to notify in a public channel
            try:
                chat_channel = None
                for channel in interaction.guild.channels:
                    if 'chat' in channel.name.lower() and hasattr(channel, 'send'):
                        chat_channel = channel
                        break

                if chat_channel:
                    notification = (
                        f"🎉 **{admin_name}** marcou ponto pro **{target_name}** "
                        f"(@{target_discord}) no rolê **{event_title}**! Sinforoso demais! 🔥"
                    )
                    await chat_channel.send(notification)
            except Exception:
                pass  # Ignore notification errors

        elif status == 403:
            await interaction.response.send_message(
                "❌ Só admin sinforoso pode marcar ponto pros outros! 😎", ephemeral=True
            )
        elif status == 404:
            await interaction.response.send_message(
                "❌ Ô meu, tu não tá cadastrado! Manda um `/register` primeiro! 😅", ephemeral=True
            )
        else:
            error_msg = data.get("message", "Sei lá o que deu errado") if data else "API bugou"
            await interaction.response.send_message(f"❌ {error_msg} 😔", ephemeral=True) 