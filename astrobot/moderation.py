import time
import string
from typing import Any
import discord
from discord import colour
from discord.ext import commands
import sqlalchemy
from astrobot import (
    mute_timers,
    util
)
from astrobot.colors import MochjiColor
from astrobot.user_sys.database import session as db_session
from astrobot.user_sys.database import (
    UserMod__Obj as _DB_UserMod__Obj,
    MutedUsers__Obj as _DB_MutedUsers__Obj
)

async def unmute(user: discord.Member, guild: discord.Guild, reason=None) -> tuple[bool, Any]:
    '''Unmute a given user. Return boolean based on if action was successful or unsuccessful.'''
    try:
        for item in db_session.query(_DB_MutedUsers__Obj):
            if str(item.user_id) == str(user.id):
                await user.edit(roles=[guild.get_role(role) for role in item.roles])
                db_session.execute(
                    sqlalchemy.delete(_DB_MutedUsers__Obj).where(_DB_MutedUsers__Obj.user_id == str(user.id)).execution_options(synchronize_session="fetch")
                )
                db_session.commit()
                try:
                    await user.send(embed=discord.Embed(
                        title=f'You have been unmuted in {guild.name}',
                        description=f'Reason: {reason}',
                        colour=MochjiColor.orange()
                    ))
                except discord.errors.Forbidden: # if user only accepts DMs from friends, nothing to do
                    pass
        return (True, None)
    except Exception as err:
        return (False, err)

