from pathlib import Path
from rich import print
import subprocess


def get_directories_with_file(file_name):
    cwd = Path(__file__).resolve().parent
    directories = [path.parent.name for path in cwd.glob("**/" + file_name)]

    if not directories:
        raise FileNotFoundError()

    return directories


def list_directories(directories):
    for index, directory in enumerate(directories, start=1):
        print(f"[bold magenta]{index}.[/] [bright_blue]{directory}[/]")


def select_directory(directories):
    try:
        print(
            "\n[bold italic cyan]Choose a directory to sync [blue](1-"
            + str(len(directories))
            + ")[/]"
        )
        choice = input(">> ")

        if choice.lower() == "q":
            raise SystemExit()

        index = int(choice)
        if 1 <= index <= len(directories):
            dir = directories[index - 1]
            execute_file(dir)
        else:
            raise ValueError()
    except (ValueError, KeyboardInterrupt, subprocess.CalledProcessError):
        raise


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
        directories = get_directories_with_file("data.spotdl")
        list_directories(directories)
        select_directory(directories)

        print("\n[bold cyan]Sync completed!")

    except FileNotFoundError:
        print(
            '\n[bold red]ERROR: file "data.spotdl" not found in any directory. Create a new playlist and try again.'
        )
    except ValueError:
        print("\n[bold red]Invalid choice. Please enter a valid number.")
    except subprocess.CalledProcessError:
        print(
            "\n[bold red]SpotDL ERROR: A 'data.spotdl' file is corrupted. Delete the corrupted file and try again."
        )
    except KeyboardInterrupt:
        print("\n[bold red]Canceling...")
    except SystemExit:
        pass
