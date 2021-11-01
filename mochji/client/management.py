import discord
from discord import colour
from discord.ext import commands
from mochji.colors import MochjiColor

class Management(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot
    
    @commands.command(brief="Get slowmode status for current channel.", help="Get slowmode status for current channel.")
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

    @commands.command(brief="Set slowmode in current channel.", help="Set slowmode in current channel.", usage="[SEC]s | [MIN]m | [HOUR]h | off")
    @commands.has_permissions(manage_channels=True)
    async def slowmode(self, ctx, time: str):
        match time[-1]:
            case 's':
                seconds = time[:-1]
                try:
                    seconds = int(seconds)
                except ValueError:
                    text = f"Unknown argument: '{time}', see '!help slowmode'"
                    embed = discord.Embed(title=text, colour=MochjiColor.red())
                    await ctx.send(embed=embed)
                    return
                await ctx.channel.edit(slowmode_delay=seconds)
                text = f"Set the slowmode delay in this channel to {seconds} seconds."
                embed = discord.Embed(title=text, colour=MochjiColor.green())
                await ctx.send(embed=embed)
            case 'm':
                minutes = time[:-1]
                try:
                    seconds = int(minutes) * 60
                except ValueError:
                    text = f"Unknown argument: '{time}', see '!help slowmode'"
                    embed = discord.Embed(title=text, colour=MochjiColor.red())
                    await ctx.send(embed=embed)
                    return
                await ctx.channel.edit(slowmode_delay=seconds)
                text = f"Set the slowmode delay in this channel to {minutes} minute(s)."
                embed = discord.Embed(title=text, colour=MochjiColor.green())
                await ctx.send(embed=embed)
            case 'h':
                hours = time[:-1]
                try:
                    seconds = int(hours) * 60 * 60
                except ValueError:
                    text = f"Unknown argument: '{time}', see '!help slowmode'"
                    embed = discord.Embed(title=text, colour=MochjiColor.red())
                    await ctx.send(embed=embed)
                    return
                await ctx.channel.edit(slowmode_delay=seconds)
                text = f"Set the slowmode delay in this channel to {hours} hour(s)."
                embed = discord.Embed(title=text, colour=MochjiColor.green())
                await ctx.send(embed=embed)
            case _:
                if time == "off":
                    await ctx.channel.edit(slowmode_delay=0)
                    text = "Removed slowmode delay from this channel."
                    embed = discord.Embed(title=text, colour=MochjiColor.green())
                    await ctx.send(embed=embed)
                else:
                    text = f"Unknown argument '{time}', see '!help slowmode'"
                    embed = discord.Embed(title=text, colour=MochjiColor.red())
                    await ctx.send(embed=embed)

    @commands.command()
    @commands.has_permissions(manage_messages=True)
    async def delete(self, ctx, number: str):
        # TODO: add method to delete messages only from specific user
        if number == "max":
            number = 100
        else:
            try:
                number = int(number)
            except ValueError:
                text = "Please specify the number of messages to delete, i.e. '!delete 5'"
                embed = discord.Embed(title=text, colour=MochjiColor.red())
                await ctx.send(embed=embed)
                return

        if number > 100:
            text = "Sorry, the max number of messages is 100"
            embed = discord.Embed(title=text, colour=MochjiColor.red())
            await ctx.send(embed=embed)
        else:
            await ctx.channel.purge(limit=number+1)
    
    @delete.error
    @slowmode.error
    async def perms_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            # TODO: implement "else" catcher for if error is of different exception type
            text = f"Sorry, you do not have permission to do that!"
            embed = discord.Embed(title=text, colour=MochjiColor.red())
            await ctx.send(ctx.author.mention, embed=embed)