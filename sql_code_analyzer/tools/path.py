import os
import sys
from pathlib import Path

from sql_code_analyzer.output.reporter.program_reporter import ProgramReporter


class ProgramPathConfig:
    output_folder = "_output"
    program_configuration = "program_configuration"
    database_configuration = "database_config"
    backup = "mem_rep_backup"

    @staticmethod
    def get_program_output_path() -> Path:
        return get_program_root_path() / ProgramPathConfig.output_folder

    @staticmethod
    def get_program_backup_path() -> Path:
        return ProgramPathConfig.get_program_output_path() / ProgramPathConfig.backup

    @staticmethod
    def get_program_configuration_path() -> Path:
        return get_program_root_path() / ProgramPathConfig.program_configuration

    @staticmethod
    def get_database_configuration_path() -> Path:
        return ProgramPathConfig.get_program_configuration_path() / ProgramPathConfig.database_configuration


def get_program_root_path() -> Path:
    """
    Provides a path to program root folder.
    :return: Path to program root folder
    """

    return Path(sys.path[0])


def create_path_if_not_exists(path: Path) -> Path:
    if not path.exists():
        try:
            path.mkdir(parents=True)
        except (Exception, ) as e:
            ProgramReporter.show_error_message(
                message=f"Program probably does not have the rights to create folders or files!\nPath: {str(path)}"
                        f"Python interpreter report: {e}"
            )

    return path


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
            message=f"The path not exists!\nPath: {str(path)}"
        )


def verify_path_access(path: Path):

    if not os.access(str(path), os.W_OK):
        ProgramReporter.show_error_message(
            message=f"Program does not have the access to path folders or files!\nPath: {str(path)}"
        )


def get_path_object(path: str):
    return Path(path)
