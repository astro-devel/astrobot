__version__ = '21.12.2'
__changelog__ = f"""**CHANGELOG**\n
- added guild_id as required DB value for UserMod__Obj (fixes c4ebeac9)
- fixed bug c4ebeac9 (get_mutes is not server specific)
- fixed bug 001 (bot sends a message that you have been kicked/banned even if the command fails.)
"""

# globs
mute_timers = {}