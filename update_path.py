import sys
from pathlib import Path


def sys_path_update() -> None:
    # update path to find local imports
    posix_path = Path.cwd().as_posix()
    sys.path.insert(0, posix_path)
