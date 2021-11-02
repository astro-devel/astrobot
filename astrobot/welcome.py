import discord
from discord.ext import commands
from astrobot.colors import MochjiColor

class WelcomeWagon(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot: commands.Bot = bot
        self.welcome_channel = 904815153177063514
    
    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        title = f"Welcome to {member.guild}!"
        description = f"\
Visit GUIDELINES_CHANNEL_ID to view the server rules.\n\
Then, check out ROLES_CHANNEL_ID to get yourself some fresh roles.\n\
Finally, head on over to GENERAL_CHANNEL_ID and join in the conversation!"
        embed = discord.Embed(
            title=title,
            description=description,
            color=MochjiColor.blue()
        )
        await member.send(embed=embed)