__version__ = '21.12.3'
__changelog__ = f"""**CHANGELOG**\n
- added role-checker to moderation commands (fixes cef4a613)
- made roles in '!whois' command mentions instead of str (also made embed color color of top role)
- converted responses from '!mute' and '!unmute' commands to embed
"""

# globs
mute_timers = {}