class Moderation(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot: commands.Bot = bot
        self.emojis = None
        self.blocked_words = [
            "cummies"
        ]

    def increment_db_count(self, member, mod_type=None):
        _query = db_session.query(_DB_UserMod__Obj)
        _user = _DB_UserMod__Obj(
            user_id = str(member.id),
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
    async def warn(self, ctx, member : discord.Member, *, reason = None, bot_invoked=False, as_dm=True):
        if bot_invoked:
            invoker = self.bot.user
        else:
            invoker = ctx.author
            self.increment_db_count(member=member, mod_type='warn') # increment count in database if not bot invoked

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
                title=f"{await self.emojis.warning()} Warning! {await self.emojis.warning()}",
                description=f"Warned by: {invoker}\nReason: {reason}",
                colour=MochjiColor.orange()
            )
            await ctx.send(member.mention, embed=embed, delete_after=10)
            return

        # send success message in channel
        embed = discord.Embed(
            title=f"{await self.emojis.success()} Warned {member.name}\nReason: {reason}",
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
            await ctx.send(embed=discord.Embed(title=f"{await self.emojis.error()} **Please use User#Discriminator format instead of mention. i.e. '!modinfo DiscordUser#1234'**", colour=MochjiColor.red()), delete_after=10)
            return

        _member_name, _member_discriminator = member.split("#")
        _member_obj = None
        async for _member in ctx.guild.fetch_members():
            if _member.name == _member_name and _member.discriminator == _member_discriminator:
                _member_obj = _member
                break
        if not _member_obj:
            await ctx.send(embed=discord.Embed(title=f"{await self.emojis.error()} **Unable to find user {member}**", colour=MochjiColor.red()), delete_after=10)
            return
        member = _member

        embed = discord.Embed(
            title=f"Moderation info for {member}"
        )
        _query = db_session.query(_DB_UserMod__Obj)
        _user = _DB_UserMod__Obj(
            user_id = str(member.id),
            warn_count = 0,
            ban_count = 0,
            kick_count = 0,
            mute_count = 0
        )
        for item in _query:
            if str(item.user_id) == str(member.id):
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
            url=f"https://cdn.discordapp.com/avatars/{member.id}/{member.avatar}" if member.avatar else None
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
        if not member.bot:
            try:
                await member.send(embed=embed)
            except discord.errors.Forbidden: # if user only accepts DMs from friends, nothing to do
                pass
        
        self.increment_db_count(member=member, mod_type='ban')

        await ctx.guild.ban(user= member, reason= reason)
        text = f"{await self.emojis.success()} **Successfully banned user {member.name}#{member.discriminator}**"
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
        if not member.bot:
            try:
                await member.send(embed=embed)
            except discord.errors.Forbidden: # if user only accepts DMs from friends, nothing to do
                pass
        
        self.increment_db_count(member=member, mod_type='kick')

        await ctx.guild.kick(user= member, reason= reason)
        text = f"{await self.emojis.success()} **Successfully kicked user {member.name}#{member.discriminator}**"
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
            text = f"{await self.emojis.success()} **Successfully unbanned user {_unban}**"
            embed = discord.Embed(title=text, colour=MochjiColor.green())
            await ctx.send(embed=embed)
        else:
            banned_users = await ctx.guild.bans()
            member_name, member_discriminator = member.split("#")
            for ban_entry in banned_users:
                user = ban_entry.user
                if (user.name, user.discriminator) == (member_name, member_discriminator):
                    await ctx.guild.unban(user)
                    text = f"{await self.emojis.success()} **Successfully unbanned user {user}**"
                    embed = discord.Embed(title=text, colour=MochjiColor.green())
                    await ctx.send(embed=embed)
    
    @commands.command()
    @commands.has_permissions(ban_members=True, manage_roles=True)
    async def mute(self, ctx, member: discord.Member, _time: str, *, reason=None):
        for item in db_session.query(_DB_MutedUsers__Obj):
            if int(item.user_id) == int(member.id):
                await ctx.send(f"**{member}** is already muted!")
                return
        _timestamp = int(time.time())
        _mute_length = util.convert_time(_time)[0]
        _unmute_time = _mute_length + _timestamp
        _roles = [role.id for role in member.roles] # collect all user roles into variable for db storage
        await member.edit(roles=[ctx.guild.get_role(915841202803326976)]) # reset user roles to just muted role
        self.increment_db_count(member, mod_type="mute")

        # add user id and user roles to db to recover after mute expires
        _db_obj = _DB_MutedUsers__Obj(
            timestamp = _timestamp,
            unmute_at = _unmute_time,
            user_id = member.id.__str__(),
            guild_id = ctx.guild.id,
            roles = _roles
        )
        db_session.add(_db_obj)
        db_session.commit()

        # attempt to send DM to muted user
        try:
            await member.send(embed=discord.Embed(
                title=f'You have been muted in {ctx.guild.name} for {_time}.',
                description=f'Reason: {reason}',
                colour=MochjiColor.orange()
            ))
        except discord.errors.Forbidden: # if user only accepts DMs from friends, nothing to do
            pass

        # create timer for unmute
        timer = util.Timer(_mute_length, unmute, member, ctx.guild, "Time has been served.")
        mute_timers[f"{member}"] = timer # add new timer to timer list

        await ctx.send(f"**{member}** has successfully been muted.")
        
        return
    
    @commands.command()
    @commands.has_permissions(ban_members=True, manage_roles=True)
    async def unmute(self, ctx, member: discord.Member, *, reason=None):
        successful, err = await unmute(member, ctx.guild, reason=reason)
        if successful:
            try:
                mute_timers[f"{member}"].cancel() # cancel timer
                mute_timers.pop(f"{member}") # remove timer from list
            except KeyError:
                await ctx.send(f"**{member}** is not muted!")
                return
            await ctx.send(f"**{member}** has successfully been unmuted.")
        else:
            await ctx.send(f"**Error**: {err}")
        return

    @commands.command()
    @commands.has_permissions(ban_members=True, manage_roles=True)
    async def get_mutes(self, ctx):
        embed = discord.Embed(
            title=f"**Active Mutes for {ctx.guild}**"
        )
        for name, time in mute_timers.items():
            embed.add_field(
                name=f"**{name}**",
                value=f"{time._timeout}s", # TODO: convert to database pull OR add timestamps to mute_timers obj, need method of determining *time_left* AND *mute_length*
                inline=True
            )
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
    
    @commands.Cog.listener()
    async def on_ready(self):
        self.emojis = self.bot.get_cog('MochjiMojis')