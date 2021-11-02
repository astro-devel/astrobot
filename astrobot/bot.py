import os
import time
import logging
import discord
from discord import embeds
from discord.ext import commands
from astrobot import __version__ as astrobot_v
from astrobot.colors import MochjiColor
from astrobot.management import Management
from astrobot.moderation import Moderation
from astrobot.test import TestCommands
from astrobot.welcome import WelcomeWagon
from astrobot.roles import Roles

# TODO:
#
# Guide: 
#   [-] -> In Progress
#   [x] -> Completed
#
# (FAR BACK BURNER)
    #   [ ] last.fm integration
    #   [ ] spotify integration
        #   [ ] spud integration ??????
# [x] get DMs working  
# [-] moderation commands
        #   [ ] Consolidate error catchers into one file
            #   [ ] delete error message after 10 seconds
    #   [ ] implement ban/kick/warn/mute count in database
    #   [x] ban
    #   [x] slowmode
    #   [x] unban
    #   [x] kick
    #   [ ] warn
    #   [ ] mute
    #   [x] blocked word list
# [-] reaction roles
    #   [ ] implement role channel and message ID in DB
# [ ] UserInfo command (will translate discord.Member object into UserInfo embed)
# [ ] !time command for users current timezone
# [ ] user system in database
    #   [ ] Moderation
            #   (NOTE: vic wants unauth atps to say "No peeking!")
            #   "maybe if u wanna get into specifics, for example do !summary @[user] [mutes] then it lists the dates/durations/reasons"
        #   [ ] number of mutes
        #   [ ] number of kicks
        #   [ ] number of warnings
        #   [ ] user moderation summary
    #   [ ] Community features
        #   [ ] XP system (see https://discord.com/moderation/360058645954-323:-Usage-of-XP-Systems)
        #   [ ] Economy system
            #   [ ] random currency drops in random channels
                #   i.e. “Dropped [random amount] twunkles! type !grab to take them before it disappears!”
            #   [ ] certain types of currency -> different rarity levels (NOTE: talk more with v ab this during devel)
            #   [ ] Games (i.e. blackjack, russian roulette)
        #   [ ] Clubs
# [x] embed
    #   [x] reimplement every message as embed
    #   [x] embed on fail (red)
    #   [x] embed on success (green)

class MochjiActivity(discord.Activity):
    def __init__(self):
        super().__init__()
        self.name = "playin wit ma willy"

def start_client():
    if not os.environ.get("DEVEL"):
        prefix = '!'
    else:
        prefix = '.'
    bot = commands.Bot(command_prefix=prefix,
                    intents=discord.Intents.all(),
                    activity=MochjiActivity())
    if os.environ.get("DEVEL"):
        # NOTE TODO NOTE TODO NOTE TODO NOTE TODO NOTE TODO NOTE TODO NOTE TODO NOTE TODO NOTE
            # WelcomeWagon currently in devel block due to bot currently being in devel
            # MAKE FUCKING SURE TO REMOVE WelcomeWagon FROM THIS BLOCK WHEN PUSH TO PROD
        # NOTE TODO NOTE TODO NOTE TODO NOTE TODO NOTE TODO NOTE TODO NOTE TODO NOTE TODO NOTE
        bot.add_cog(WelcomeWagon(bot))
        bot.add_cog(TestCommands(bot))

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

    @bot.command()
    async def version(ctx):
        text = f"Current astrobot version is '{astrobot_v}'"
        embed = discord.Embed(
            title=text,
            color=MochjiColor.white()
        )
        await ctx.send(embed=embed)

    @bot.event
    async def on_ready():
        print(f'Logged in as: {bot.user}, Prefix= "{prefix}"')

    bot.run(os.environ["BOT_TOKEN"])


