from discord.ext.commands import Bot

def init_cogs(bot: Bot) -> None:
    import os
    from astrobot.emojis import MochjiMojis
    from astrobot.error import ErrorHandler
    from astrobot.management import Management
    from astrobot.moderation import Moderation
    from astrobot.test import TestCommands
    from astrobot.time import TimeStuffs
    from astrobot.user import UserInfo
    #from astrobot.welcome import WelcomeWagon
    from astrobot.roles import Roles
    #from astrobot.fm.fm import FMCommands

    if os.environ.get("DEVEL"):
        # cog(s) that should ONLY be enabled during devel
        bot.add_cog(TestCommands(bot))
    else:
        # cog(s) that should NOT be enabled during devel
        #bot.add_cog(WelcomeWagon(bot))
        pass

    bot.add_cog(UserInfo(bot))
    bot.add_cog(MochjiMojis(bot))
    bot.add_cog(TimeStuffs(bot))
    bot.add_cog(ErrorHandler(bot))
    bot.add_cog(Moderation(bot))
    bot.add_cog(Roles(bot))
    bot.add_cog(Management(bot))
    #bot.add_cog(FMCommands(bot))