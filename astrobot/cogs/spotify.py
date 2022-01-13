from typing import Optional
import discord
from discord.ext import commands
from discord.ext.commands.core import check
from astrobot.colors import MochjiColor
from astrobot.spotify import spotify as sp

class Spotify(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot: discord.Bot = bot
        self._commands = {
            "_help": self._help_message,
            "_error": self._error,
            "_connect": self._connect,
            "_play": self._play,
            "_playback_mgr": self._playback_mgr,
            "_getter": self._getter
        }
        self.cached_sessions = dict()
    
    async def _error(self, ctx, err_type, *args):
        error = '**Unknown**'
        if err_type == 'not_found':
            error = f'**Command Not Found ({args[0]})**'
        elif err_type == 'generic':
            error = args[0]
        return f"An Error Occurred: {error}"

    async def _help_message(*args):
        return '''```
Spotify Module (!sp) Commands:

-\thelp: show this message
-\tconnect: connect your discord account to astrobot
-\tplay track [track]: play a track
-\tpause: pause playback
-\tresume: resume playback
-\tnext: play next track
-\tprevious: play previous track
-\tget [devices]: get a list of [devices]
```'''

    async def _getter(self, ctx, *args):
        user: Optional[sp.SpotifyUserObject] = self.cached_sessions.get(ctx.author.id.__str__(), await self._grab_user_and_cache(ctx.author.id.__str__()))
        if not user:
            return "User could not be found... If you haven't connected your spotify account yet, do that by running '!sp connect'."
        option = args[0]
        if option == "devices":
            devstring = str()
            count = 1
            for dev in user.session.playback_devices():
                devstring += f"{count}. **{dev.name}** - *{dev.type}*, **Status:** {'***ACTIVE***' if dev.is_active else '*INACTIVE*'}, Volume: **{dev.volume_percent}%**\n"
                count += 1
            embed = discord.Embed(
                title = "Visible Devices:",
                description= devstring
            )
            await ctx.send(embed=embed)
            return
        elif option == "playlists":
            return "FNI"
        return

    async def _grab_user_and_cache(self, user_id) -> Optional[sp.SpotifyUserObject]:
        user = sp.SpotifyUserObject(user_id)
        if not user.pop_from_db():
            return None
        self.cached_sessions[user_id] = user
        return user

    async def _playback_mgr(self, ctx, *args):
        user: Optional[sp.SpotifyUserObject] = self.cached_sessions.get(ctx.author.id.__str__(), await self._grab_user_and_cache(ctx.author.id.__str__()))
        if not user:
            return "User could not be found... If you haven't connected your spotify account yet, do that by running '!sp connect'."
        option = args[0]
        if option == "next":
            user.session.playback_next()
            return "Playing next track..."
        elif option == "previous":
            user.session.playback_previous()
            return "Playing previous track..."
        elif option == "pause":
            user.session.playback_pause()
            return "Pausing playback..."
        elif option == "resume":
            user.session.playback_resume()
            return "Resuming playback..."

    async def _play(self, ctx, type, *args):
        user: Optional[sp.SpotifyUserObject] = self.cached_sessions.get(ctx.author.id.__str__(), await self._grab_user_and_cache(ctx.author.id.__str__()))
        if not user:
            return "User could not be found... If you haven't connected your spotify account yet, do that by running '!sp connect'."
        if type == "track":
            track = user.session.search(args[0])[0].items[0]
            user.session.playback_start_tracks([track.id])
            return f"Playing **{track.name}** by **{track.artists[0].name}**..."
        else:
            return await self._error('generic', f"option '{type}' not recognized...")
        return

    async def _connect(self, ctx, *args):
        from asyncio import TimeoutError
        from urllib.parse import parse_qs

        _user = sp.SpotifyUserObject(discord_user_id=ctx.author.id.__str__())
        try:
            await ctx.author.send("Here's your private link!")
        except discord.Forbidden:
            return "It appears that I'm not able to DM you. In order to keep everything secure, I need to DM you a private login link. Please enable DMs from server members and try again."

        def sanity_check(m):
            return m.channel == ctx.author.dm_channel and m.author == ctx.author

        await ctx.author.send(_user.auth.url)
        await ctx.author.send("After you sign in, you will be given a code to send back to me. Once I get that code, you'll be logged in and ready to go! (I'll wait for 5 minutes, but after that I'll have to time out.)")
        try:
            _ret = await self.bot.wait_for('message', timeout=300.0, check=sanity_check)
            _params = parse_qs(_ret.content)
            callback = sp.CallbackObject(_params['code'][0], _params['state'][0])
        except TimeoutError:
            await ctx.author.send("Are you still there? Sorry, I had to time out, but if you still want to connect, feel free to run the command '!sp connect' again!")
            return

        success, err = _user.authorize_user(callback)
        if success:
            _user.store_to_db()
            self.cached_sessions[ctx.author.id] = _user
            await ctx.author.send("Congratulations! You're now logged in with your spotify account and are able to use the !sp commands. Have fun!")
        else:
            await ctx.author.send(await self._error(ctx, 'generic', err))

    def _parse_args(self, _args: str) -> tuple:
        args = _args.split()
        cmd = tuple()
        if args[0] == 'help':
            cmd = (self._commands['_help'], ())
        elif args[0] == 'connect':
            cmd = (self._commands['_connect'], ())
        elif args[0] == 'play':
            cmd = (self._commands['_play'], (args[1], ' '.join(args[2:])))
        elif args[0] == 'next' or args[0] == 'previous' or args[0] == 'pause' or args[0] == 'resume':
            cmd = (self._commands['_playback_mgr'], [args[0]])
        elif args[0] == 'get':
            cmd = (self._commands['_getter'], [' '.join(args[1:])])
        else:
            cmd = (self._commands['_error'], ('not_found', ' '.join(args)))
        return cmd

    async def _run(self, ctx, args):
        cmd, cmd_args = self._parse_args(args)
        return await cmd(ctx, *cmd_args)

    @commands.command()
    async def sp(self, ctx, *, args: str):
        res = await self._run(ctx, args)
        if res:
            await ctx.send(res)
        return