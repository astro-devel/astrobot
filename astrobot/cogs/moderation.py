import time
import datetime
import string
import discord
from discord.ext import commands
from astrobot import (
    util
)
from astrobot.checks import invoker_is_lower_rank
from astrobot import colors
from astrobot.colors import MochjiColor
from astrobot.user_sys.database import session as db_session
from astrobot.user_sys.database import (
    UserMod__Obj as _DB_UserMod__Obj
)

class Moderation(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot: commands.Bot = bot

    def increment_db_count(self, member, guild_id, mod_type=None) -> None:
        _query = db_session.query(_DB_UserMod__Obj)
        _user = _DB_UserMod__Obj(
            user_id = str(member.id),
            guild_id = str(guild_id),
            warn_count = 0,
            ban_count = 0,
            kick_count = 0,
            mute_count = 0
        )
        for item in _query:
            if str(item.user_id) == str(member.id):
                _user = item
                db_session.delete(item)
                break

        if mod_type == 'warn': _user.warn_count += 1
        elif mod_type == 'ban': _user.ban_count += 1
        elif mod_type == 'kick': _user.kick_count += 1
        elif mod_type == 'mute': _user.mute_count += 1

        db_session.add(_user)
        db_session.commit()

    @commands.command(brief="Warn a user", help="Warn a given user.", usage="@[user] [reason]")
    @commands.has_permissions(kick_members=True)
    @commands.check(invoker_is_lower_rank)
    async def warn(self, ctx, member : discord.Member, *, reason = None, bot_invoked=False):
        if bot_invoked:
            invoker = self.bot.user
        else:
            invoker = ctx.author
            self.increment_db_count(member=member, guild_id=ctx.guild.id, mod_type='warn') # increment count in database if not bot invoked

        # send warn Message to user
        embed = discord.Embed(
            title=f"{self.bot.custom_emojis.warning} Warning! {self.bot.custom_emojis.warning}",
            description=f"Server: {ctx.guild.name}\nWarned by: {invoker}\nReason: {reason}",
            colour=MochjiColor.orange()
        )
        if bot_invoked:
            embed.set_footer(text="NOTE: This will not count against your official warnings tally.")
        try:
            await member.send(embed=embed)
        except discord.Forbidden: # if user only accepts DMs from friends, warn them in server channel
            embed = discord.Embed(
                title=f"{self.bot.custom_emojis.warning} Warning! {self.bot.custom_emojis.warning}",
                description=f"Warned by: {invoker}\nReason: {reason}",
                colour=MochjiColor.orange()
            )
            await ctx.send(member.mention, embed=embed, delete_after=10)
            return

        # send success message in channel
        embed = discord.Embed(
            title=f"{self.bot.custom_emojis.success} Warned {member.name}\nReason: {reason}",
            colour=MochjiColor.green()
        )
        if not bot_invoked: # no need to send a warn_success if automod
            await ctx.send(embed=embed, delete_after=10)

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

    @commands.command()
    @commands.has_permissions(kick_members=True, ban_members=True)
    async def modinfo(self, ctx, *, member: str):
        # TODO: implement just name search and if multiple, show list of options (with nick if applicable)
        if member[0:3] == "<@!":
            await ctx.send(embed=discord.Embed(title=f"{self.bot.custom_emojis.error} **Please use User#Discriminator format instead of mention. i.e. '!modinfo DiscordUser#1234'**", colour=MochjiColor.red()), delete_after=10)
            return

        _member_name, _member_discriminator = member.split("#")
        _member_obj = None
        async for _member in ctx.guild.fetch_members():
            if _member.name == _member_name and _member.discriminator == _member_discriminator:
                _member_obj = _member
                break
        if not _member_obj:
            await ctx.send(embed=discord.Embed(title=f"{self.bot.custom_emojis.error} **Unable to find user {member}, are they in the server?**", colour=MochjiColor.red()), delete_after=10)
            return
        member = _member

        embed = discord.Embed(
            title=f"Moderation info for {member}"
        )
        _query = db_session.query(_DB_UserMod__Obj)
        _user = _DB_UserMod__Obj(
            user_id = str(member.id),
            guild_id = str(ctx.guild.id),
            warn_count = 0,
            ban_count = 0,
            kick_count = 0,
            mute_count = 0
        )
        for item in _query:
            if str(item.user_id) == str(member.id) and str(item.guild_id) == str(ctx.guild.id):
                _user = item
                break

        embed.add_field(
            name="**Warns**",
            value=_user.warn_count
        ).add_field(
            name="**Bans**",
            value=_user.ban_count
        ).add_field(
            name="**Kicks**",
            value=_user.kick_count
        ).add_field(
            name="**Mutes**",
            value=_user.mute_count
        ).set_thumbnail(
            url=member.avatar.__str__() if member.avatar else None
        )

        await ctx.send(embed=embed)

    @commands.command(brief="Ban a user", help="Ban a given user.", usage="@[user] [reason]")
    @commands.has_permissions(ban_members=True)
    @commands.check(invoker_is_lower_rank)
    async def ban(self, ctx, member : discord.Member, *, reason = None):

        try:
            await ctx.guild.ban(user= member, reason= reason)
        except discord.Forbidden:
            await ctx.send(embed=discord.Embed(
                title = f"{self.bot.custom_emojis.error} **Unable to ban {member.name}#{member.discriminator}, try manually.**"
            ))
            return

        embed = discord.Embed(
            title=f"You have been banned from {ctx.guild.name}",
            description=f"Banned by: {ctx.author}\nBan Reason: {reason}",
            colour=MochjiColor.red()
        )
        if not member.bot:
            try:
                await member.send(embed=embed)
            except discord.Forbidden: # if user only accepts DMs from friends, nothing to do
                pass
        
        self.increment_db_count(member=member, guild_id=ctx.guild.id, mod_type='ban')

        text = f"{self.bot.custom_emojis.success} **Successfully banned user {member.name}#{member.discriminator}**"
        embed = discord.Embed(title=text, colour=MochjiColor.green())
        await ctx.send(embed=embed)

    @commands.command(brief="Kick a user", help="Kick a given user.", usage="@[user] [reason]")
    @commands.has_permissions(kick_members=True)
    @commands.check(invoker_is_lower_rank)
    async def kick(self, ctx, member : discord.Member, *, reason = None):

        try:
            await ctx.guild.kick(user= member, reason= reason)
        except discord.Forbidden:
            await ctx.send(embed=discord.Embed(
                title = f"{self.bot.custom_emojis.error} **Unable to kick {member.name}#{member.discriminator}, try manually.**"
            ))
            return

        embed = discord.Embed(
            title=f"You have been kicked from {ctx.guild.name}",
            description=f"Kicked by: {ctx.author}\nKick Reason: {reason}",
            colour=MochjiColor.red()
        )
        if not member.bot:
            try:
                await member.send(embed=embed)
            except discord.Forbidden: # if user only accepts DMs from friends, nothing to do
                pass
        
        self.increment_db_count(member=member, guild_id=ctx.guild.id, mod_type='kick')

        text = f"{self.bot.custom_emojis.success} **Successfully kicked user {member.name}#{member.discriminator}**"
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
            text = f"{self.bot.custom_emojis.success} **Successfully unbanned user {_unban}**"
            embed = discord.Embed(title=text, colour=MochjiColor.green())
            await ctx.send(embed=embed)
        else:
            banned_users = await ctx.guild.bans()
            member_name, member_discriminator = member.split("#")
            for ban_entry in banned_users:
                user = ban_entry.user
                if (user.name, user.discriminator) == (member_name, member_discriminator):
                    await ctx.guild.unban(user)
                    text = f"{self.bot.custom_emojis.success} **Successfully unbanned user {user}**"
                    embed = discord.Embed(title=text, colour=MochjiColor.green())
                    await ctx.send(embed=embed)
    
    @commands.command()
    @commands.has_permissions(moderate_members=True)
    @commands.check(invoker_is_lower_rank)
    async def ismuted(self, ctx, member: discord.Member):
        # TODO: update to use string rep of member instead of Member obj
        # TODO: re-implement database entries for mutes
        embed = discord.Embed(title=f"Mute status for {member}:")
        embed.add_field(
            name="Status:",
            value="Muted" if member.communication_disabled_until else "Not Muted"
        )
        if member.communication_disabled_until:
            embed.add_field(
                name="Reason:",
                value="NI"
            ).add_field(
                name="Expires in:",
                value=util.time_between(discord.utils.utcnow(), member.communication_disabled_until)
            ).add_field(
                name="Muted by:",
                value="NI"
            )
        await ctx.send(embed=embed)

    @commands.command()
    @commands.has_permissions(moderate_members=True)
    @commands.check(invoker_is_lower_rank)
    async def mute(self, ctx, member: discord.Member, _time: str, *, reason=None):
        if member.communication_disabled_until: # if user is already timed out, return
            time_left = util.time_between(discord.utils.utcnow(), member.communication_disabled_until)
            await ctx.send(embed=discord.Embed(
                title=f"{self.bot.custom_emojis.error} **{member}** is already muted! Expires in {time_left}",
                colour=MochjiColor.red()
            ))
            return

        _timestamp = int(time.time())
        _mute_length = util.convert_time(_time)[0]
        _unmute_time = _mute_length + _timestamp
        iso_timestamp = datetime.datetime.fromtimestamp(_unmute_time, tz=datetime.timezone.utc)
        self.increment_db_count(member, guild_id=ctx.guild.id, mod_type="mute")

        await member.timeout(until=iso_timestamp, reason=reason)

        # attempt to send DM to muted user
        try:
            await member.send(embed=discord.Embed(
                title=f'{self.bot.custom_emojis.warning} You have been muted in {ctx.guild.name} for {_time}.',
                description=f'Reason: {reason}',
                colour=MochjiColor.orange()
            ))
        except discord.Forbidden: # if user only accepts DMs from friends, nothing to do
            pass

        await ctx.send(embed=discord.Embed(
            title=f"{self.bot.custom_emojis.success} **{member}** has successfully been muted.",
            colour=MochjiColor.green()
        ))
        
        return
    
    @commands.command()
    @commands.has_permissions(moderate_members=True)
    @commands.check(invoker_is_lower_rank)
    async def unmute(self, ctx, member: discord.Member, *, reason=None):
        if not member.communication_disabled_until:
            embed = discord.Embed(
                title=f"{self.bot.custom_emojis.error} **{member}** is not muted!",
                colour=MochjiColor.red()
            )
            await ctx.send(embed=embed)
            return
        
        await member.remove_timeout(reason=reason)
        try:
            await member.send(embed=discord.Embed(
                title=f'You have been unmuted in {ctx.guild.name}',
                description=f'Reason: {reason}',
                colour=MochjiColor.green()
            ))
        except discord.Forbidden: # if user only accepts DMs from friends, nothing to do
            pass
        await ctx.send(embed=discord.Embed(
            title=f"{self.bot.custom_emojis.success} **{member}** has successfully been unmuted.",
            colour=MochjiColor.green()
        ))
        return

    """ TODO: reimplement after database added back (see ismuted() TODO)
    @commands.command()
    @commands.has_permissions(ban_members=True, manage_roles=True)
    async def get_mutes(self, ctx):
        embed = discord.Embed(
            title=f"**Active Mutes for {ctx.guild}**"
        )
        for name, time in mute_timers.items():
            # TODO: convert to database pull (add timer info to database obj, mute() will need edit prob), need method of determining *time_left* AND *mute_length*, also need database pull to make command guild-specific
            embed.add_field(
                name=f"**{name}**",
                value=f"{time._timeout}s", 
                inline=True
            )
        await ctx.send(embed=embed)
    """
    @commands.command()
    @commands.has_permissions(administrator=True)
    async def blockword(self, ctx, word: str):
        self.bot.blocked_words.append(word.lower())
        self.bot.sync_blocked_words()
        await ctx.send(embed=discord.Embed(
            title=f"{self.bot.custom_emojis.success} Added word '{word.lower()}' to blocked words list.",
            color=colors.GREEN
        ))
    
    @commands.command()
    @commands.has_permissions(administrator=True)
    async def unblockword(self, ctx, word: str):
        if word.lower() not in self.bot.blocked_words:
            await ctx.send(embed=discord.Embed(
                title=f"{self.bot.custom_emojis.error} '{word.lower()}' is not currently a blocked word.",
                color=colors.RED
            ))
            return
        self.bot.blocked_words.remove(word.lower())
        self.bot.sync_blocked_words()
        await ctx.send(embed=discord.Embed(
            title=f"{self.bot.custom_emojis.success} Removed word '{word.lower()}' from blocked words list.",
            color=colors.GREEN
        ))
    
    @commands.command()
    @commands.has_permissions(administrator=True)
    async def blockedwords(self, ctx):
        if not self.bot.blocked_words:
            await ctx.send("There are currently no blocked words.")
            return
        await ctx.send("```\n\
{0}```".format('\n'.join(self.bot.blocked_words)))
        

    @commands.Cog.listener()
    async def on_message(self, message):
        # check message for blocked words
        ctx: commands.Context = await self.bot.get_context(message)
        words = list(set(message.content.split()))
        if "!blockword" in words or ctx.author.bot:
            return
        for word in words:
            word: str = word.lower()
            for char in word:
                if char not in string.ascii_letters:
                    word = word.replace(char, "")
            if word in self.bot.blocked_words:
                await message.delete()
                await self.warn(ctx, message.author, reason=f"`{word}` is a forbidden word. Watch your language!", bot_invoked=True)