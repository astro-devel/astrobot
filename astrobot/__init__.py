"""all-encompassing god-level bot for mochjicord"""

__version__ = '22.1.5'
__changelog__ = """**CHANGELOG**\n
- add remindme command, for setting reminders
- add reminders command, for listing reminders (reminders list), and deleting reminders (reminders delete X)
- [BTS] create Astrobot object, subclassed from commands.Bot
- [BTS] create AstrobotHelpCommand object, subclassed from commands.DefaultHelpCommand
- [BTS] converted MochjiMojis functions to variables (should help prevent 429-ing **Prayge**)
- [BTS] reimpl util.Timer as time.BaseTimer to be used as subclass for various timers"""