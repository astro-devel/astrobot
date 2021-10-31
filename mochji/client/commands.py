import string
import discord
from discord.ext import commands
from mochji.colors import MochjiColor

class Moderation(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot
        self.blocked_words = [
            "cummies"
        ]

    @commands.command(brief="Get slowmode status for current channel.", help="Get slowmode status for current channel.")
    async def slowmode_status(self, ctx):
        # TODO: if possible, make this callable with just '!slowmode'
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
            # TODO: implement remainder logic
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

    # BUG 001: 
    #   Affects: 
    #       - All commands requiring DM to be sent after action
    #   Overview:
    #       - current dm method returns 403 - Forbidden
    #           - (403 Forbidden (error code: 50007): Cannot send messages to this user)
    #   Status:
    #       - DM method currently commented out while other features are being tested/implemented
    @commands.command(brief="Ban a user", help="Ban a given user.", usage="@[user] [reason]")
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, member : discord.Member, *, reason = None):
        await ctx.guild.ban(user= member, reason= reason)
        text = f"Successfully banned user {member.name}#{member.discriminator}"
        embed = discord.Embed(title=text, colour=MochjiColor.green())
        await ctx.send(embed=embed)

        # TODO: once DMs start working, change this to embed
#        msg = f"You have been banned from {ctx.guild.name}\nReason: {reason}"
#        await member.send(msg)

    @commands.command(brief="Kick a user", help="Kick a given user.", usage="@[user] [reason]")
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, member : discord.Member, *, reason = None):
        await ctx.guild.kick(user= member, reason= reason)
        text = f"Successfully kicked user {member.name}#{member.discriminator}"
        embed = discord.Embed(title=text, colour=MochjiColor.green())
        await ctx.send(embed=embed)

        # TODO: once DMs start working, change this to embed
#        msg = f"You have been kicked from {ctx.guild.name}\nReason: {reason}"
#        await member.send(msg)

    @commands.command(brief="Unban a user", help="Unban a given user.", usage="[user]#[discriminator]")
    @commands.has_permissions(ban_members=True)
    async def unban(self, ctx, *, member):
        banned_users = await ctx.guild.bans()
        member_name, member_discriminator = member.split("#")
        for ban_entry in banned_users:
            user = ban_entry.user
            if (user.name, user.discriminator) == (member_name, member_discriminator):
                await ctx.guild.unban(user)
                text = f"Successfully unbanned user {member.name}#{member.discriminator}"
                embed = discord.Embed(title=text, colour=MochjiColor.green())
                await ctx.send(embed=embed)

                # TODO: once DMs start working, change this to embed
#                msg = f"You have been unbanned from {ctx.guild.name}! Feel free to rejoin the server."
#                await member.send(msg)

    @ban.error
    @unban.error
    @kick.error
    @slowmode.error
    async def perms_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            # TODO: implement "else" catcher for if error is of different exception type
            text = f"Sorry, you do not have permission to do that!"
            embed = discord.Embed(title=text, colour=MochjiColor.red())
            await ctx.send(ctx.author.mention, embed=embed)

    @commands.Cog.listener()
    async def on_message(self, message):
        # check message for blocked words
        words = list(set(message.content.split()))
        for word in words:
            for char in word:
                if char not in string.ascii_letters:
                    word = word.replace(char, "")
            if word in self.blocked_words:
                await message.delete()
                await message.channel.send("No! Bad Boy! Shut the fuck up with that shit!")