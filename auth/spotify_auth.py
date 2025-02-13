import spotipy
from spotipy.oauth2 import SpotifyOAuth

SPOTIPY_SCOPE = "user-library-read, user-read-private playlist-read-collaborative playlist-modify-public user-follow-read user-library-read user-library-modify playlist-modify-private user-read-email "


class SpotifyAuthenticator:
    def __init__(self, client_id, client_secret, redirect_uri):
        self.sp_oauth = SpotifyOAuth(
            client_id, client_secret, redirect_uri, scope=SPOTIPY_SCOPE
        )

    def get_authorization_url(self):
        return self.sp_oauth.get_authorize_url()

    def get_access_token(self, redirect_url):
        code = self.sp_oauth.parse_response_code(redirect_url)
        if code:
            token_info = self.sp_oauth.get_access_token(code)
            return token_info
        return None
