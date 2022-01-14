import os
from discord.ext.commands import Bot
from astrobot.cogs.emojis import MochjiMojis
from astrobot.cogs.error import ErrorHandler
from astrobot.cogs.management import Management
from astrobot.cogs.moderation import Moderation
from astrobot.cogs.test import TestCommands
from astrobot.time import TimeStuffs
from astrobot.cogs.user import UserInfo
from astrobot.cogs.logger import Logging
from astrobot.cogs.spotify import Spotify
from astrobot.cogs.halys import Halys

def init_cogs(bot: Bot) -> None:

    if os.environ.get("DEVEL"):
        # cog(s) that should ONLY be enabled during devel
        bot.add_cog(TestCommands(bot))
    else:
        # cog(s) that should NOT be enabled during devel
        pass

    bot.add_cog(UserInfo(bot))
    bot.add_cog(MochjiMojis(bot))
    bot.add_cog(TimeStuffs(bot))
    bot.add_cog(ErrorHandler(bot))
    bot.add_cog(Moderation(bot))
    bot.add_cog(Management(bot))
    bot.add_cog(Logging(bot))
    bot.add_cog(Spotify(bot))
    bot.add_cog(Halys(bot))