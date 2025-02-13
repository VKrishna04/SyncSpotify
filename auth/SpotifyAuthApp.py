import os
import sys
from dotenv import load_dotenv

from PyQt5.QtCore import QUrl
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QApplication

from ..auth.spotify_auth import SpotifyAuthenticator
from ..gui.SyncSpotify import SyncSpotify

# Spotify configuration
load_dotenv()
SPOTIPY_CLIENT_ID = os.getenv("SPOTIPY_CLIENT_ID")
SPOTIPY_CLIENT_SECRET = os.getenv("SPOTIPY_CLIENT_SECRET")
SPOTIPY_REDIRECT_URI = "http://localhost:62908/callback"


class OAuthHandler(QWidget):
    def __init__(self, authenticator):
        super().__init__()
        self.authenticator = authenticator
        self.webview = QWebEngineView(self)
        self.webview.urlChanged.connect(self.handle_url_change)

        layout = QVBoxLayout()
        layout.addWidget(self.webview)
        self.setLayout(layout)

        # Get the authorization URL
        auth_url = self.authenticator.get_authorization_url()
        self.webview.setUrl(QUrl(auth_url))

    def handle_url_change(self, qurl):
        # Extract the redirected URL
        redirect_url = qurl.toString()

        # Check if the URL contains the expected redirect URI
        if SPOTIPY_REDIRECT_URI in redirect_url:
            # Get the access token
            token_info = self.authenticator.get_access_token(redirect_url)

            # Close the OAuthHandler window
            self.close()

            # Start the main application
            app = QApplication(sys.argv)
            window = SyncSpotify(token_info["access_token"], token_info["access_token"])
            window.show()
            sys.exit(app.exec_())


if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Initialize the SpotifyAuthenticator
    spotify_authenticator = SpotifyAuthenticator(
        SPOTIPY_CLIENT_ID, SPOTIPY_CLIENT_SECRET, SPOTIPY_REDIRECT_URI
    )

    # Create and run the OAuthHandler window
    oauth_handler = OAuthHandler(spotify_authenticator)
    oauth_handler.show()

    sys.exit(app.exec_())
