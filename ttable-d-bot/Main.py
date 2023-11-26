import discord
import logging
import os

from discord.ext import commands
from constants.common import *

logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)
logger = logging.getLogger(__name__)


class UQTimetableBot(commands.Bot):
    def __init__(self, command_prefix="T!"):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True
        intents.presences = True

        super().__init__(command_prefix=command_prefix, intents=intents)

        # Add your events and commands here

    # Event: Bot is ready
    async def on_ready(self) -> None:
        logger.info(f"Logged in as {self.user.name}")

    async def setup_hook(self) -> None:
        await super().setup_hook()
        self.remove_command("help")
        await self.load_cogs()

    async def load_cogs(self) -> None:
        for filename in os.listdir("./cogs"):
            if (filename.endswith(PY_FILE_EXTENSION) and
                    filename.startswith(COG_PRE)):
                await self.load_extension(
                    f"cogs.{filename[:-len(PY_FILE_EXTENSION)]}")

    async def reload_cogs(self) -> None:
        for filename in os.listdir("./cogs"):
            if (filename.endswith(PY_FILE_EXTENSION) and
                    filename.startswith(COG_PRE)):
                await self.reload_extension(
                    f"cogs.{filename[:-len(PY_FILE_EXTENSION)]}")


if __name__ == "__main__":
    # Create an instance of your bot
    bot = UQTimetableBot()

    # Run the bot with your token
    bot.run("no")
