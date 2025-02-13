from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QPushButton,
    QLabel,
    QComboBox,
    QMainWindow,
)
import spotipy
import requests
from ..logic.sync_logic import (
    sync_spotify_to_spotify,
)


class SyncSpotify(QMainWindow):
    def __init__(self, source_access_token, destination_access_token):
        super().__init__()

        # Attributes to store the access tokens
        self.source_access_token = source_access_token
        self.destination_access_token = destination_access_token

        # Fetch the user's playlists from Spotify during initialization
        self.source_playlists = self.get_user_playlists(self.source_access_token)
        self.destination_playlists = self.get_user_playlists(
            self.destination_access_token
        )

        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("SyncSpotify")
        self.setGeometry(100, 100, 800, 600)

        layout = QVBoxLayout()

        self.source_playlist_combo = QComboBox()
        self.source_playlist_combo.addItems(self.source_playlists)
        layout.addWidget(self.source_playlist_combo)

        self.destination_playlist_combo = QComboBox()
        self.destination_playlist_combo.addItems(self.destination_playlists)
        layout.addWidget(self.destination_playlist_combo)

        self.sync_button = QPushButton("Sync Spotify Accounts", self)
        self.sync_button.clicked.connect(self.sync_playlists)
        layout.addWidget(self.sync_button)

        self.convert_button = QPushButton("Convert to YouTube Playlist", self)
        self.convert_button.clicked.connect(self.convert_to_youtube)
        layout.addWidget(self.convert_button)

        self.status_label = QLabel("Status: Ready")
        layout.addWidget(self.status_label)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def sync_playlists(self):
        selected_source_playlist = self.source_playlist_combo.currentText()
        selected_destination_playlist = self.destination_playlist_combo.currentText()

        self.status_label.setText(
            f"Status: Syncing {selected_source_playlist} to {selected_destination_playlist}"
        )

        self.get_user_playlists(self.source_access_token)
        self.get_user_playlists(self.destination_access_token)

        sync_spotify_to_spotify(self.source_playlists, self.destination_playlists)
        self.status_label.setText("Status: Sync Complete")

    def convert_to_youtube(self):
        # Logic to convert Spotify playlist to YouTube
        pass

    def get_user_playlists(self, access_token):
        sp = spotipy.Spotify(auth=access_token)

        playlists = sp.current_user_playlists()

        if playlists is not None and "items" in playlists:
            return [playlist["name"] for playlist in playlists["items"]]
        else:
            print("No playlists found.")
            return []
