import os
import time
import logging
import discord
from discord.ext import commands

from astrobot import __version__ as astrobot_v
from astrobot import (
    __changelog__,
    util
)
from astrobot.colors import MochjiColor
from astrobot.cogs import init_cogs
from astrobot.user_sys.database import (
    CommandLog__Obj as DB_CommandLog__Obj,
    session as db_session
) 

class MochjiActivity(discord.Activity):
    def __init__(self):
        super().__init__()
        self.name = "Mr. Robot"
        self.type = discord.ActivityType.watching
        self.timestamps = {
            "start": 1635626843000
        }

def start_client():
    if not os.environ.get("DEVEL"):
        prefix = '!' # use ! prefix in production (astrobot)
    else:
        prefix = '.' # use . prefix in development (ObamaBot)
    
    # initialize bot object
    bot = commands.Bot(command_prefix=prefix,
                    intents=discord.Intents.all(),
                    activity=MochjiActivity())

    # initialize all bot cogs
    init_cogs(bot)

    @bot.command(brief="Return bot version", help="Return bot version.")
    async def version(ctx):
        """Return current version bot is running"""
        text = f"Current astrobot version is '{astrobot_v}'"
        embed = discord.Embed(
            title=text,
            description="**You can view this version's changes with the '!changelog' command**",
            color=MochjiColor.white()
        )
        await ctx.send(embed=embed)
    
    @bot.command(brief="Return changelog for current bot version", help="Return changelog for current bot version.")
    async def changelog(ctx):
        """Return changelog for current bot version"""
        embed = discord.Embed(
            title=f"**astrobot v{astrobot_v} CHANGELOG**",
            description=__changelog__,
            color=MochjiColor.white()
        )
        await ctx.send(embed=embed)
    @bot.command(brief="Delete all DMs from bot", help="Delete all DMs recieved from bot.")
    async def delete_dm_history(ctx):
        """Delete all DMs from bot"""
        await ctx.author.create_dm() # attempt to open DMChannel with user
        channel = ctx.author.dm_channel
        if channel: # if user is able to recieve DMs
            async for message in channel.history():
                if message.author == bot.user:
                    # there's gotta be a better way to do this bc what
                    # ends up happening is there are a lot of user messages and
                    # deletion thread starts getting hung up
                    #
                    # TODO: implement method for auto-skipping over known non-bot msgs
                    await message.delete()
        else: # if user is not able to recieve DMs
            return
        embed = discord.Embed(
            title=f"{await bot.get_cog('MochjiMojis').success()} Successfully deleted all my messages to you.",
            footer="NOTE: this does not affect your server warn/kick counts.",
            color=MochjiColor.green()
        )
        await ctx.send(embed=embed)

    @bot.event
    async def on_ready():
        print(f'Logged in as: {bot.user}, Prefix= "{prefix}", using py-cord version: {discord.__version__} (frozen at commit \'16f9bcb\' for "stability")')

    bot.run(os.environ["BOT_TOKEN"])


if __name__ == "__main__":
    start_client()
