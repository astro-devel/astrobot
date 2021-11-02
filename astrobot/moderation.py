from operator import is_
import string
import discord
from discord import embeds
from discord import colour
from discord.ext import commands
from astrobot.colors import MochjiColor

class Moderation(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot: commands.Bot = bot
        self.blocked_words = [
            "cummies"
        ]

    @commands.command(brief="Warn a user", help="Warn a given user.", usage="@[user] [reason]")
    @commands.has_permissions()
    async def warn(self, ctx, member : discord.Member, *, reason = None, is_bot_invoked=False):
        if is_bot_invoked:
            invoker = self.bot.user
        else:
            invoker = ctx.author
        embed = discord.Embed(
            title=f"⚠️ Warning! ⚠️",
            description=f"Server: {ctx.guild.name}\nWarned by: {invoker}\nReason: {reason}",
            colour=MochjiColor.red()
        )
        if is_bot_invoked:
            embed.set_footer(text="NOTE: This will not count against your official warnings tally.")
        await member.send(embed=embed)

    @commands.command(brief="Ban a user", help="Ban a given user.", usage="@[user] [reason]")
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, member : discord.Member, *, reason = None):
        embed = discord.Embed(
            title=f"You have been banned from {ctx.guild.name}",
            description=f"Banned by: {ctx.author}\nBan Reason: {reason}",
            colour=MochjiColor.red()
        )
        await member.send(embed=embed)

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
        await member.send(embed=embed)
        
        await ctx.guild.kick(user= member, reason= reason)
        text = f"Successfully kicked user {member.name}#{member.discriminator}"
        embed = discord.Embed(title=text, colour=MochjiColor.green())
        await ctx.send(embed=embed)

    @commands.command(brief="Unban a user", help="Unban a given user.", usage="[user]#[discriminator]")
    @commands.has_permissions(ban_members=True)
    async def unban(self, ctx, *, member):
        # BUG: does not send message after successful unban
        banned_users = await ctx.guild.bans()
        member_name, member_discriminator = member.split("#")
        for ban_entry in banned_users:
            user = ban_entry.user
            if (user.name, user.discriminator) == (member_name, member_discriminator):
                await ctx.guild.unban(user)
                text = f"Successfully unbanned user {member.name}#{member.discriminator}"
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
                await self.warn(ctx, message.author, reason=f"`{word}` is a forbidden word. Watch your language!", is_bot_invoked=True)