import os
from discord import colour
import requests
import discord
from discord.ext import commands
from astrobot.colors import MochjiColor
from astrobot.user_sys.database import session as db_session
from astrobot.user_sys.database import FMUser__Obj as _DB_FMUser__Obj

API_KEY = os.environ["LAST_FM_API_KEY"]

class FMCommands(commands.Cog):
    def __init__(self, bot) -> None:
        self.user = None
        self.bot: commands.Bot = bot

    def make_request_url(self, _method, _user):
        return f"http://ws.audioscrobbler.com/2.0/?method={_method}&user={_user}&api_key={API_KEY}&format=json"

    @commands.command()
    async def fm(self, ctx):

        _db_query = db_session.query(_DB_FMUser__Obj)
        for item in _db_query:
            if str(item.user_id) == str(ctx.author.id):
                user = item.lastfm_user
                break

        _last_track = requests.get(self.make_request_url("user.getrecenttracks", user)).json()['recenttracks']['track'][0]
        _last_track_artist = _last_track['artist']['#text']
        _last_track_album = _last_track['album']['#text']
        _last_track_title = _last_track['name']
        _last_track_url = _last_track['url']

        user_scrobble_count = _user_info = requests.get(self.make_request_url("user.getInfo", user)).json()['user']['playcount']
        user_avatar_url = f"https://cdn.discordapp.com/avatars/{ctx.author.id}/{ctx.author.avatar}" if ctx.author.avatar else None

        try:
            _x = _last_track.get('@attr')['nowplaying']
            assert _x == 'true'
            _is_now_playing = True
        except:
            _is_now_playing = False

        embed = discord.Embed(
            colour = MochjiColor.white()
        ).add_field(
            name="\a",
            value=f"[{_last_track_title}]({_last_track_url})\n**{_last_track_artist}** | *{_last_track_album}*"
        )
        embed.set_author(name=f"{'Now Playing' if _is_now_playing else 'Last Played Track'} - {ctx.author.nick if ctx.author.nick else ctx.author.name}", url=f"https://last.fm/user/{user}", icon_url=user_avatar_url)
        embed.set_thumbnail(url=_last_track['image'][3]['#text'])
        embed.set_footer(text=f"{user} has {user_scrobble_count} total scrobbles.")

        await ctx.send(embed=embed)
    
    @commands.command()
    async def fmsetuser(self, ctx, lastfm_username):
        _user = _DB_FMUser__Obj(
            user_id = ctx.author.id,
            lastfm_user = lastfm_username
        )
        db_session.add(_user)
        db_session.commit()
        await ctx.send(f"Successfully connected last.fm user '{lastfm_username}' to {ctx.author.mention}")