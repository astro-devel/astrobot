from dataclasses import dataclass
from typing import Optional
import tekore as spot
from tekore._auth.scope import Scope
from astrobot.spotify import database as db

@dataclass
class CallbackObject:
    code: str
    state: str

class SpotifyUserObject:
    def __init__(self, discord_user_id: str, user_token: Optional[spot.RefreshingToken]=None) -> None:
        self.scopes = Scope(
            spot.scope.user_read_currently_playing,
            spot.scope.user_modify_playback_state,
            spot.scope.user_read_playback_state
        )
        self.CLIENT_ID, self.CLIENT_SECRET, self.REDIRECT_URI = spot.config_from_environment()
        self.discord_user_id = discord_user_id
        self.cred = spot.RefreshingCredentials(self.CLIENT_ID, self.CLIENT_SECRET, self.REDIRECT_URI)
        self.auth = spot.UserAuth(self.cred, scope=self.scopes)
        self.client_token = spot.request_client_token(self.CLIENT_ID, self.CLIENT_SECRET)
        self.user_token = user_token
        self.session = spot.Spotify(token=self.user_token or self.client_token, asynchronous=False)
        self.session_type = 'user' if self.user_token else 'client'
        if not self.user_token:
            self.check_for_existing_user()
    
    def check_for_existing_user(self) -> None:
        for obj in db.session.query(db.SpotifyUserToken__Obj):
            if obj.user_id == self.discord_user_id:
                self.pop_from_db()

    def authorize_user(self, callback: CallbackObject) -> tuple[bool, Optional[Exception]]:
        '''
            Authorize a User object with given callback details. Sets self.user_token. 
            Returns tuple with boolean for success and an Exception object (if one occured).
        '''
        try:
            _token = self.auth.request_token(code=callback.code, state=callback.state)
            assert isinstance(_token, spot.RefreshingToken) # this should always return a RefreshingToken, but just in case
            self.user_token = _token
        except Exception as err:
            return (False, err)
        return (True, None)
    
    def refresh_token(self):
        try:
            self.user_token = self.cred.refresh_user_token(self.user_token.refresh_token)
            return True
        except Exception:
            return False

    def store_to_db(self):
        db.session.add(db.SpotifyUserToken__Obj(
            user_id = self.discord_user_id,
            access_token = self.user_token.access_token,
            refresh_token = self.user_token.refresh_token,
            expires_at = self.user_token._token.expires_at
        ))
        db.session.commit()
        return True
    
    def update_db(self):
        from sqlalchemy import update
        db.session.execute( 
            update(db.SpotifyUserToken__Obj).
            where(db.SpotifyUserToken__Obj.user_id == self.discord_user_id).
            values(
                access_token = self.user_token.access_token,
                refresh_token = self.user_token.refresh_token,
                expires_at=self.user_token._token.expires_at
            )
        )
        db.session.commit()

    def pop_from_db(self):
        import time
        _db_tok = None
        for obj in db.session.query(db.SpotifyUserToken__Obj):
            if obj.user_id == self.discord_user_id:
                _db_tok = obj
                break

        if not _db_tok:
            return False

        _tok = spot.Token(token_info={
            'token_type': 'Bearer',
            'access_token': _db_tok.access_token,
            'refresh_token': _db_tok.refresh_token,
            'expires_in': int(_db_tok.expires_at) - int(time.time())
        }, uses_pkce=False)
        _tok._scope = self.scopes
        self.user_token = spot.RefreshingToken(_tok, self.cred._client)
        self.session.token = self.user_token
        self.session_type = 'user'
        return True

def __login(user: SpotifyUserObject):
    '''for testing only, do not this function anywhere besides the REPL!'''
    import webbrowser
    from urllib.parse import urlparse
    from urllib.parse import parse_qs

    webbrowser.open(user.auth.url)
    _redirurl = input("URL: ")
    _params = parse_qs(urlparse(_redirurl).query)
    callback = CallbackObject(_params['code'][0], _params['state'][0])
    if user.authorize_user(callback)[0]:
        return True
    return False


    

