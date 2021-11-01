import discord
from discord.ext import commands
from astrobot.colors import MochjiColor

class TimeStuffs(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot