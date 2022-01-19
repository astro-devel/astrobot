from discord.ext import commands

class MochjiMojis(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.emoji_guild = None
        self.bot = bot

    async def warning(self):
        return await self.emoji_guild.fetch_emoji(905755522739892274)
    async def error(self):
        return await self.emoji_guild.fetch_emoji(905755493111312394)
    async def success(self):
        return await self.emoji_guild.fetch_emoji(905755460446060544)

    @commands.Cog.listener()
    async def on_ready(self):
        self.emoji_guild = self.bot.get_guild(483461183496519698)