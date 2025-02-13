import os
import sys
import json

# from dotenv import load_dotenv

from PyQt5.QtWidgets import QApplication, QInputDialog
from flask import Flask, redirect, request, render_template, url_for, session, jsonify
from flask_executor import Executor

from gui.SyncSpotify import SyncSpotify
from auth.spotify_auth import SpotifyAuthenticator
from logic.sync_logic import sync_spotify_to_spotify, first_time_transfer
from auth.youtube_auth import YouTubeAuthenticator
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import isodate


# Initialize the Flask app
flask_app = Flask(__name__, template_folder="templates")
flask_app.config["EXECUTOR_TYPE"] = "thread"
flask_app.config["EXECUTOR_MAX_WORKERS"] = 2  # Adjust as needed
executor = Executor(flask_app)


class AppContext:
    spotify_accounts = (
        []
    )  # List to store Spotify access tokenscounts = []  # List to store Spotify access tokens


# Spotify configuration
# load_dotenv()
SPOTIPY_CLIENT_ID = os.getenv("SPOTIPY_CLIENT_ID")
SPOTIPY_CLIENT_SECRET = os.getenv("SPOTIPY_CLIENT_SECRET")
PORT_SECRET = os.getenv("PORT_SECRET")
SPOTIPY_SCOPE = "user-library-read user-read-private playlist-read-collaborative playlist-modify-public user-follow-read user-library-read user-library-modify playlist-modify-private user-read-email "  # Define the required scopes
if PORT_SECRET is None:
    PORT_SECRET = "62908"
SPOTIPY_REDIRECT_URI = f"http://localhost:{PORT_SECRET}/callback"


# Initialize the SpotifyAuthenticator
spotify_authenticator = SpotifyAuthenticator(
    SPOTIPY_CLIENT_ID, SPOTIPY_CLIENT_SECRET, SPOTIPY_REDIRECT_URI
)

# Initialize the YouTubeAuthenticator
youtube_authenticator = YouTubeAuthenticator()


@flask_app.route("/callback")
def handle_callback():
    redirect_url = request.url

    if "spotify" in redirect_url:
        handle_spotify_callback(redirect_url)

    return f"Callback received. Redirect URL: {redirect_url}"


def handle_spotify_callback(redirect_url):
    # Get the Spotify access token
    token_info = spotify_authenticator.get_access_token(redirect_url)

    if token_info and "access_token" in token_info:
        AppContext.spotify_accounts.append(token_info["access_token"])
    else:
        print("Error: Unable to get Spotify access token.")

    # Start the main application for Spotify in the main thread
    start_spotify_app()


def start_spotify_app():
    # Start the main application for Spotify in the main thread
    app = QApplication(sys.argv)

    if len(AppContext.spotify_accounts) < 2:
        print("Error: At least two Spotify accounts are required.")
        return

    # Get the source Spotify account from the user
    source_account, ok = QInputDialog.getItem(
        None,
        "Choose Source Spotify Account",
        "Select the source Spotify account:",
        [f"Account {i+1}" for i in range(len(AppContext.spotify_accounts))],
        0,
        False,
    )

    if not ok:
        print("User canceled account selection.")
        return

    # Remove the selected source account from the available accounts
    source_index = int(source_account.split()[-1]) - 1
    source_access_token = AppContext.spotify_accounts.pop(source_index)

    # Get the destination Spotify account from the user
    destination_account, ok = QInputDialog.getItem(
        None,
        "Choose Destination Spotify Account",
        "Select the destination Spotify account:",
        [f"Account {i+1}" for i in range(len(AppContext.spotify_accounts))],
        0,
        False,
    )

    if not ok:
        # Return the source account back to the list if the user canceled destination selection
        AppContext.spotify_accounts.insert(source_index, source_access_token)
        print("User canceled destination selection.")
        return

    # Use the selected destination Spotify account
    destination_index = int(destination_account.split()[-1]) - 1
    destination_access_token = AppContext.spotify_accounts.pop(destination_index)

    try:
        # Modify the instantiation of SyncSpotify with source and destination access tokens
        window = SyncSpotify(source_access_token, destination_access_token)
        window.show()
        text = "Spotify app started."
        print(text)
        # Start the main event loop
        sys.exit(app.exec_())

    except Exception as e:
        print(f"Error starting Spotify app: {str(e)}")


