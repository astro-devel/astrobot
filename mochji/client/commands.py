import discord
from discord.ext import commands
from discord.ext.commands.core import command
from mochji.colors import MochjiColor

class Moderation(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot
        self.blocked_words = [
            "cummies"
        ]

    @commands.command(brief="Set slowmode in current channel.", help="Set slowmode in current channel.", usage="[time]s | [time]m | [time]h | none | remove")
    @commands.has_permissions(manage_channels=True)
    async def slowmode(self, ctx, time: str):
        match time[-1]:
            case 's':
                seconds = time[:-1]
                await ctx.channel.edit(slowmode_delay=seconds)
                await ctx.send(f"Set the slowmode delay in this channel to {seconds} seconds.")
            case 'm':
                minutes = time[:-1]
                seconds = int(minutes) * 60
                await ctx.channel.edit(slowmode_delay=seconds)
                await ctx.send(f"Set the slowmode delay in this channel to {minutes} minute(s).")
            case 'h':
                hours = time[:-1]
                seconds = int(hours) * 60 * 60
                await ctx.channel.edit(slowmode_delay=seconds)
                await ctx.send(f"Set the slowmode delay in this channel to {hours} hour(s).")
            case _:
                if time == "none" or time == "remove":
                    await ctx.channel.edit(slowmode_delay=0)
                    await ctx.send(f"Removed slowmode delay from this channel.")
                else:
                    await ctx.send("Unknown interval, try '!help slowmode'...")

    # BUG: 
    # Affects: all commands requiring DM to be sent after action
    # Overview:
    # current dm method returns 403 - Forbidden
    # (403 Forbidden (error code: 50007): Cannot send messages to this user)
    @commands.command(brief="Ban a user", help="Ban a given user.", usage="@[user] [reason]")
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, member : discord.Member, *, reason = None):
        await ctx.guild.ban(user= member, reason= reason)
        await ctx.send(f"Successfully banned user {member.mention}")
        msg = f"You have been banned from {ctx.guild.name}\nReason: {reason}"
        await member.send(msg)

    @commands.command(brief="Kick a user", help="Kick a given user.", usage="@[user] [reason]")
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, member : discord.Member, *, reason = None):
        await ctx.guild.kick(user= member, reason= reason)
        await ctx.send(f"Successfully kicked user {member.mention}")
        msg = f"You have been kicked from {ctx.guild.name}\nReason: {reason}"
        await member.send(msg)

    @commands.command(brief="Unban a user", help="Unban a given user.", usage="[user]#[discriminator]")
    @commands.has_permissions(ban_members=True)
    async def unban(self, ctx, *, member):
        banned_users = await ctx.guild.bans()
        member_name, member_discriminator = member.split("#")
        for ban_entry in banned_users:
            user = ban_entry.user
            if (user.name, user.discriminator) == (member_name, member_discriminator):
                await ctx.guild.unban(user)
                await ctx.send(f'Successfully unbanned user {user.mention}')
                msg = f"You have been unbanned from {ctx.guild.name}! Feel free to rejoin the server."
                await member.send(msg)
                return

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
            if word in self.blocked_words:
                await message.delete()
                await message.channel.send("No! Bad Boy! Shut the fuck up with that shit!")