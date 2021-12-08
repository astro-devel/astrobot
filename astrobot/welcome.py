import discord
from discord.ext import commands
from astrobot.colors import MochjiColor

class WelcomeWagon(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot: commands.Bot = bot
        self.welcome_channel = 904815153177063514
        self.channels = [None, None, None]
    
    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        title = f"Welcome to {member.guild}!"
        description = f"\
Visit {self.channels[0].mention} to view the server rules.\n\
Then, check out {self.channels[1].mention} to get yourself some fresh roles.\n\
Finally, head on over to {self.channels[2].mention} and join in the conversation!"
        embed = discord.Embed(
            title=title,
            description=description,
            color=MochjiColor.blue()
        )
        await member.send(embed=embed)
    
    @commands.Cog.listener()
    async def on_ready(self):
        return
        # BUG: returns 403: Missing Access
        self.channels.append(await self.bot.fetch_channel(900194414868181035)) # mochji GUIDELINES
        self.channels.append(await self.bot.fetch_channel(900218443129839637)) # mochji ROLES
        self.channels.append(await self.bot.fetch_channel(900226421513945148)) # mochji GENERAL