# SyncSpotify

**SyncSpotify** is a Python-based application designed to sync playlists between different Spotify accounts and convert Spotify playlists to YouTube playlists. It uses Flask for backend operations and PyQt5 for the GUI interface. While the core playlist synchronization between services is not yet implemented, it allows playlist transfers from one Spotify account to another and conversion to YouTube playlists.

<a target="_blank" href="https://icons8.com/icon/11116/spotify">Spotify logo</a> icon by <a target="_blank" href="https://icons8.com">Icons8</a>

### Key Features
- **Spotify Authentication**: Handles authentication using OAuth via Spotify's API.
- **YouTube Authentication**: Handles authentication using OAuth via YouTube's API.
- **Playlist Transfer**: Transfer playlists from one Spotify account to another.
- **Playlist Conversion**: Convert Spotify playlists to YouTube playlists.
- **Automatic Sync**: Automatically sync playlists between accounts.
- **User Interface**: Built with PyQt5 for account selection and playlist management.
- **Flask Backend**: Manages API requests and responses, ensuring smooth communication between the application and Spotify.
- **Dark/Light Mode**: Provides a user-friendly interface with support for both dark and light themes.
- **Role-based Access**: Ability to assign different roles for users with distinct permissions (e.g., viewing and managing playlists).

### Workflow
1. **User Interaction**: Users interact with the GUI built using PyQt5 to select accounts and playlists for transfer or conversion.
2. **Backend Process**: Flask manages the backend, processing API calls to transfer playlists between Spotify accounts or convert them to YouTube playlists.
3. **Response Handling**: Flask sends responses back to the GUI, updating the user on the status of the playlist transfer or conversion.

### Files Overview
- **app.py**: Contains the main logic, routing, and launch point for the Flask application.
- **auth/spotify_auth.py**: Handles Spotify OAuth authentication using the `spotipy` library.
- **auth/youtube_auth.py**: Handles YouTube OAuth authentication using the `google-auth` library.
- **gui/SyncSpotify.py**: PyQt5-based GUI application for managing user accounts and initiating playlist synchronization or conversion.
- **logic/sync_logic.py**: Placeholder for synchronization logic, which will eventually handle syncing playlists between different music services.
- **templates/framer1.html**: Landing page with login options for multiple music services.
- **templates/index.html**: Main application interface, with buttons for authentication and initiating transfers.
- **templates/profiles.html**: Displays user profile data and logout options.

### Installation
To install necessary dependencies, run:
```bash
pip install Flask PyQt5 Flask-Executor spotipy Flask-WebEngine
```

### Development Plans
- **Expanded Functionality**: The plan includes the full implementation of playlist synchronization between multiple services and seamless playlist transfer.

### Potential Improvements
- Shift the playlist syncing logic completely to the Flask backend for streamlined operations.
- Develop API integrations for other music services like Amazon Music.
