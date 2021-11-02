import discord
from discord.ext import commands
from astrobot.colors import MochjiColor


class ErrorHandler(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_command_error(self, ctx: commands.Context, error: commands.CommandError):
        if isinstance(error, commands.CommandNotFound):
            return
        elif isinstance(error, commands.MissingPermissions):
            text = "You are not authorized to use this command!"
            embed = discord.Embed(title=text, colour=MochjiColor.red())
            await ctx.send(ctx.author.mention, embed=embed, delete_after=5)
        elif isinstance(error, commands.BotMissingPermissions):
            text = "Sorry, I'm not allowed to do that here. :("
            embed = discord.Embed(title=text, colour=MochjiColor.red())
            await ctx.send(ctx.author.mention, embed=embed, delete_after=5)
        else:
            text = "Sorry, an unknown error occured. Please try again."
            embed = discord.Embed(
                title=text,
                description=error,
                colour=MochjiColor.red()
            )
            await ctx.send(ctx.author.mention, embed=embed, delete_after=5)