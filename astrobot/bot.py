import os
import time
import logging
import discord
from discord.ext import commands

from astrobot import __version__ as astrobot_v
from astrobot import __changelog__
from astrobot.colors import MochjiColor
from astrobot.init_cogs import init_cogs

LOG_DIR = os.environ["LOG_DIR"]

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

    # initalize pycord logger
    log_time = int(time.time())
    logger = logging.getLogger('discord')
    logger.setLevel(logging.DEBUG)
    handler = logging.FileHandler(filename=f'{LOG_DIR}/{log_time}.log', encoding='utf-8', mode='w')
    handler.setFormatter(logging.Formatter('[%(asctime)s][ %(levelname)s ] %(name)s: %(message)s'))
    logger.addHandler(handler)

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
        print(f'Logged in as: {bot.user}, Prefix= "{prefix}"')
    
    @bot.event
    async def on_command(ctx: commands.context.Context):
        # TODO: consider integrating into database instead of logfile
        _t = time.localtime()
        if not os.path.isdir(f"{LOG_DIR}/{ctx.author.name}"): os.mkdir(f"{LOG_DIR}/{ctx.author.name}") # create user log directory if does not exist
        with open(f"{LOG_DIR}/{ctx.author.name}/invokes.log", 'a') as _log:
            # log invoked command with timestamp and invoke server
            print(f"[ {str(_t.tm_year)[2:]}.{_t.tm_mday}.{_t.tm_mon} - {_t.tm_hour}:{_t.tm_min}:{_t.tm_sec} ] {ctx.author} {'attempted to invoke' if ctx.command_failed else 'invoked'} command '{ctx.command}' in {ctx.guild}", file=_log)
    
    bot.run(os.environ["BOT_TOKEN"])


