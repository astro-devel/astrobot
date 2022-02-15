import os
from discord.ext.commands import Bot
from ..time import *
from .error import ErrorHandler
from .management import Management
from .moderation import Moderation
from .test import TestCommands
from .user import UserInfo
from .logger import Logging
from .spotify import Spotify
from .halys import Halys


def init_cogs(bot: Bot) -> None:

    if os.environ.get("DEVEL"):
        # cog(s) that should ONLY be enabled during devel
        bot.add_cog(TestCommands(bot))
    else:
        # cog(s) that should NOT be enabled during devel
        pass

    bot.add_cog(UserInfo(bot))
    bot.add_cog(Time(bot))
    bot.add_cog(Reminders(bot))
    bot.add_cog(ErrorHandler(bot))
    bot.add_cog(Moderation(bot))
    bot.add_cog(Management(bot))
    bot.add_cog(Logging(bot))
    bot.add_cog(Spotify(bot))
    bot.add_cog(Halys(bot))
