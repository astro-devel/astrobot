import discord
from discord.ext import commands


class UserInfo(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot

    @commands.command()
    async def whois(self, ctx, member: discord.Member):
        name = f"{member.name}#{member.discriminator}"
        joined_guild_at = member.joined_at.date()
        joined_discord_at = member.created_at.date()
        current_status = member.raw_status
        avatar = member.avatar
        user_id = member.id
        _roles = member.roles
        roles = ""
        counter = 0

        _roles.reverse()
        for role in _roles:
            if counter > 10:
                break
            if role.name == "@everyone":
                continue
            roles += f"{role.mention}\n"
            counter += 1

        embed = (
            discord.Embed(colour=member.top_role.color)
            .add_field(name="Name:", value=name)
            .add_field(name="Joined Server:", value=joined_guild_at)
            .add_field(name="Joined Discord:", value=joined_discord_at)
            .add_field(name="Status:", value=current_status)
            .add_field(name="ID:", value=user_id)
            .add_field(name="Roles:", value=roles if roles else "None")
        )

        if avatar:
            embed.set_thumbnail(url=avatar.__str__() if avatar else None)

        await ctx.send(embed=embed)

    @commands.command()
    async def whoami(self, ctx):
        await self.whois(ctx, ctx.author)
