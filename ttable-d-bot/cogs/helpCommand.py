from discord.ext import commands
import discord
import logging

log_format = "[%(asctime)s] [%(levelname)-8s] %(name)s: %(message)s"
logging.basicConfig(level=logging.INFO, format=log_format)
logger = logging.getLogger(__name__)


class HelpCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.excluded_commands = ["clear-cache"]

    @commands.Cog.listener()
    async def on_ready(self):
        logger.info(f"{self.__class__.__name__} cog is ready.")

    @commands.command(name='help', help='Display custom help')
    async def custom_help(self, ctx, *args):
        if not args:
            # Display a general help message
            command_list = [f"- `{command.name}`: {command.help}"
                            for command in self.bot.commands
                            if command.name not in self.excluded_commands]

            # https://stackoverflow.com/questions/24483182/python-split-list-into-n-chunks
            split_commands = tuple(tuple(command_list[i::3]) for i in range(3))

            embed = discord.Embed(
                title="Bot Help",
                description=f"Use `{self.bot.command_prefix}help "
                            f"[command]` for more info on a command.",
                colour=discord.Colour.red())

            for index, col in enumerate(split_commands):
                embed.add_field(name=f"Column {index + 1}",
                                value="\n".join(col),
                                inline=True)

        else:
            # Display help for a specific command
            command = self.bot.get_command(args[0])
            if command:
                embed = discord.Embed(title=f"Command: {command.name}",
                                      description=command.help,
                                      colour=discord.Colour.green())

            else:
                await ctx.send("Command not found.")
                return

        embed.set_footer(text=f"Custom help command | {self.bot.user.name}")
        await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(HelpCog(bot))
    return bot
