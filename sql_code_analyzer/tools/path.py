import os
import sys
from pathlib import Path


def get_program_root_path() -> Path:
    """
    Provides a path to program root folder.
    :return: Path to program root folder
    """

    return Path(sys.path[0])


def get_absolute_path(path: str) -> Path:
    """
    Determines if the path is already absolute
    If yes, then it returns
    If no then we assume that the path must start with the root path of the program

    :return: Absolute path
    """

    if not Path(path).is_absolute():
        root_path = get_program_root_path()
        path = root_path / path

    return path
