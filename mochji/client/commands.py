import discord
from discord import client
from discord.ext import commands

class MainCog(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot

    @commands.command()
    async def balls(self, ctx):
        await ctx.send("nuts even")