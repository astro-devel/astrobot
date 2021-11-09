import os
import time
import logging
import discord
from discord.ext import commands

from astrobot import __version__ as astrobot_v
from astrobot.colors import MochjiColor
from astrobot.emojis import MochjiMojis
from astrobot.error import ErrorHandler
from astrobot.management import Management
from astrobot.moderation import Moderation
from astrobot.test import TestCommands
from astrobot.time import TimeStuffs
from astrobot.user import UserInfo
from astrobot.welcome import WelcomeWagon
from astrobot.roles import Roles

class MochjiActivity(discord.Activity):
    def __init__(self):
        super().__init__()
        self.name = "with your mom"

def start_client():
    if not os.environ.get("DEVEL"):
        prefix = '!'
    else:
        prefix = '.'
    bot = commands.Bot(command_prefix=prefix,
                    intents=discord.Intents.all(),
                    activity=MochjiActivity())

    if os.environ.get("DEVEL"):
        # cog(s) that should ONLY be enabled during devel
        bot.add_cog(TestCommands(bot))
    else:
        # cog(s) that should NOT be enabled during devel
        bot.add_cog(WelcomeWagon(bot))

    bot.add_cog(UserInfo(bot))
    bot.add_cog(MochjiMojis(bot))
    bot.add_cog(TimeStuffs(bot))
    bot.add_cog(ErrorHandler(bot))
    bot.add_cog(Moderation(bot))
    bot.add_cog(Roles(bot))
    bot.add_cog(Management(bot))

    # TODO: remember to uncomment logger block when begin self-hosting bot
    '''
    log_time = int(time.time())
    logger = logging.getLogger('discord')
    logger.setLevel(logging.DEBUG)
    handler = logging.FileHandler(filename=f'logs/{log_time}.log', encoding='utf-8', mode='w')
    handler.setFormatter(logging.Formatter('[%(asctime)s][ %(levelname)s ] %(name)s: %(message)s'))
    logger.addHandler(handler)
    '''

    @bot.command(brief="Return bot version", help="Return bot version.")
    async def version(ctx):
        text = f"Current astrobot version is '{astrobot_v}'"
        embed = discord.Embed(
            title=text,
            color=MochjiColor.white()
        )
        await ctx.send(embed=embed)
    
    @bot.command(brief="Delete all DMs from bot", help="Delete all DMs recieved from bot.")
    async def delete_dm_history(ctx):
        await ctx.author.create_dm()
        channel: discord.DMChannel | None = ctx.author.dm_channel
        if channel:
            async for message in channel.history():
                if message.author == bot.user:
                    await message.delete()
        else:
            return
        embed = discord.Embed(
            title=f"{await bot.get_cog('MochjiMojis').success()} Successfully deleted all my messages to you.",
            footer="NOTE: this does not affect your server warn/kick counts.",
            color=MochjiColor.green()
        )
        await ctx.send(embed=embed)

    @bot.event
    async def on_ready():
        print(f'Logged in as: {bot.user}, Prefix= "{prefix}"')

    bot.run(os.environ["BOT_TOKEN"])


