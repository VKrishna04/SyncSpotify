from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import os
import json


class YouTubeAuthenticator:
    def __init__(self):
        self.flow = InstalledAppFlow.from_client_secrets_file(
            "client_secrets.json",
            scopes=["https://www.googleapis.com/auth/youtube.force-ssl"],
        )

    def get_authorization_url(self):
        return self.flow.authorization_url()[0]

    def fetch_token(self, redirect_url):
        self.flow.fetch_token(authorization_response=redirect_url)

    def credentials_to_dict(self):
        credentials = self.flow.credentials
        return {
            "token": credentials.token,
            "refresh_token": credentials.refresh_token,
            "token_uri": getattr(credentials, "token_uri", None),
            "client_id": credentials.client_id,
            "client_secret": credentials.client_secret,
            "scopes": credentials.scopes,
        }

    def credentials_from_dict(self, credentials_dict):
        from google.oauth2.credentials import Credentials

        return Credentials(
            credentials_dict["token"],
            refresh_token=credentials_dict["refresh_token"],
            token_uri=credentials_dict.get("token_uri"),
            client_id=credentials_dict["client_id"],
            client_secret=credentials_dict["client_secret"],
            scopes=credentials_dict["scopes"],
        )
