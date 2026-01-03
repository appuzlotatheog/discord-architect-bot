import discord
from discord import app_commands
from discord.ext import commands
from utils.ai import generate_blueprint, modify_blueprint
from utils.builder import build_server, get_server_structure, nuke_server
from utils.memory import MemoryManager
import json
import io

class Architect(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.blueprints = {} # Store blueprints by guild_id
        self.styles = {} # Store styles by guild_id

    def get_memory(self, guild_id):
        return MemoryManager(guild_id)

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if not interaction.guild:
            await interaction.response.send_message("This command can only be used in a server.", ephemeral=True)
            return False
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("❌ You need **Administrator** permissions to use this bot.", ephemeral=True)
            return False
        return True

    @app_commands.command(name="style", description="Set the overall server aesthetic")
    @app_commands.choices(type=[
        app_commands.Choice(name="Minimal", value="minimal"),
        app_commands.Choice(name="Detailed", value="detailed"),
        app_commands.Choice(name="Themed", value="themed"),
        app_commands.Choice(name="Professional", value="professional"),
        app_commands.Choice(name="Gaming", value="gaming"),
        app_commands.Choice(name="Community", value="community")
    ])
    async def style(self, interaction: discord.Interaction, type: app_commands.Choice[str]):
        self.styles[interaction.guild_id] = type.value
        await interaction.response.send_message(f"Server style set to: **{type.name}**", ephemeral=True)

    @app_commands.command(name="architect", description="Create a server structure from a description")
    async def architect(self, interaction: discord.Interaction, description: str):
        await interaction.response.defer()
        try:
            memory = self.get_memory(interaction.guild_id)
            history = await memory.get_context()
            current_structure = await get_server_structure(interaction.guild)
            style = self.styles.get(interaction.guild_id, "standard")
            
            async def status_callback(msg):
                try:
                    await interaction.edit_original_response(content=msg)
                except: pass

            blueprint = await generate_blueprint(description, style, history, current_structure, status_callback)
            self.blueprints[interaction.guild_id] = blueprint
            
            # Store interaction
            await memory.store_interaction(interaction.user.id, description, blueprint)

            # Create a summary embed
            embed = discord.Embed(title="Server Blueprint Generated", description=blueprint.get('description', 'No description'), color=discord.Color.blue())
            embed.add_field(name="Server Name", value=blueprint.get('server_name', 'N/A'), inline=False)
            
            categories = blueprint.get('categories', [])
            embed.add_field(name="Structure", value=f"{len(categories)} categories, {sum(len(c.get('channels', [])) for c in categories)} channels", inline=False)
            
            view = ConfirmView(self.bot, blueprint)
            await interaction.followup.send(embed=embed, view=view)
        except Exception as e:
            await interaction.followup.send(f"An error occurred: {str(e)}")

    @app_commands.command(name="recall", description="Show previous setup requests for this server")
    async def recall(self, interaction: discord.Interaction):
        memory = self.get_memory(interaction.guild_id)
        history = await memory.get_context(limit=5)
        
        if not history:
            await interaction.response.send_message("No history found for this server.", ephemeral=True)
            return

        embed = discord.Embed(title="Server History", color=discord.Color.gold())
        for i, entry in enumerate(history, 1):
            embed.add_field(
                name=f"{i}. {entry['timestamp']}", 
                value=f"Request: {entry['request'][:100]}...", 
                inline=False
            )
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="quick_setup", description="Use a preset template")
    @app_commands.choices(template=[
        app_commands.Choice(name="Gaming Community", value="gaming"),
        app_commands.Choice(name="Study Group", value="study"),
        app_commands.Choice(name="Professional Team", value="professional"),
        app_commands.Choice(name="Friends Hangout", value="friends")
    ])
    async def quick_setup(self, interaction: discord.Interaction, template: app_commands.Choice[str]):
        await interaction.response.defer()
        # Pre-defined prompts for templates
        prompts = {
            "gaming": "Create a comprehensive gaming server with general chat, voice channels for different games, a clips channel, and roles for different ranks.",
            "study": "Create a study server with subject-specific channels, quiet study voice rooms, resource sharing channels, and roles for tutors and students.",
            "professional": "Create a professional workspace with department channels, meeting rooms, announcement channels, and a project management structure.",
            "friends": "Create a casual server for friends with a general chat, meme channel, music bot channel, and a few voice channels."
        }
        
        description = prompts.get(template.value, "Create a standard Discord server.")
        # Reuse architect logic
        await self.architect.callback(self, interaction, description)

    @app_commands.command(name="preview", description="Preview the current blueprint")
    async def preview(self, interaction: discord.Interaction):
        blueprint = self.blueprints.get(interaction.guild_id)
        if not blueprint:
            await interaction.response.send_message("No blueprint found. Use /architect first.", ephemeral=True)
            return
        
        file = discord.File(io.StringIO(json.dumps(blueprint, indent=2)), filename="blueprint.json")
        await interaction.response.send_message("Current blueprint:", file=file, ephemeral=True)

    @app_commands.command(name="modify", description="Modify the current blueprint")
    async def modify(self, interaction: discord.Interaction, changes: str):
        blueprint = self.blueprints.get(interaction.guild_id)
        if not blueprint:
            await interaction.response.send_message("No blueprint found. Use /architect first.", ephemeral=True)
            return

        await interaction.response.defer()
        try:
            async def status_callback(msg):
                try:
                    await interaction.edit_original_response(content=msg)
                except: pass

            new_blueprint = await modify_blueprint(blueprint, changes, status_callback)
            self.blueprints[interaction.guild_id] = new_blueprint
            
            # Create a summary embed
            embed = discord.Embed(title="Blueprint Modified", description=new_blueprint.get('description', 'No description'), color=discord.Color.green())
            embed.add_field(name="Server Name", value=new_blueprint.get('server_name', 'N/A'), inline=False)
            
            categories = new_blueprint.get('categories', [])
            embed.add_field(name="Structure", value=f"{len(categories)} categories, {sum(len(c.get('channels', [])) for c in categories)} channels", inline=False)
            
            view = ConfirmView(self.bot, new_blueprint)
            await interaction.followup.send(embed=embed, view=view)
        except Exception as e:
            await interaction.followup.send(f"An error occurred: {str(e)}")

    @app_commands.command(name="backup", description="Create a backup of the current server")
    async def backup(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        try:
            structure = await get_server_structure(interaction.guild)
            memory = self.get_memory(interaction.guild_id)
            await memory.create_backup(structure)
            await interaction.followup.send("✅ Backup created successfully!", ephemeral=True)
        except Exception as e:
            await interaction.followup.send(f"Failed to create backup: {e}", ephemeral=True)

    @app_commands.command(name="clean_slate", description="⚠️ DANGEROUS: Delete all channels and categories")
    async def clean_slate(self, interaction: discord.Interaction):
        # Double confirmation
        view = CleanSlateView(self.bot)
        await interaction.response.send_message("⚠️ **WARNING**: This will delete ALL channels and categories in this server. This action cannot be undone.\n\nAre you sure?", view=view, ephemeral=True)

class CleanSlateView(discord.ui.View):
    def __init__(self, bot):
        super().__init__()
        self.bot = bot

    @discord.ui.button(label="CONFIRM DELETE EVERYTHING", style=discord.ButtonStyle.danger)
    async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("Starting clean slate protocol...", ephemeral=True)
        await nuke_server(interaction.guild)
        await interaction.followup.send("Server has been wiped.", ephemeral=True)

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.secondary)
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("Cancelled.", ephemeral=True)

