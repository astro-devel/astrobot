import discord
from discord.ext import commands
from astrobot.colors import MochjiColor

class TestCommands(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot
    
    @commands.command()
    async def say_hello(self, ctx):
        user: discord.Member = ctx.author
        await user.send("Hello, there!")