import discord
from discord.ext import commands
from astrobot.colors import MochjiColor

class WelcomeWagon(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot: commands.Bot = bot
        self.welcome_channel = 904815153177063514
    
    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        channel: discord.TextChannel = self.bot.get_channel(self.welcome_channel)
        text = f"Wellcum to the {channel.guild} server!"
        embed = discord.Embed(
            title=text,
            color=MochjiColor.blue()
        )
        await channel.send(member.mention)
        await channel.send(embed=embed)