class ConfirmView(discord.ui.View):
    def __init__(self, bot, blueprint):
        super().__init__()
        self.bot = bot
        self.blueprint = blueprint

    @discord.ui.button(label="Build Server", style=discord.ButtonStyle.green, emoji="🏗️")
    async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("🚀 **Initializing Construction Protocol...**", ephemeral=True)
        message = await interaction.original_response()
        
        async def progress_callback(current, total, status):
            percent = int((current / total) * 100)
            bar_length = 10
            filled_length = int(bar_length * current // total)
            bar = "▓" * filled_length + "░" * (bar_length - filled_length)
            
            embed = discord.Embed(title="🏗️ Building Server...", color=discord.Color.from_rgb(0, 255, 255))
            embed.add_field(name="Progress", value=f"`[{bar}]` **{percent}%**", inline=False)
            embed.add_field(name="Status", value=f"*{status}*", inline=False)
            embed.set_footer(text="Architect Bot • Construction in progress")
            
            try:
                await message.edit(content=None, embed=embed)
            except: pass

        await build_server(interaction.guild, self.blueprint, progress_callback)
        
        final_embed = discord.Embed(title="✅ Construction Complete!", description="Your server has been successfully built according to the blueprint.", color=discord.Color.from_rgb(0, 255, 127))
        final_embed.set_thumbnail(url="https://cdn-icons-png.flaticon.com/512/190/190411.png")
        final_embed.add_field(name="Next Steps", value="• Review the created roles and permissions\n• Invite your friends!\n• Use `/modify` if you need changes", inline=False)
        final_embed.set_footer(text="Architect Bot • Ready for action")
        
        await message.edit(content=None, embed=final_embed)

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.red, emoji="✖️")
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = discord.Embed(title="❌ Construction Cancelled", description="The blueprint has been discarded.", color=discord.Color.red())
        await interaction.response.send_message(embed=embed, ephemeral=True)

async def setup(bot):
    await bot.add_cog(Architect(bot))
