import os
import time
import collections
import discord
from discord.ext import commands
from astrobot import (
    __version__ as astrobot_v,
    __changelog__,
    util
)
from astrobot.colors import MochjiColor
from astrobot.cogs import init_cogs
from astrobot.time import (
    database as timedb,
    Reminders,
    RemindersTimer
)

class MochjiActivity(discord.Activity):
    def __init__(self):
        super().__init__()
        self.name = f"Mr. Robot | v{astrobot_v}"
        self.type = discord.ActivityType.watching

class AstrobotHelpCommand(commands.DefaultHelpCommand):
    def __init__(self, **options):
        super().__init__(**options)

class Astrobot(commands.Bot):
    def __init__(self, help_command=AstrobotHelpCommand(), **options):

        if not os.environ.get("DEVEL"):
            prefix = '!' # use ! prefix in production (astrobot)
        else:
            prefix = '.' # use . prefix in development (ObamaBot)

        super().__init__(prefix, help_command, **options)
        self.remindme_timers = collections.defaultdict(list)

def start_client():

    # initialize bot object
    bot = Astrobot(
        intents=discord.Intents.all(),
        activity=MochjiActivity())

    # initialize all bot cogs
    init_cogs(bot)

    @bot.command(brief="Return bot version", help="Return bot version.")
    async def version(ctx):
        """Return current version bot is running."""
        text = f"Current astrobot version is '{astrobot_v}'"
        embed = discord.Embed(
            title=text,
            description="**You can view this version's changes with the '!changelog' command**",
            color=MochjiColor.white()
        )
        await ctx.send(embed=embed)

    @bot.command(brief="Return changelog for current bot version",
                 help="Return changelog for current bot version.")
    async def changelog(ctx):
        """Return changelog for current bot version."""
        embed = discord.Embed(
            title=f"**astrobot v{astrobot_v} CHANGELOG**",
            description=__changelog__,
            color=MochjiColor.white()
        )
        await ctx.send(embed=embed)
    @bot.command(brief="Delete all DMs from bot",
                 help="Delete all DMs recieved from bot.")
    async def delete_dm_history(ctx):
        """Delete all DMs from bot."""
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

        async def reinit_reminders():
            """Reinit reminders, and send outstanding reminders."""
            _now = int(time.time())
            _reminder_count = 0
            for timer in timedb.session.query(timedb.Reminders):
                exp = int(timer.remind_at) - _now
                if exp < 0:
                    await Reminders.send_reminder(bot, timer.channel_id, timer.user_id, timer.reminder_text, -exp)
                    continue
                reminder_timer = RemindersTimer(exp, Reminders.send_reminder, bot, timer.channel_id, timer.user_id, timer.reminder_text, reminder_text=timer.reminder_text)
                bot.remindme_timers[int(timer.user_id)].append(reminder_timer)
                _reminder_count += 1
            return _reminder_count

        print(f"Reinitialized {await reinit_reminders()} reminders.")
        print(f'Logged in as: {bot.user}, Prefix= "{bot.command_prefix}", using py-cord version: {discord.__version__}')

    bot.run(os.environ["BOT_TOKEN"])
    """ 
    (keeping the de-abstracted bot init here for rn, may need it in the future, but for rn, bot.run is fine ig)
    try:
        loop = bot.loop
        loop.add_signal_handler(signal.SIGINT, loop.stop)
        loop.add_signal_handler(signal.SIGTERM, loop.stop)
        loop.run_until_complete(bot.start(os.environ["BOT_TOKEN"])) # start bot
    except KeyboardInterrupt:
        loop.run_until_complete(bot.close())
    finally:
        loop.close()
    """


if __name__ == "__main__":
    start_client()
