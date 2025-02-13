from pathlib import Path
from rich import print
import subprocess
import shutil
import atexit
import json


class DIR:
    start_dir = Path(__file__).resolve().parent
    temp_dir = Path(start_dir, "__TEMP__")

    sync_script = "sync-playlist.py"
    json_file = "data.spotdl"

    @classmethod
    def create_temp_dir(cls):
        dir = cls.temp_dir

        if dir.exists():
            cls.delete_temp()
        dir.mkdir(parents=True)

    @classmethod
    def delete_temp(cls):
        dir = cls.temp_dir

        if dir.exists():
            shutil.rmtree(dir)

    @classmethod
    def rename_temp_dir(cls, name):
        cls.temp_dir.rename(name)


class SpotDL:
    type = ""

    def start_spotdl(self, url):
        try:
            if url.startswith(
                (
                    "https://open.spotify.com/playlist/",
                    "https://open.spotify.com/album/",
                )
            ):
                subprocess.run(
                    [
                        "spotdl",
                        "--log-level",
                        "INFO",
                        "sync",
                        url,
                        "--save-file",
                        "data.spotdl",
                    ],
                    cwd=DIR.temp_dir,
                ).check_returncode()

                if "playlist" in url:
                    SpotDL.type = "playlist"
                elif "album" in url:
                    SpotDL.type = "album"
            else:
                raise NameError()
        except (NameError, KeyboardInterrupt, subprocess.CalledProcessError):
            raise

    def extract_playlist_name(self):
        file = Path(DIR.temp_dir, DIR.json_file)

        if file.exists():
            file = open(file, "r", encoding="utf8")
            data = json.load(file)

            if "playlist" in SpotDL.type:
                return data["songs"][0]["list_name"]
            elif "album" in SpotDL.type:
                return data["songs"][0]["album_name"]
        else:
            raise json.JSONDecodeError("File not found or is empty", "", 0)


if __name__ == "__main__":
    try:
        d = DIR()

        print("[bold italic cyan]Insert a valid Spotify URL")
        url = input(">> ")

        if url.lower() == "q":
            raise SystemExit()

        d.create_temp_dir()
        spotdl = SpotDL()
        spotdl.start_spotdl(url)

        type_name = spotdl.extract_playlist_name()
        if type_name:
            new_dir = Path(d.temp_dir.parent, type_name)

            if new_dir.exists():
                raise FileExistsError()
            else:
                d.rename_temp_dir(new_dir)

                print("\n[bold cyan]Sync completed!")
        else:
            raise ValueError("Playlist or album name could not be determined.")

    except NameError:
        print("\n[bold red]ERROR: It's not a valid Spotify URL.")
    except subprocess.CalledProcessError:
        print("\n[bold red]ERROR: SpotDL Error.")
    except json.JSONDecodeError:
        print("\n[bold red]ERROR: 'data.spotdl' file was not created.")
    except FileExistsError:
        print("\n[bold red]ERROR: The folder already exists")
    except KeyboardInterrupt:
        print("\n[bold red]Canceling...")
    except SystemExit:
        pass

    atexit.register(d.delete_temp)
