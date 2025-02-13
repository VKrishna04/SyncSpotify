from pathlib import Path
from rich import print
import subprocess


def get_directories_with_file(file_name):
    cwd = Path(__file__).resolve().parent
    directories = [path.parent.name for path in cwd.glob("**/" + file_name)]

    if not directories:
        raise FileNotFoundError()

    for path_object in directories:
        execute_file(path_object)


def execute_file(dir):
    try:
        print(f"\n[bold italic yellow]Updating playlist:[/] [bright_blue]{dir}[/]")

        subprocess.run(
            ["spotdl", "--log-level", "INFO", "sync", "data.spotdl", "--preload"],
            cwd=dir,
        ).check_returncode()
    except (subprocess.CalledProcessError, KeyboardInterrupt):
        raise


if __name__ == "__main__":
    try:
        get_directories_with_file("data.spotdl")

        print("\n[bold cyan]Sync completed!")

    except subprocess.CalledProcessError:
        print(
            "\n[bold red]SpotDL ERROR: A 'data.spotdl' file is corrupted. Delete the corrupted file and try again."
        )
    except KeyboardInterrupt:
        print("\n[bold red]Canceling...")
