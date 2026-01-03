import discord
from discord.ext import commands
from discord import app_commands
import time

class General(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="ping", description="Check the bot's latency.")
    async def ping(self, interaction: discord.Interaction):
        latency = round(self.bot.latency * 1000)
        embed = discord.Embed(
            title="🏓 Pong!",
            description=f"Latency: **{latency}ms**",
            color=discord.Color.green()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="info", description="Get information about the bot.")
    async def info(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="🏗️ Discord Architect Bot",
            description="An advanced AI-powered Discord server builder.",
            color=discord.Color.blue()
        )
        embed.add_field(name="Developer", value="[Your Name/Handle]", inline=True)
        embed.add_field(name="Library", value=f"discord.py {discord.__version__}", inline=True)
        embed.add_field(name="AI Models", value="Groq, Google Gemini, OpenRouter", inline=False)
        embed.set_footer(text="Open Source Project")
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="help", description="List available commands.")
    async def help(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="📚 Help Center",
            description="Here are the available commands:",
            color=discord.Color.gold()
        )
        
        # Architect Commands
        embed.add_field(
            name="🏗️ Architect",
            value=(
                "`/architect [description] [style]` - Generate a server blueprint\n"
                "`/preview` - Preview the current blueprint\n"
                "`/modify [changes]` - Modify the current blueprint\n"
                "`/build` - Build the server from the blueprint\n"
                "`/backup [name]` - Create a backup of the server\n"
                "`/clean_slate` - Delete all channels and roles (Dangerous!)\n"
                "`/recall` - Undo the last build action"
            ),
            inline=False
        )
        
        # General Commands
        embed.add_field(
            name="⚙️ General",
            value=(
                "`/ping` - Check latency\n"
                "`/info` - Bot information\n"
                "`/help` - Show this message"
            ),
            inline=False
        )
        
        await interaction.response.send_message(embed=embed, ephemeral=True)

async def setup(bot):
    await bot.add_cog(General(bot))
