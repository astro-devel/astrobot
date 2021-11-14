import discord
from discord.ext import commands
from astrobot.colors import MochjiColor

class WelcomeWagon(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot: commands.Bot = bot
        self.welcome_channel = 904815153177063514
        self.channel_ids = [None, None, None]
    
    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        title = f"Welcome to {member.guild}!"
        description = f"\
Visit {self.channel_ids[0]} to view the server rules.\n\
Then, check out {self.channel_ids[1]} to get yourself some fresh roles.\n\
Finally, head on over to {self.channel_ids[2]} and join in the conversation!"
        embed = discord.Embed(
            title=title,
            description=description,
            color=MochjiColor.blue()
        )
        await member.send(embed=embed)
    
    @commands.Cog.listener()
    async def on_ready(self):
        return
        # BUG: throws 403 on attempted fetch
#        self.channel_ids.append(await self.bot.fetch_guild(900194414868181035)) # mochji GUIDELINES
#        self.channel_ids.append(await self.bot.fetch_guild(900218443129839637)) # mochji ROLES
#        self.channel_ids.append(await self.bot.fetch_guild(900226421513945148)) # mochji GENERAL