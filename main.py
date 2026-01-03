import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
import asyncio

# Load environment variables
load_dotenv()

TOKEN = os.getenv('DISCORD_TOKEN')
APP_ID = os.getenv('DISCORD_APP_ID')

from utils.database import init_db

class ArchitectBot(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix='!',
            intents=discord.Intents.default(),
            application_id=APP_ID
        )

    async def setup_hook(self):
        await init_db()
        await self.load_extension('cogs.architect')
        await self.load_extension('cogs.general')
        await self.tree.sync()
        print("Commands synced")

    async def on_ready(self):
        print(f'Logged in as {self.user} (ID: {self.user.id})')
        print('------')

async def main():
    bot = ArchitectBot()
    async with bot:
        await bot.start(TOKEN)

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
