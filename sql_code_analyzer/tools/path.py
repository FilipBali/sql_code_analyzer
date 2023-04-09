import os
import sys
from pathlib import Path

from sql_code_analyzer.output.reporter.base import ProgramReporter


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

    path = Path(path)
    if not path.is_absolute():
        root_path = get_program_root_path()
        path = root_path / path

    return path


def verify_path_exists(path: Path):

    if not path.exists():
        ProgramReporter.show_error_message(
            message="The path not exists!\nPath: " + str(path)
        )


def verify_path_access(path: Path):

    if not os.access(str(path), os.W_OK):
        ProgramReporter.show_error_message(
            message="Program does not have the access to path folders or files!\nPath: " + str(path)
        )
