__version__ = '21.11.3'
__changelog__ = f"""**CHANGELOG**\n
- Implemented !mute, !unmute, and !get_mute commands
- Changed !get_mod_info command to !modinfo
- Changed error messages to delete after 10s instead of 5s
- Added ability to combine multipliers on !slowmode command (i.e. !slowmode 5h25m)"""

# globs
mute_timers = {}