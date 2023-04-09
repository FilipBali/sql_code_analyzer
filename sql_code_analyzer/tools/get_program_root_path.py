import sys


def get_program_root_path() -> str:
    """
    Provides a path to program root folder.
    :return: Path to program root folder
    """

    return sys.path[0]
