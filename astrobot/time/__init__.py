import time
import datetime
import zoneinfo
import discord
from discord.ext import commands
from astrobot.colors import MochjiColor

class TimeStuffs(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot
        self.timezones = zoneinfo.available_timezones()
        self.emojis = None
    
    @commands.command()
    async def time(self, ctx, tz: str):
        assert tz in self.timezones
        t = time.gmtime()
        utc_time = datetime.datetime(t.tm_year, t.tm_mon, t.tm_mday, t.tm_hour, t.tm_min, tzinfo=datetime.timezone.utc)
        lt = utc_time.astimezone(zoneinfo.ZoneInfo(tz))
        minute = lt.minute
        if minute < 10:
            minute = f"0{minute}"
        local_time = f"{lt.hour}:{minute}"
        embed = discord.Embed(
            title = f"Time for {tz} is {local_time}",
            colour = MochjiColor.green()
        )
        await ctx.send(embed=embed)

    '''
    @commands.command()
    async def timezones(self, ctx):
        z = ""
        for zone in self.timezones:
            z += zone + '\n'
        embed = discord.Embed(
            title = "Available Timezones",
            description = z,
            colour = MochjiColor.white()
        )
        await ctx.send(embed=embed)
    '''
    @commands.Cog.listener()
    async def on_ready(self):
        self.emojis = self.bot.get_cog('MochjiMojis')