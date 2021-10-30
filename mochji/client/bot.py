import os
import time
import fnmatch
import logging
import discord
from discord import activity
from discord.ext import commands
from mochji import util
from mochji.client.commands import MainCog
from mochji.exceptions import MochjiEnvironmentVariableNotFound

# TODO: 
# [-] moderation commands
#       [x] ban
#           - implement auth check
#       [x] unban
#           - implement auth check
#       [ ] kick
#           - implement method
#           - implement auth check
#       [ ] mute
#       [ ] blocked word list
# [ ] reaction roles
# [ ] embed
rlog = []
async def print_rlog(*args):
    rlog.append(f"[ {int(time.time())} ]: " + util.collect_to_string(args))

blocked_words = [
    "cummies"
]

class MochjiActivity(discord.Activity):
    def __init__(self):
        super().__init__()
        self.name = "playin wit ma willy"

def start_client():
    bot = commands.Bot(command_prefix='!',
                    intents=discord.Intents.all(),
                    activity=MochjiActivity())

    log_time = int(time.time())
    logger = logging.getLogger('discord')
    logger.setLevel(logging.DEBUG)
    handler = logging.FileHandler(filename=f'logs/{log_time}.log', encoding='utf-8', mode='w')
    handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
    logger.addHandler(handler)

    @bot.command()
    @commands.has_permissions(ban_members=True)
    async def ban(ctx, member : discord.Member, *, reason = None):
        await member.ban(reason = reason)
        await ctx.send(f"Successfully banned {member.mention}")
    
    @bot.command()
    @commands.has_permissions(ban_members=True)
    async def unban(ctx, *, member):
        banned_users = await ctx.guild.bans()
        member_name, member_discriminator = member.split("#")

        for ban_entry in banned_users:
            user = ban_entry.user

            if (user.name, user.discriminator) == (member_name, member_discriminator):
                await ctx.guild.unban(user)
                await ctx.send(f'Unbanned {user.mention}')
                return

    @ban.error
    @unban.error
    async def perms_error(ctx, error):
        if isinstance(error, commands.MissingPermissions):
            text = f"Sorry {ctx.author.mention}, you do not have permissions to do that!"
            await ctx.send(text)

    @bot.event
    async def on_ready():
        #await client.change_presence(activity=discord.Game("playin with my willy"))
        await print_rlog(f'Logged in as: {bot.user}')
    
    '''
    @bot.event
    async def on_message(message):
        # check message for blocked words
        words = list(set(message.content.split()))
        for word in words:
            if word in blocked_words:
                await message.delete()
                await message.channel.send("No! Bad Boy! Shut the fuck up with that shit!")
    '''


    try:
        bot.add_cog(MainCog(bot))
        bot.run(os.environ["BOT_TOKEN"])
    except KeyError:
        err = "Please define the environment variable 'BOT_TOKEN' with the bot's token. This can be found at \"https://discord.com/developers/applications/[ APPLICATION_ID ]/bot\""
        raise MochjiEnvironmentVariableNotFound(err)


