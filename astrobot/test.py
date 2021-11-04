import discord
from discord.ext import commands
from astrobot.colors import MochjiColor

class TestCommands(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.guild = None
        self.emojis = None
    
    @commands.command()
    async def say_hello(self, ctx):
        user: discord.Member = ctx.author
        await user.send("Hello, there!")
    
    @commands.command()
    async def emochji(self, ctx):
        embed = discord.Embed(
            title = await self.emojis.success(),
            description = await self.emojis.warning()
        )
        await ctx.send(embed=embed)
    
    @commands.Cog.listener()
    async def on_ready(self):
        self.emojis = self.bot.get_cog('MochjiMojis')