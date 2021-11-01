import string
import discord
from discord.ext import commands
from colors import MochjiColor

class Moderation(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot
        self.blocked_words = [
            "cummies"
        ]

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
            word: str = word.lower()
            for char in word:
                if char not in string.ascii_letters:
                    word = word.replace(char, "")
            if word in self.blocked_words:
                await message.delete()
                await message.channel.send("No! Bad Boy! Shut the fuck up with that shit!")