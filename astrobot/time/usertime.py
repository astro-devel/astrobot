import os
from datetime import datetime
from typing import Optional
import discord
from discord.ext import commands
from geopy.geocoders import GeoNames
from geopy.timezone import Timezone


class Time(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot
        self.geocoder = GeoNames(os.environ["GEONAMES_USER"])

    def get_timezone(self, query: str) -> Optional[Timezone]:
        search = self.geocoder.geocode(query)
        if not search:
            return None
        return self.geocoder.reverse_timezone((search.latitude, search.longitude))

    @commands.command()
    async def time(self, ctx, *, query: str):
        q = self.get_timezone(query)
        if not q:
            return
        t = datetime.now(tz=q.pytz_timezone)
        embed = discord.Embed(
            title=f"Current Time for '{query}' is: {t.strftime('%H:%M')}.",
            color=self.bot.colors.green,
        )
        await ctx.send(embed=embed)
        return
