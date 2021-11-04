import discord
from discord.enums import Status
from discord.ext import commands
from astrobot.colors import MochjiColor

class UserInfo(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot
    
    @commands.command()
    async def whoami(self, ctx):
        member: discord.Member | discord.ClientUser = ctx.author
        name = f"{member.name}#{member.discriminator}"
        joined_guild_at = member.joined_at.date()
        joined_discord_at = member.created_at.date()
        nickname = member.nick
        current_status = member.raw_status
        avatar = member.avatar
        user_id = member.id
        avatar_url = f"https://cdn.discordapp.com/avatars/{user_id}/{avatar}" if avatar else None
        _roles = member.roles
        roles = ""
        counter = 0

        for role in _roles:
            if counter > 10:
                break
            if counter == 0:
                counter += 1
                continue
            roles += f"{role}\n"
            counter += 1

        mention = member.mention

        embed = discord.Embed(
            title = f"User Info"
        ).add_field(
            name="Name:",
            value=name
        ).add_field(
            name="Joined Server:",
            value=joined_guild_at
        ).add_field(
            name="Joined Discord:",
            value=joined_discord_at
        ).add_field(
            name="Status:",
            value=current_status
        ).add_field(
            name="ID:",
            value=user_id
        ).add_field(
            name="Roles:",
            value=roles
        )

        if avatar:
            embed.set_thumbnail(url=avatar_url)

        await ctx.send(embed=embed)