@flask_app.route("/" or "/index")
def home():
    return render_template("index.html")


@flask_app.route("/framer")
def framer():
    return render_template("framer1.html")


@flask_app.route("/loginSpotify")
def login_spotify():
    # Redirect to Spotify for authentication
    return redirect(spotify_authenticator.get_authorization_url())


@flask_app.route("/loginYouTube")
def login_youtube():
    # Redirect to YouTube for authentication
    return redirect(youtube_authenticator.get_authorization_url())


@flask_app.route("/callbackYouTube")
def handle_youtube_callback():
    redirect_url = request.url
    youtube_authenticator.fetch_token(redirect_url)
    session["yt_token_info"] = youtube_authenticator.credentials_to_dict()
    return "YouTube callback received."


@flask_app.route("/convertSpotifyToYouTube")
def convert_spotify_to_youtube():
    sp = get_spotify_user()
    yt = get_youtube_user()
    playlist_id = request.args.get("playlist_id")
    name = request.args.get("name")
    queries = []
    playlist = []

    tracks_data = sp.playlist_tracks(
        playlist_id=playlist_id, fields="items.track(name, artists.name)"
    )
    if tracks_data is None:
        return "Error: Unable to retrieve tracks data from Spotify."
    for item in tracks_data.get("items", []):
        track = item["track"]
        query = [track["name"]]
        query.extend(artist["name"] for artist in track["artists"])
        queries.append(" ".join(query))

    for query in queries:
        rep = (
            yt.search()
            .list(part="snippet,id", q=query, type="video", maxResults=1)
            .execute()["items"][0]
        )
        video = {
            "id": rep["id"]["videoId"],
            "name": rep["snippet"]["title"],
            "channel": rep["snippet"]["channelTitle"],
            "url": f"https://youtu.be/{rep['id']['videoId']}",
        }
        playlist.append(video)

    return render_template("convert.html", playlist=playlist, name=name)


def get_spotify_user():
    from spotipy import Spotify
    from spotipy.oauth2 import SpotifyOAuth

    # Assuming the first Spotify account in the list is the one to be used
    if not AppContext.spotify_accounts:
        raise Exception("No Spotify accounts available.")

    access_token = AppContext.spotify_accounts[0]
    sp_oauth = SpotifyOAuth(
        client_id=SPOTIPY_CLIENT_ID,
        client_secret=SPOTIPY_CLIENT_SECRET,
        redirect_uri=SPOTIPY_REDIRECT_URI,
        scope=SPOTIPY_SCOPE,
    )
    return Spotify(auth=access_token)


def get_youtube_user():
    credentials = youtube_authenticator.credentials_from_dict(session["yt_token_info"])
    return build("youtube", "v3", credentials=credentials, cache_discovery=False)


@flask_app.route("/profiles")
def accounts():
    try:
        user_info = session.get("account_info", {})
        display_name = user_info.get("display_name")
        email = user_info.get("email")
        return render_template(
            "profiles.html",
            user_name=user_info.get(display_name),
            user_email=user_info.get(email),
        )
    except Exception as e:
        print(f"Error rendering profiles.html: {str(e)}")
        return "An error occurred."


@flask_app.route("/process_data", methods=["POST"])
def process_data():
    try:
        payload = request.json
        # Process payload, make API calls, perform business logic

        # Prepare a response
        response_data = {"status": "success", "message": "Data processed successfully"}
        return jsonify(response_data), 200

    except Exception as e:
        print(f"Error processing data: {str(e)}")
        response_data = {"status": "error", "message": "An error occurred"}
        return jsonify(response_data), 500


@flask_app.route("/api/users")
def get_users():
    return jsonify(AppContext.spotify_accounts)


@flask_app.route("/logout")
def logout():
    session.pop("account_info", None)
    return redirect(url_for("home"))


if __name__ == "__main__":
    # Start the Flask app in the main thread
    port = os.getenv("PORT_SECRET")
    if port is None:
        port = 62908
    flask_app.run(port=int(port), debug=True, load_dotenv=True)
