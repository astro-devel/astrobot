from discord.ext import commands

class MochjiMojis(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
    
    @commands.command(hidden=True)
    async def sosadge(self, ctx):
        await ctx.send(self.sadge)

    @commands.Cog.listener()
    async def on_ready(self):
        emoji_guild = self.bot.get_guild(483461183496519698)
        _emojis = await emoji_guild.fetch_emojis()
        emojis = dict()
        for emoji in _emojis:
            emojis[emoji.id] = emoji
        self.warning = emojis.get(905755522739892274)
        self.error = emojis.get(905755493111312394)
        self.success = emojis.get(905755460446060544)
        self.sadge = emojis.get(935004762733158452)