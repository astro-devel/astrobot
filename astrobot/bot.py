import os
import time
import logging
import discord
from discord.ext import commands
from astrobot.management import Management
from astrobot.moderation import Moderation
from astrobot.welcome import WelcomeWagon
from astrobot.roles import Roles

# TODO:
#
# Guide: 
#   [-] -> In Progress
#   [x] -> Completed
#
# [ ] get DMs working  
# [-] moderation commands
    #   [x] ban
    #   [x] slowmode
    #   [x] unban
    #   [x] kick
    #   [ ] mute
    #   [x] blocked word list
# [-] reaction roles
# [ ] UserInfo command (will translate discord.Member object into UserInfo embed)
# [ ] !time command for users current timezone
# [ ] user system in database
    #   [ ] Moderation
        #   [ ] number of mutes
        #   [ ] number of kicks
        #   [ ] number of warnings
    #   [ ] Community
        #   [ ] XP
        #   [ ] Club
# [-] embed
    #   [ ] reimplement every message as embed
    #   [x] embed on fail (red)
    #   [x] embed on success (green)
# [ ] Community Features:
    #   [ ] XP system (see https://discord.com/moderation/360058645954-323:-Usage-of-XP-Systems)
    #   [ ] Clubs

class MochjiActivity(discord.Activity):
    def __init__(self):
        super().__init__()
        self.name = "playin wit ma willy"

def start_client():
    if not os.environ.get("OBAMA_BOT"):
        prefix = '!'
    else:
        prefix = '.'
    bot = commands.Bot(command_prefix=prefix,
                    intents=discord.Intents.all(),
                    activity=MochjiActivity())
    bot.add_cog(Moderation(bot))
    bot.add_cog(Roles(bot))
    bot.add_cog(Management(bot))
    bot.add_cog(WelcomeWagon(bot))

    '''
    log_time = int(time.time())
    logger = logging.getLogger('discord')
    logger.setLevel(logging.DEBUG)
    handler = logging.FileHandler(filename=f'logs/{log_time}.log', encoding='utf-8', mode='w')
    handler.setFormatter(logging.Formatter('[%(asctime)s][ %(levelname)s ] %(name)s: %(message)s'))
    logger.addHandler(handler)
    '''

    @bot.event
    async def on_ready():
        print(f'Logged in as: {bot.user}, Prefix= "{prefix}"')

    bot.run(os.environ["BOT_TOKEN"])


