from os import execv, path
from subprocess import check_call
from sys import argv
from sys import platform as sysplatform

FILE_EXT = ".exe" if sysplatform == "win32" else ""

def par2_executable():
    """
    Returns the path to the par2cmdline-turbo executable.
    """
    return path.join(  # noqa: PTH118
        path.dirname(__file__),  # noqa: PTH120
        "binaries",
        f"par2{FILE_EXT}"
    )


MESSAGE = (
    f"Running par2 via par2cmdline.py at {par2_executable()}"
)


def __call():
    """
    Binary entry point. Passes all command-line arguments to binary.
    """
    if sysplatform == "win32":
        # execvp broken on Windows, use subprocess instead to not launch a new shell
        print(f"\033[95m{MESSAGE}\033[0m")
        check_call([par2_executable(), *argv[1:]])
    else:
        print(f"\033[95m{MESSAGE}\033[0m")
        execv(par2_executable(), ["par2", *argv[1:]])
