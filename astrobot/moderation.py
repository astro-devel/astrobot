from operator import is_
import string
import discord
from discord import embeds
from discord import colour
from discord import message
from discord.ext import commands
from astrobot.colors import MochjiColor

class Moderation(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot: commands.Bot = bot
        self.blocked_words = [
            "cummies"
        ]

    @commands.command(brief="Warn a user", help="Warn a given user.", usage="@[user] [reason]")
    @commands.has_permissions(kick_members=True)
    async def warn(self, ctx, member : discord.Member, *, reason = None, bot_invoked=False, as_dm=True):
        if bot_invoked:
            invoker = self.bot.user
        else:
            invoker = ctx.author

        # send warn Message to user
        embed = discord.Embed(
            title=f"⚠️ Warning! ⚠️",
            description=f"Server: {ctx.guild.name}\nWarned by: {invoker}\nReason: {reason}",
            colour=MochjiColor.orange()
        )
        if bot_invoked:
            embed.set_footer(text="NOTE: This will not count against your official warnings tally.")
        try:
            await member.send(embed=embed)
        except discord.errors.Forbidden: # if user only accepts DMs from friends, warn them in server channel
            embed = discord.Embed(
                title=f"⚠️ Warning! ⚠️",
                description=f"Warned by: {invoker}\nReason: {reason}",
                colour=MochjiColor.orange()
            )
            await ctx.send(member.mention, embed=embed, delete_after=5)
            return

        # send success message in channel
        embed = discord.Embed(
            title=f"Warned {member.name}\nReason: {reason}",
            colour=MochjiColor.green()
        )
        if not bot_invoked: # no need to send a warn_success if automod
            await ctx.send(embed=embed, delete_after=5)

    @commands.command()
    @commands.has_permissions(ban_members=True)
    async def get_bans(self, ctx):
        bans = await ctx.guild.bans()
        list = ""
        counter = 1
        for ban in bans:
            list += f"{counter}. {ban.user} ({ban.reason if ban.reason else 'No reason given'})\n"
            counter += 1
        embed = discord.Embed(
            title = "Banned Users",
            description = list,
            colour = MochjiColor.black()
        )
        await ctx.send(embed=embed)


    @commands.command(brief="Ban a user", help="Ban a given user.", usage="@[user] [reason]")
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, member : discord.Member, *, reason = None):
        embed = discord.Embed(
            title=f"You have been banned from {ctx.guild.name}",
            description=f"Banned by: {ctx.author}\nBan Reason: {reason}",
            colour=MochjiColor.red()
        )
        try:
            await member.send(embed=embed)
        except discord.errors.Forbidden: # if user only accepts DMs from friends, nothing to do
            pass

        await ctx.guild.ban(user= member, reason= reason)
        text = f"Successfully banned user {member.name}#{member.discriminator}"
        embed = discord.Embed(title=text, colour=MochjiColor.green())
        await ctx.send(embed=embed)

    @commands.command(brief="Kick a user", help="Kick a given user.", usage="@[user] [reason]")
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, member : discord.Member, *, reason = None):
        embed = discord.Embed(
            title=f"You have been kicked from {ctx.guild.name}",
            description=f"Kicked by: {ctx.author}\nKick Reason: {reason}",
            colour=MochjiColor.red()
        )
        try:
            await member.send(embed=embed)
        except discord.errors.Forbidden: # if user only accepts DMs from friends, nothing to do
            pass
        
        await ctx.guild.kick(user= member, reason= reason)
        text = f"Successfully kicked user {member.name}#{member.discriminator}"
        embed = discord.Embed(title=text, colour=MochjiColor.green())
        await ctx.send(embed=embed)

    @commands.command(brief="Unban a user", help="Unban a given user.", usage="[number] | [user]#[discriminator]")
    @commands.has_permissions(ban_members=True)
    async def unban(self, ctx, *, member: int | str):
        if isinstance(member, int):
            bans = await ctx.guild.bans()
            _unban = bans[member-1].user
            await ctx.guild.unban(_unban)
            text = f"Successfully unbanned user {_unban}"
            embed = discord.Embed(title=text, colour=MochjiColor.green())
            await ctx.send(embed=embed)
        elif isinstance(member, str):
            banned_users = await ctx.guild.bans()
            member_name, member_discriminator = member.split("#")
            for ban_entry in banned_users:
                user = ban_entry.user
                if (user.name, user.discriminator) == (member_name, member_discriminator):
                    await ctx.guild.unban(user)
                    text = f"Successfully unbanned user {user}"
                    embed = discord.Embed(title=text, colour=MochjiColor.green())
                    await ctx.send(embed=embed)
        

    @commands.Cog.listener()
    async def on_message(self, message):
        # check message for blocked words
        ctx: commands.Context = await self.bot.get_context(message)
        words = list(set(message.content.split()))
        for word in words:
            word: str = word.lower()
            for char in word:
                if char not in string.ascii_letters:
                    word = word.replace(char, "")
            if word in self.blocked_words:
                await message.delete()
                await self.warn(ctx, message.author, reason=f"`{word}` is a forbidden word. Watch your language!", bot_invoked=True)