import os
import discord
from discord.ext import commands
from astrobot.colors import MochjiColor

class ErrorHandler(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_command_error(self, ctx: commands.Context, error: commands.CommandError):
        has_self_handler = []
        if ctx.invoked_with in has_self_handler:
            return # if the command has its own handler, no need to run it through the global one

        if isinstance(error, commands.CommandNotFound):
            return
        elif isinstance(error, commands.MissingPermissions) or isinstance(error, commands.CheckFailure):
            text = f"{self.bot.custom_emojis.error} You are not authorized to use this command!"
            embed = discord.Embed(title=text, colour=MochjiColor.red())
            await ctx.send(ctx.author.mention, embed=embed, delete_after=10)
            return
        elif isinstance(error, commands.BotMissingPermissions):
            text = f"{self.bot.custom_emojis.error} Sorry, I'm not allowed to do that here. :("
            embed = discord.Embed(title=text, colour=MochjiColor.red())
            await ctx.send(ctx.author.mention, embed=embed, delete_after=10)
            return
        text = f"{self.bot.custom_emojis.error} Uncaught error occured. Hopefully this will help:"
        err_type = str(type(error)).split('.')[-1].replace("'", "")
        err = f"<{err_type} {error}"
        embed = discord.Embed(
            title=text,
            description=err,
            colour=MochjiColor.red()
        )
        if os.environ.get("DEVEL"):
            await ctx.send(ctx.author.mention, embed=embed)
        else:
            await ctx.send(ctx.author.mention, embed=embed, delete_after=10)