# initialize environment variables
import dotenv

dotenv.load_dotenv()

import os
import time
import asyncio
import collections
from types import SimpleNamespace
import discord
from discord.ext import commands
from . import __version__ as astrobot_v
from .types import MochjiMojis
from .cogs import init_cogs
from .time import database as timedb, Reminders, RemindersTimer


class AstrobotHelpCommand(commands.DefaultHelpCommand):
    def __init__(self, **options):
        super().__init__(**options)


class Astrobot(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix="."
            if os.environ.get("DEVEL")
            else "!",  # '!' if production, '.' if development
            help_command=AstrobotHelpCommand(),  # astrobot custom help command
            intents=discord.Intents(
                messages=True, guilds=True, members=True
            ),  # set gateway intents
            activity=discord.Game(  # set activity text
                name=f"v{astrobot_v} | run !help for help"
            ),
            max_messages=None,  # disable message cache to save memory
        )

        # custom astrobot attrs
        self.remindme_timers = collections.defaultdict(list)
        self.custom_emojis = None
        self.blocked_words = self.fetch_blocked_words()
        self.colors = SimpleNamespace(
            **{
                "black": 1579032,
                "red": 13186640,
                "orange": 14516534,
                "yellow": 14534754,
                "green": 7783784,
                "blue": 3897790,
                "purple": 8801474,
                "white": 14277081,
            }
        )

    @staticmethod
    def fetch_blocked_words() -> list:
        bwl = list()
        bwl_filepath = os.environ["BLOCKED_WORDS_LIST"]
        if not os.path.exists(bwl_filepath):
            open(bwl_filepath, "a").close()
            return bwl
        with open(bwl_filepath, "r") as f:
            for line in f.readlines():
                bwl.append(line.strip())
        return bwl

    def sync_blocked_words(self) -> None:
        with open(os.environ["BLOCKED_WORDS_LIST"], "w") as f:
            for word in self.blocked_words:
                f.write(f"{word}\n")


def start_client():

    # initialize bot object
    bot = Astrobot()

    # initialize all bot cogs
    init_cogs(bot)

    @bot.command(brief="Return bot version", help="Return bot version.")
    async def version(ctx):
        """Return current version bot is running."""
        text = f"Current astrobot version is '{astrobot_v}'"
        embed = discord.Embed(
            title=text,
            description="**You can view this version's changes with the '!changelog' command**",
            color=bot.colors.white,
        )
        await ctx.send(embed=embed)

    @bot.command(
        brief="Return changelog for current bot version",
        help="Return changelog for current bot version.",
    )
    async def changelog(ctx):
        """Return link to changelog for current bot version."""
        embed = discord.Embed(
            title=f"**astrobot v{astrobot_v} CHANGELOG**",
            description=f"[Click here](https://github.com/astro-devel/astrobot/blob/master/CHANGELOG.md#{astrobot_v.replace('.', '')}) to view this version's changelog.",
            color=bot.colors.white,
        )
        await ctx.send(embed=embed)

    @bot.command(
        brief="Delete all DMs from astrobot",
        help="Delete all DMs recieved from astrobot.",
    )
    async def delete_dm_history(ctx):
        """Delete all DMs from bot."""
        await ctx.author.create_dm()  # attempt to open DMChannel with user
        channel = ctx.author.dm_channel
        if channel:  # if user is able to recieve DMs
            async for message in channel.history():
                if message.author == bot.user:
                    # TODO: implement method for auto-skipping over known non-bot msgs
                    await message.delete()
                    await asyncio.sleep(1)
        else:  # if user is not able to recieve DMs
            return
        embed = discord.Embed(
            title=f"{bot.custom_emojis.success} Successfully deleted all my messages to you.",
            color=bot.colors.green,
        ).set_footer(text="NOTE: this does not affect your server warn/kick counts.")
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
                    await Reminders.send_reminder(
                        bot,
                        timer.channel_id,
                        timer.user_id,
                        timer.reminder_text,
                        secs_late=-exp,
                    )
                    continue
                reminder_timer = RemindersTimer(
                    exp,
                    Reminders.send_reminder,
                    bot,
                    timer.channel_id,
                    timer.user_id,
                    timer.reminder_text,
                    reminder_text=timer.reminder_text,
                )
                bot.remindme_timers[int(timer.user_id)].append(reminder_timer)
                _reminder_count += 1
            return _reminder_count

        emoji_guild = bot.get_guild(483461183496519698)
        bot.custom_emojis = MochjiMojis(
            warning=await emoji_guild.fetch_emoji(905755522739892274),
            error=await emoji_guild.fetch_emoji(905755493111312394),
            success=await emoji_guild.fetch_emoji(905755460446060544),
            sadge=await emoji_guild.fetch_emoji(935004762733158452),
        )

        print(f"Reinitialized {await reinit_reminders()} reminders.")
        print(
            f'Logged in as: {bot.user}, Prefix= "{bot.command_prefix}", using py-cord version: {discord.__version__}'
        )

    bot_token = os.environ["BOT_TOKEN"]
    bot.run(bot_token)
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
