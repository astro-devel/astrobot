import discord
from discord.ext import commands
from astrobot import colors
from astrobot.colors import MochjiColor
from astrobot import util

class Management(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot: discord.Bot = bot
        self.emojis = None
    
    @commands.command()
    async def serverinfo(self, ctx):
        bots=list()
        for user in ctx.guild.members:
            if user.bot:
                bots.append(user)
        embed = discord.Embed(
            title=f"Server stats for {ctx.guild}",
            color=colors.BLACK
        ).add_field(
            name="Members:",
            value=ctx.guild.member_count
        ).add_field(
            name="Bots:",
            value=len(bots)
        ).add_field(
            name="Server Owner:",
            value=ctx.guild.owner.mention
        ).add_field(
            name="Server Boosters:",
            value=len(ctx.guild.premium_subscribers)
        ).add_field(
            name="Server Boosts:",
            value=ctx.guild.premium_subscription_count
        ).add_field(
            name="Server Created:",
            value=ctx.guild.created_at.date()
        )
        embed.set_thumbnail(url=ctx.guild.icon.url)
        await ctx.send(embed=embed)
        return

    @commands.command(brief="Get slowmode status for current channel", help="Get slowmode status for current channel.")
    async def slowmode_status(self, ctx):
        slowmode: int = ctx.channel.slowmode_delay
        if slowmode == 0:
            text = "There is currently no active slowmode"

        elif slowmode < 60:
            text = f"Current slowmode setting is: {slowmode} seconds"

        elif 3600 > slowmode >= 60: # if slowmode is minutes
            if slowmode % 60 == 0:
                slowmode = int(slowmode / 60)
                text = f"Current slowmode setting is: {slowmode} minute(s)"
            else:
                remainder = slowmode % 60
                slowmode -= remainder
                slowmode = int(slowmode / 60)
                text = f"Current slowmode setting is: {slowmode} minute(s) {remainder} second(s)"

        elif slowmode >= 3600: # if slowmode is hours
            seconds_remainder = slowmode % 60
            if seconds_remainder: # if remainder of seconds, remove from slowmode
                slowmode -= seconds_remainder
            slowmode = int(slowmode / 60) # divide to minutes
            minutes_remainder = slowmode % 60
            if minutes_remainder:
                slowmode -= minutes_remainder
            hours = int(slowmode / 60)

            text = f"Current slowmode setting is: {hours} hour(s)"
            if minutes_remainder:
                text += f" {minutes_remainder} minute(s)"
            if seconds_remainder:
                text += f" {seconds_remainder} second(s)"

        embed = discord.Embed(title=text, colour=MochjiColor.green())
        await ctx.send(embed=embed)

    @commands.command(brief="Set slowmode in current channel", help="Set slowmode in current channel.", usage="[HOUR]h[MIN]m[SEC]s | off")
    @commands.has_permissions(manage_channels=True)
    async def slowmode(self, ctx, *, time: str):

        if time == "off":
            if not ctx.channel.slowmode_delay:
                text = f"{self.emojis.error} Channel currently not in slowmode!"
                embed = discord.Embed(title=text, colour=MochjiColor.red())
                await ctx.send(embed=embed)
                return
            await ctx.channel.edit(slowmode_delay=0)
            text = f"{self.emojis.success} Removed slowmode delay from this channel."
            embed = discord.Embed(title=text, colour=MochjiColor.green())
            await ctx.send(embed=embed)
            return
        else:
            seconds, times = util.convert_time(time)

            if not seconds:
                text = f"{self.emojis.error} Unknown argument: '{time}', see '!help slowmode'"
                embed = discord.Embed(title=text, colour=MochjiColor.red())
                await ctx.send(embed=embed)
                return

            if seconds > 21600:
                text = f"{self.emojis.error} Time must not be greater than 6 hours."
                embed = discord.Embed(title=text, colour=MochjiColor.red())
                await ctx.send(embed=embed)
                return

            await ctx.channel.edit(slowmode_delay=seconds)
            text = f"{self.emojis.success} Set the slowmode delay in this channel to {times.get('h', times.get('H')) + ' hour(s)' if times.get('h', times.get('H')) else ''} {times.get('m', times.get('M')) + ' minute(s)' if times.get('m', times.get('M')) else ''} {times.get('s', times.get('S')) + ' second(s)' if times.get('s', times.get('S')) else ''}."
            embed = discord.Embed(title=text, colour=MochjiColor.green())
            await ctx.send(embed=embed)
            return

    @commands.command(brief="Delete a given number of messages", help="Delete a given number of messages.", usage="[AMOUNT]", aliases=["del"])
    @commands.has_permissions(manage_messages=True)
    async def delete(self, ctx, number: str):
        # TODO: check in on possibility of removing specific user's messages
        if number == "max":
            number = 100
        else:
            try:
                number = int(number)
            except ValueError:
                text = f"{self.emojis.error} Please specify the number of messages to delete, i.e. '!delete 5'"
                embed = discord.Embed(title=text, colour=MochjiColor.red())
                await ctx.send(embed=embed)
                return

        if number > 100:
            text = f"{self.emojis.error} Sorry, the max number of messages is 100"
            embed = discord.Embed(title=text, colour=MochjiColor.red())
            await ctx.send(embed=embed)
        else:
            await ctx.channel.purge(limit=number+1)
    
    @commands.Cog.listener()
    async def on_ready(self):
        self.emojis = self.bot.get_cog('MochjiMojis')