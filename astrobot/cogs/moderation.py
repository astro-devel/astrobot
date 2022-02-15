import time
import datetime
import string
import discord
import sqlalchemy as sql
from discord.ext import commands
from astrobot import util
from astrobot.checks import invoker_is_lower_rank
from astrobot.user_sys import database as db


class Moderation(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot: commands.Bot = bot

    def increment_db_count(self, member, guild_id, mod_type=None) -> None:
        _query = db.session.query(db.GuildUser__Obj)
        modinfo = None
        for item in _query:
            if str(item.user_id) == str(member.id) and str(item.guild_id) == str(
                guild_id
            ):
                modinfo = item.moderation_info
                break

        if modinfo:
            modinfo[mod_type] += 1
            db.session.execute(
                sql.update(db.GuildUser__Obj)
                .where(
                    (
                        sql.and_(
                            db.GuildUser__Obj.user_id == member.id,
                            db.GuildUser__Obj.guild_id == guild_id,
                        )
                    )
                )
                .values(moderation_info=modinfo)
                .execution_options(synchronize_session="fetch")
            )
        else:
            userobj = db.GuildUser__Obj.blank_obj(member.id, guild_id)
            userobj.moderation_info[mod_type] += 1
            db.session.add(userobj)

        db.session.commit()
        return

    @commands.command(
        brief="Warn a user", help="Warn a given user.", usage="@[user] [reason]"
    )
    @commands.has_permissions(kick_members=True)
    @commands.check(invoker_is_lower_rank)
    async def warn(
        self, ctx, member: discord.Member, *, reason=None, bot_invoked=False
    ):
        if bot_invoked:
            invoker = self.bot.user
        else:
            invoker = ctx.author
            self.increment_db_count(
                member=member, guild_id=ctx.guild.id, mod_type="warn"
            )  # increment count in database if not bot invoked

        # send warn Message to user
        embed = discord.Embed(
            title=f"{self.bot.custom_emojis.warning} Warning! {self.bot.custom_emojis.warning}",
            description=f"Server: {ctx.guild.name}\nWarned by: {invoker}\nReason: {reason}",
            colour=self.bot.colors.orange,
        )
        if bot_invoked:
            embed.set_footer(
                text="NOTE: This will not count against your official warnings tally."
            )
        try:
            await member.send(embed=embed)
        except discord.Forbidden:  # if user only accepts DMs from friends, warn them in server channel
            embed = discord.Embed(
                title=f"{self.bot.custom_emojis.warning} Warning! {self.bot.custom_emojis.warning}",
                description=f"Warned by: {invoker}\nReason: {reason}",
                colour=self.bot.colors.orange,
            )
            await ctx.send(member.mention, embed=embed, delete_after=10)
            return

        # send success message in channel
        embed = discord.Embed(
            title=f"{self.bot.custom_emojis.success} Warned {member.name}\nReason: {reason}",
            colour=self.bot.colors.green,
        )
        if not bot_invoked:  # no need to send a warn_success if automod
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
            title="Banned Users", description=list, colour=self.bot.colors.black
        )
        await ctx.send(embed=embed)

    @commands.command()
    @commands.has_permissions(kick_members=True, ban_members=True)
    async def modinfo(self, ctx, *, member: str):
        # TODO: implement just name search and if multiple, show list of options (with nick if applicable)
        if member[0:3] == "<@!":
            await ctx.send(
                embed=discord.Embed(
                    title=f"{self.bot.custom_emojis.error} **Please use User#Discriminator format instead of mention. i.e. '!modinfo DiscordUser#1234'**",
                    colour=self.bot.colors.red,
                ),
                delete_after=10,
            )
            return

        _member_name, _member_discriminator = member.split("#")
        _member_obj = None
        async for _member in ctx.guild.fetch_members():
            if (
                _member.name == _member_name
                and _member.discriminator == _member_discriminator
            ):
                _member_obj = _member
                break
        if not _member_obj:
            await ctx.send(
                embed=discord.Embed(
                    title=f"{self.bot.custom_emojis.error} **Unable to find user {member}, are they in the server?**",
                    colour=self.bot.colors.red,
                ),
                delete_after=10,
            )
            return
        member = _member

        embed = discord.Embed(title=f"Moderation info for {member}")
        _query = db.session.query(db.GuildUser__Obj)
        _user = db.GuildUser__Obj.blank_obj(member.id, ctx.guild.id)
        for item in _query:
            if str(item.user_id) == str(member.id) and str(item.guild_id) == str(
                ctx.guild.id
            ):
                _user = item
                break

        embed.add_field(
            name="**Warns**", value=_user.moderation_info["warn"]
        ).add_field(name="**Bans**", value=_user.moderation_info["ban"]).add_field(
            name="**Kicks**", value=_user.moderation_info["kick"]
        ).add_field(
            name="**Mutes**", value=_user.moderation_info["mute"]
        ).set_thumbnail(
            url=member.avatar.__str__() if member.avatar else None
        )

        await ctx.send(embed=embed)

    @commands.command(
        brief="Ban a user", help="Ban a given user.", usage="@[user] [reason]"
    )
    @commands.has_permissions(ban_members=True)
    @commands.check(invoker_is_lower_rank)
    async def ban(self, ctx, member: discord.Member, *, reason=None):

        try:
            await ctx.guild.ban(user=member, reason=reason)
        except discord.Forbidden:
            await ctx.send(
                embed=discord.Embed(
                    title=f"{self.bot.custom_emojis.error} **Unable to ban {member.name}#{member.discriminator}, try manually.**"
                )
            )
            return

        embed = discord.Embed(
            title=f"You have been banned from {ctx.guild.name}",
            description=f"Banned by: {ctx.author}\nBan Reason: {reason}",
            colour=self.bot.colors.red,
        )
        if not member.bot:
            try:
                await member.send(embed=embed)
            except discord.Forbidden:  # if user only accepts DMs from friends, nothing to do
                pass

        self.increment_db_count(member=member, guild_id=ctx.guild.id, mod_type="ban")

        text = f"{self.bot.custom_emojis.success} **Successfully banned user {member.name}#{member.discriminator}**"
        embed = discord.Embed(title=text, colour=self.bot.colors.green)
        await ctx.send(embed=embed)

    @commands.command(
        brief="Kick a user", help="Kick a given user.", usage="@[user] [reason]"
    )
    @commands.has_permissions(kick_members=True)
    @commands.check(invoker_is_lower_rank)
    async def kick(self, ctx, member: discord.Member, *, reason=None):

        try:
            await ctx.guild.kick(user=member, reason=reason)
        except discord.Forbidden:
            await ctx.send(
                embed=discord.Embed(
                    title=f"{self.bot.custom_emojis.error} **Unable to kick {member.name}#{member.discriminator}, try manually.**"
                )
            )
            return

        embed = discord.Embed(
            title=f"You have been kicked from {ctx.guild.name}",
            description=f"Kicked by: {ctx.author}\nKick Reason: {reason}",
            colour=self.bot.colors.red,
        )
        if not member.bot:
            try:
                await member.send(embed=embed)
            except discord.Forbidden:  # if user only accepts DMs from friends, nothing to do
                pass

        self.increment_db_count(member=member, guild_id=ctx.guild.id, mod_type="kick")

        text = f"{self.bot.custom_emojis.success} **Successfully kicked user {member.name}#{member.discriminator}**"
        embed = discord.Embed(description=text, colour=self.bot.colors.green)
        await ctx.send(embed=embed)

    def is_int_convertable(self, item):
        try:
            int(item)
            return True
        except ValueError:
            return False

    @commands.command(
        brief="Unban a user",
        help="Unban a given user.",
        usage="[number] | [user]#[discriminator]",
    )
    @commands.has_permissions(ban_members=True)
    async def unban(self, ctx, *, member):
        if self.is_int_convertable(member):
            member = int(member)
            bans = await ctx.guild.bans()
            _unban = bans[member - 1].user
            await ctx.guild.unban(_unban)
            text = f"{self.bot.custom_emojis.success} **Successfully unbanned user {_unban}**"
            embed = discord.Embed(title=text, colour=self.bot.colors.green)
            await ctx.send(embed=embed)
        else:
            banned_users = await ctx.guild.bans()
            member_name, member_discriminator = member.split("#")
            for ban_entry in banned_users:
                user = ban_entry.user
                if (user.name, user.discriminator) == (
                    member_name,
                    member_discriminator,
                ):
                    await ctx.guild.unban(user)
                    text = f"{self.bot.custom_emojis.success} **Successfully unbanned user {user}**"
                    embed = discord.Embed(title=text, colour=self.bot.colors.green)
                    await ctx.send(embed=embed)

    @commands.command()
    @commands.has_permissions(moderate_members=True)
    @commands.check(invoker_is_lower_rank)
    async def ismuted(self, ctx, member: discord.Member):
        if (
            member.communication_disabled_until
            and member.communication_disabled_until < discord.utils.utcnow()
        ):
            await member.edit(communication_disabled_until=None)

        embed = discord.Embed(title=f"Mute status for {member}:")
        embed.add_field(
            name="Status:",
            value="Muted" if member.communication_disabled_until else "Not Muted",
        )
        if member.communication_disabled_until:
            embed.add_field(
                name="Expires at:",
                value=f"<t:{int(member.communication_disabled_until.timestamp())}:F>",
            )
        await ctx.send(embed=embed)

    @commands.command()
    @commands.has_permissions(moderate_members=True)
    @commands.check(invoker_is_lower_rank)
    async def mute(self, ctx, member: discord.Member, _time: str, *, reason=None):
        if (
            member.communication_disabled_until
            and member.communication_disabled_until < discord.utils.utcnow()
        ):
            await member.edit(communication_disabled_until=None)

        if member.communication_disabled_until:  # if user is already timed out, return
            await ctx.send(
                embed=discord.Embed(
                    title=f"{self.bot.custom_emojis.error} **{member}** is already muted! Expires <t:{int(member.communication_disabled_until.timestamp())}:R>",
                    colour=self.bot.colors.red,
                )
            )
            return

        _timestamp = int(time.time())
        _mute_length = util.convert_time(_time)[0]
        _unmute_time = _mute_length + _timestamp
        iso_timestamp = datetime.datetime.fromtimestamp(
            _unmute_time, tz=datetime.timezone.utc
        )
        self.increment_db_count(member, guild_id=ctx.guild.id, mod_type="mute")

        await member.timeout(until=iso_timestamp, reason=reason)

        # attempt to send DM to muted user
        try:
            await member.send(
                embed=discord.Embed(
                    title=f"{self.bot.custom_emojis.warning} You have been muted in {ctx.guild.name} for {_time}.",
                    description=f"Reason: {reason}",
                    colour=self.bot.colors.orange,
                )
            )
        except discord.Forbidden:  # if user only accepts DMs from friends, nothing to do
            pass

        await ctx.send(
            embed=discord.Embed(
                title=f"{self.bot.custom_emojis.success} **{member}** has successfully been muted.",
                colour=self.bot.colors.green,
            )
        )

        return

    @commands.command()
    @commands.has_permissions(moderate_members=True)
    @commands.check(invoker_is_lower_rank)
    async def unmute(self, ctx, member: discord.Member, *, reason=None):
        if not member.communication_disabled_until:
            embed = discord.Embed(
                title=f"{self.bot.custom_emojis.error} **{member}** is not muted!",
                colour=self.bot.colors.red,
            )
            await ctx.send(embed=embed)
            return

        await member.remove_timeout(reason=reason)
        try:
            await member.send(
                embed=discord.Embed(
                    title=f"You have been unmuted in {ctx.guild.name}",
                    description=f"Reason: {reason}",
                    colour=self.bot.colors.green,
                )
            )
        except discord.Forbidden:  # if user only accepts DMs from friends, nothing to do
            pass
        await ctx.send(
            embed=discord.Embed(
                title=f"{self.bot.custom_emojis.success} **{member}** has successfully been unmuted.",
                colour=self.bot.colors.green,
            )
        )
        return

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def blockword(self, ctx, word: str):
        self.bot.blocked_words.append(word.lower())
        self.bot.sync_blocked_words()
        await ctx.send(
            embed=discord.Embed(
                title=f"{self.bot.custom_emojis.success} Added word '{word.lower()}' to blocked words list.",
                color=self.bot.colors.green,
            )
        )

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def unblockword(self, ctx, word: str):
        if word.lower() not in self.bot.blocked_words:
            await ctx.send(
                embed=discord.Embed(
                    title=f"{self.bot.custom_emojis.error} '{word.lower()}' is not currently a blocked word.",
                    color=self.bot.colors.red,
                )
            )
            return
        self.bot.blocked_words.remove(word.lower())
        self.bot.sync_blocked_words()
        await ctx.send(
            embed=discord.Embed(
                title=f"{self.bot.custom_emojis.success} Removed word '{word.lower()}' from blocked words list.",
                color=self.bot.colors.green,
            )
        )

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def blockedwords(self, ctx):
        if not self.bot.blocked_words:
            await ctx.send("There are currently no blocked words.")
            return
        await ctx.send(
            "```\n\
{0}```".format(
                "\n".join(self.bot.blocked_words)
            )
        )

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
                await self.warn(
                    ctx,
                    message.author,
                    reason=f"`{word}` is a forbidden word. Watch your language!",
                    bot_invoked=True,
                )
