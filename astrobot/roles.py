from multiprocessing import Value
import os
import discord
from discord.ext import commands
from colors import MochjiColor

class Roles(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot: commands.Bot = bot
        self.roles_and_reactions = {
            discord.PartialEmoji(name="🥜"): 904437228829290537,
            discord.PartialEmoji(name="daddyu", id=844610685333930044): 904437310341410876,
            discord.PartialEmoji(name="⏰"): 904437357334392833,
            discord.PartialEmoji(name="🟪"): 904437401013846016
        }
        self.role_message_id = 0

    @commands.command()
    async def get_emoji_id(self, ctx, emoji : discord.Emoji):
        await ctx.send(emoji.id)

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def init_roles(self, ctx):
        channel = self.bot.get_channel(os.environ["ROLE_CHANNEL_ID"])
        text = "React to recieve a role."
        embed = discord.Embed(title=text, colour=MochjiColor.white())
        msg: discord.Message = await ctx.send(embed=embed)
        for emoji in self.roles_and_reactions:
            await msg.add_reaction(emoji)
        self.role_message_id = msg.id

    @init_roles.error
    async def perms_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            # TODO: implement "else" catcher for if error is of different exception type
            text = f"Sorry, you do not have permission to do that!"
            embed = discord.Embed(title=text, colour=MochjiColor.red())
            await ctx.send(ctx.author.mention, embed=embed)

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
        if payload.message_id != self.role_message_id:
            return
        if payload.member.id == self.bot.user.id:
            return
        guild = self.bot.get_guild(payload.guild_id)
        if not guild:
            print("self.bot.get_guild -> None")
            return
        try:
            role_id = self.roles_and_reactions[payload.emoji]
        except KeyError:
            print("role_id -> roles_and_reactions : KeyError")
            return
        role = guild.get_role(role_id)
        if not role:
            print("guild.get_role -> None")
            return
        await payload.member.add_roles(role)
    
    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload: discord.RawReactionActionEvent):
        if payload.message_id != self.role_message_id:
            return
        guild = self.bot.get_guild(payload.guild_id)
        if not guild:
            print("self.bot.get_guild -> None")
            return
        member = guild.get_member(payload.user_id)
        if member is None:
            print("guild.get_member -> None")
            return
        if member.id == self.bot.user.id:
            return
        try:
            role_id = self.roles_and_reactions[payload.emoji]
        except KeyError:
            print("role_id -> roles_and_reactions : KeyError")
            return
        role = guild.get_role(role_id)
        if not role:
            print("guild.get_role -> None")
            return
        await member.remove_roles(role)

