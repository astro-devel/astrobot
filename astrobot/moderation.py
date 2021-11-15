import string
import discord
from discord import embeds
from discord import colour
from discord import message
from discord.ext import commands
from astrobot.colors import MochjiColor
from astrobot.user_sys.database import session as db_session
from astrobot.user_sys.database import UserMod__Obj as _DB_UserMod__Obj

class Moderation(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot: commands.Bot = bot
        self.emojis = None
        self.blocked_words = [
            "cummies"
        ]

    def increment_db_count(self, member, _type=None):
        _query = db_session.query(_DB_UserMod__Obj)
        _user = None
        for item in _query:
            if item.user_id == member:
                _user = item
                db_session.delete(item)

        if _type == 'warn': _user.warn_count += 1
        elif _type == 'ban': _user.ban_count += 1
        elif _type == 'kick': _user.kick_count += 1
        elif _type == 'mute': _user.mute_count += 1

        db_session.add(_user)
        db_session.commit()

    @commands.command(brief="Warn a user", help="Warn a given user.", usage="@[user] [reason]")
    @commands.has_permissions(kick_members=True)
    async def warn(self, ctx, member : discord.Member, *, reason = None, bot_invoked=False, as_dm=True):
        if bot_invoked:
            invoker = self.bot.user
        else:
            invoker = ctx.author

        # send warn Message to user
        embed = discord.Embed(
            title=f"{await self.emojis.warning()} Warning! {await self.emojis.warning()}",
            description=f"Server: {ctx.guild.name}\nWarned by: {invoker}\nReason: {reason}",
            colour=MochjiColor.orange()
        )
        if bot_invoked:
            embed.set_footer(text="NOTE: This will not count against your official warnings tally.")
        try:
            await member.send(embed=embed)
        except discord.errors.Forbidden: # if user only accepts DMs from friends, warn them in server channel
            embed = discord.Embed(
                title=f"{await self.emojis.warning()} Warning! {self.emojis.warning()}",
                description=f"Warned by: {invoker}\nReason: {reason}",
                colour=MochjiColor.orange()
            )
            await ctx.send(member.mention, embed=embed, delete_after=5)
            return

        # increment count in database
        if not bot_invoked: # bot warns don't count towards total count
            self.increment_db_count(member=member, _type='warn')

        # send success message in channel
        embed = discord.Embed(
            title=f"{await self.emojis.success()} Warned {member.name}\nReason: {reason}",
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
        
        self.increment_db_count(member=member, type='ban')

        await ctx.guild.ban(user= member, reason= reason)
        text = f"{await self.emojis.success()} Successfully banned user {member.name}#{member.discriminator}"
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
        
        self.increment_db_count(member=member, type='kick')

        await ctx.guild.kick(user= member, reason= reason)
        text = f"{await self.emojis.success()} Successfully kicked user {member.name}#{member.discriminator}"
        embed = discord.Embed(description=text, colour=MochjiColor.green())
        await ctx.send(embed=embed)

    def is_int_convertable(self, item):
        try:
            int(item)
            return True
        except ValueError:
            return False

    @commands.command(brief="Unban a user", help="Unban a given user.", usage="[number] | [user]#[discriminator]")
    @commands.has_permissions(ban_members=True)
    async def unban(self, ctx, *, member):
        if self.is_int_convertable(member):
            member = int(member)
            bans = await ctx.guild.bans()
            _unban = bans[member-1].user
            await ctx.guild.unban(_unban)
            text = f"{await self.emojis.success()} Successfully unbanned user {_unban}"
            embed = discord.Embed(title=text, colour=MochjiColor.green())
            await ctx.send(embed=embed)
        else:
            banned_users = await ctx.guild.bans()
            member_name, member_discriminator = member.split("#")
            for ban_entry in banned_users:
                user = ban_entry.user
                if (user.name, user.discriminator) == (member_name, member_discriminator):
                    await ctx.guild.unban(user)
                    text = f"{await self.emojis.success()} Successfully unbanned user {user}"
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
                await self.warn(ctx, message.author, reason=f"{self.emojis.warning()} `{word}` is a forbidden word. Watch your language!", bot_invoked=True)
    
    @commands.Cog.listener()
    async def on_ready(self):
        self.emojis = self.bot.get_cog('MochjiMojis')