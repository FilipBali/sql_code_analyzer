import argparse
import os
from operator import methodcaller
from pathlib import Path
from sys import stdin
import re

from sql_code_analyzer.input.database_server.base import database_connection_handler
from sql_code_analyzer.input.database_server.config import DBConfig
from sql_code_analyzer.output import enums
from sql_code_analyzer.output.reporter.base import OutputType
from sql_code_analyzer.output.reporter.program_reporter import ProgramReporter
from sql_code_analyzer.output.terminator.base import Terminator
from sql_code_analyzer.tools.path import get_program_root_path, get_absolute_path, verify_path_access, \
    verify_path_exists
from test_cases.sqlglot.tester import run_tests


class CArgs:
    """
    Instance from CArgs class contains all data comes as input of program.

    Provides:
        Program arguments parsing and processing and interface to obtain these data.
        Help a message where parameters are described in detail.
        Features retrieve SQL input from file/standard input/database server.
        Possibility to create configuration template for proper database connection.
        Create statements from raw SQL file

    """

    def __init__(self):

        self.show_dll = False
        self.database_statements = []
        self.dialect: str = ""
        self.file: str | Path = ""
        self.tests: bool = False
        self.raw_sql: str = ""
        self.statements: list = []
        self.rules_path: str = ""
        self.include_folders: list = []
        self.exclude_folders: list = []
        self.serialization_path: str | None = None
        self.deserialization_path: str | None = None
        self.connection_file_create: bool = False
        self.connection_file_option: str = "Default"
        self.connection_file_path: str | None = None
        self.db_config = None
        self.report_output_nothing = None
        self.report_output_file = None

        args = parse_args()

        if args.verbose:
            ProgramReporter.verbose = True

        # If file path sets, then verify its correctness
        verify_file_path(self, args)

        # Run tests
        if self.tests:
            run_tests()
            Terminator.exit(enums.ExitWith.Success)

        # Create database connection file template
        if self.connection_file_create:
            self.create_database_connection_file()
            Terminator.exit(enums.ExitWith.Success)

        if self.report_output_nothing:
            if self.report_output_file:
                ProgramReporter.show_error_message(
                    message="Parameters --report-output-nothing and --report-output-file are mutually exclusive."
                )

            ProgramReporter.report_output = OutputType.NoReport

        if self.report_output_file:
            if self.report_output_nothing:
                ProgramReporter.show_error_message(
                    message="Parameters --report-output-nothing and --report-output-file are mutually exclusive."
                )
            ProgramReporter.report_output = OutputType.File
            ProgramReporter.report_output_file = get_absolute_path(path=self.report_output_file)
            verify_path_exists(path=ProgramReporter.report_output_file)
            verify_path_access(path=ProgramReporter.report_output_file)

        if self.connection_file_path and self.deserialization_path:
            ProgramReporter.show_error_message(
                message="Attributes --connection_file_path and --deserialization-path are mutually exclusive.\n"
                        "It possible to load memory representation either from serialized file or database server."
            )

        if self.connection_file_path:
            # load from an existing database
            self.db_config = DBConfig(path=get_absolute_path(path=self.connection_file_path),
                                      option=self.connection_file_option)

            database_connection_handler(args=self)

        self.db_config = None
        if self.file:
            # load sql from file
            with open(self.file, 'r') as file:
                self.raw_sql = file.read()

            parse_raw_sql_to_statement(self)

        else:
            # check stdin
            print("Enter target SQL:")
            self.raw_sql = stdin.read()
            parse_raw_sql_to_statement(self)

        if self.serialization_path is not None:
            self.serialization_path = get_absolute_path(path=self.serialization_path)
            verify_path_exists(path=self.serialization_path)
            verify_path_access(path=self.serialization_path)

        if self.deserialization_path is not None:
            self.deserialization_path = get_absolute_path(path=self.deserialization_path)
            verify_path_exists(path=self.deserialization_path)
            verify_path_access(path=self.deserialization_path)

        if self.rules_path != os.path.join(get_program_root_path(), "checker", "rules"):
            self.rules_path = get_absolute_path(path=self.rules_path)
            verify_path_exists(path=self.rules_path)
            verify_path_access(path=self.rules_path)

    def update_parameters(self, args: argparse) -> None:
        """
        Dynamically creates/updates self object properties
        :param args: Data that need to be saved to self-object
        :return: None
        """

        for argument, value in vars(args).items():
            setattr(self, argument, value)

    @staticmethod
    def create_database_connection_file() -> None:
        """
        Create a template file as an example for proper database connection.
        :return: None
        """

        root_path = get_program_root_path()

        f = open(os.path.join(root_path, "db_connection.cfg"), "w")
        f.write(
            "##################################################################\n"
            "#############    THIS FILE CONTAINS CONFIGURATION    #############\n"
            "##################################################################\n"
            "# \n"
            "# This file is a configuration template for connecting the program\n".upper() +
            "# to an existing database. Please replace the words containing\n".upper() +
            "# the underscore with the data that corresponds to connecting \n".upper() +
            "# the client to the database.\n".upper() +
            "# \n"
            "# In this file you can create comments using the grid wildcard (#)\n".upper() +
            "# which will cause all content after it on a given line to be \n".upper() +
            "# ignored by the program.\n".upper() +
            "#\n"            
            "# Here is an example of use:\n"
            "#\n"
            "# DIALECT = oracle # enter database dialect\n"
            "# USERNAME = MyName  # enter your username\n"
            "# PASSWORD = An4q6Db458d1w2r8  # enter your password\n"
            "# HOST = localhost  # enter host url (for example localhost)\n"
            "# PORT = 1521  # enter the port number\n"
            "# SERVICE =  orcl.mshome.net  # enter the database service name\n"
            "\n"
            "\n"
            "DIALECT = target_dialect # enter database dialect\n"
            "USERNAME = your_username  # enter your username\n"
            "PASSWORD = your_password  # enter your password\n"
            "HOST = target_host  # enter host url (for example localhost)\n"
            "PORT = target_port_number  # enter the port number\n"
            "SERVICE =  target_service  # enter the database service name\n"
        )
        f.close()


def parse_raw_sql_to_statement(args_data) -> None:
    """
    Implements algorithm to detect a statement from raw input file.
    Statements are stored as items in a list.
    If appropriate, stand alone comments blocks are deleted.
    Statements are detected by statement's terminating character ";"

    :param args_data: Arguments data
    :return: None
    """

    raw = args_data.raw_sql

    # match two or more lines
    regex = r"(?:\r?\n){2,}"
    statements = re.split(regex, raw.strip())
    # call lstrip method on every single statement
    statements = list(map(methodcaller("lstrip"), statements))

    def delete_comment_blocks():
        regex = r"(?:\r?\n){1,}"
        to_remove = []

        #####################################################################
        # Find and delete all comment blocks
        # Reason: SQLGLot ends up with an error when it only parses comments
        #####################################################################
        for statement in statements:
            stmt_split_by_line = re.split(regex, statement.strip())
            stmt_split_by_line = list(map(methodcaller("lstrip"), stmt_split_by_line))

            remove_statement = True
            for statement_part in stmt_split_by_line:
                # statement_part
                if not (remove_statement and statement_part.startswith("--")):
                    remove_statement = False
                    break

            if remove_statement:
                to_remove.append(statement)

        for comment_block in to_remove:
            statements.remove(comment_block)

    # Delete comments block
    delete_comment_blocks()

    # Split statements
    statement_delimiter = ";"

    t_statements = []
    append_to_new_line = False
    for statement in statements:
        if len(t_statements) == 0:
            t_statements.append(statement)
            continue

        if append_to_new_line:
            t_statements.append(statement)
            append_to_new_line = False
            continue

        t_statements[-1] += statement

        if statement_delimiter in statement:
            append_to_new_line = True

    statements = t_statements

    # statements = ' '.join(statements).split(statement_delimiter)
    t_statements = []
    for statement in statements:
        t_statements += statement.split(statement_delimiter)

    statements = t_statements
    statements = [statement + statement_delimiter for statement in statements if statement != ""]

    # Delete comments block again
    # There can be again because of a statement split by delimiter ;
    delete_comment_blocks()

    keep_statements = []
    for statement in statements:
        statement_list = statement.splitlines()
        statement_list_tmp = list(map(methodcaller("lstrip"), statement_list))
        for index, line in enumerate(statement_list_tmp):
            if len(line) == 1:
                keep_statements.append(statement_list)
                break
            if len(line) > 1:
                if line[0:2] != "--":
                    statement_with_code = statement_list[index:]
                    keep_statements.append('\n'.join(statement_with_code))
                    break

    args_data.statements += keep_statements


def parse_args() -> argparse:
    """
    Parse program arguments using Argparse library
    :return: Argparse object
    """

    parser = argparse.ArgumentParser()
    parser.add_argument("-t", "--tests",
                        action='store_true',
                        required=False,
                        help="Run tests.",
                        default=None)

    parser.add_argument("-d", "--dialect",
                        metavar="",
                        required=False,
                        help="Expect target dialect.",
                        default=None)

    parser.add_argument("-f", "--file",
                        type=str,
                        metavar="",
                        required=False,
                        help="Expect file with target SQL, "
                             "if this parameter is not present "
                             "then the program expects it on standard input.",
                        default=None)

    parser.add_argument("-cfc", "--connection-file-create",
                        action='store_true',
                        required=False,
                        help="Create template file for database connection.",
                        default=None)

    parser.add_argument("-cfo", "--connection-file-option",
                        required=False,
                        type=str,
                        help="Specify option in config file. Config file may contain several configurations "
                             "which can be selected by this parameter. Default value is \"Default\"",
                        default="Default")

    parser.add_argument("-cfp", "--connection-file-path",
                        required=False,
                        type=str,
                        help="Path where is expected to be a file with data for database connection.",
                        default=None)

    parser.add_argument("-sp", "--serialization-path",
                        required=False,
                        type=str,
                        help="If set, program provides backup of result memory representation"
                             " and saves it to that path.",
                        default=None)

    parser.add_argument("-dp", "--deserialization-path",
                        required=False,
                        type=str,
                        help="If set, program loads a memory representation and initialise memory representation "
                             "from it at the beginning",
                        default=None)

    parser.add_argument("-rp", "--rules-path",
                        type=str,
                        required=False,
                        help="Specify folder with rules. If not set then default is "
                             "..\\sql_code_analyzer\\checker\\rules",
                        default=os.path.join(get_program_root_path(), "checker", "rules"))

    parser.add_argument("-if", "--include-folders",
                        nargs='+',
                        type=str,
                        required=False,
                        help="Specify folder names with rules which should be included in rules path. "
                             "Parameters --include-folders and --exclude-folders "
                             "are mutually exclusive and only one of them can be set. "
                             "Accepted format: -if folder1 folder2 folderN",
                        default=[])

    parser.add_argument("-ef", "--exclude-folders",
                        nargs='+',
                        type=str,
                        required=False,
                        help="Specify folder names with rules which should NOT be included in rules path. "
                             "Parameters --include-folders and --exclude-folders "
                             "are mutually exclusive and only one of them can be set. "
                             "Accepted format: -ef folder1 folder2 folderN",
                        default=[])

    parser.add_argument("-rof", "--report-output-file",
                        type=str,
                        metavar="",
                        required=False,
                        help="If set, expects path where program will store reports. "
                             "Mutually exclusive with parameter --report-output-nothing",
                        default=None)

    parser.add_argument("-ron", "--report-output-nothing",
                        action='store_true',
                        required=False,
                        help="If set, program will no store reports. "
                             "Mutually exclusive with parameter --report-output-file",
                        default=None)

    parser.add_argument("-v", "--verbose",
                        action='store_true',
                        required=False,
                        help="If set, program show information messages on standard input.",
                        default=None)

    args = parser.parse_args()
    return args


def verify_file_path(self, args: argparse) -> None:
    """
    Process and verify if the file exists.
    The arguments of the program need to be verified before they are used.
    If the user makes a mistake and sets a path that is not correct,
    for example, it is not a file, the program will detect this
    and give the user the opportunity to correct the path
    or choose to exit the program.

    :return: None
    """

    err_user_answer = False

    if args.file is not None:

        self.file = get_absolute_path(path=args.file)
        while 1:
            if not self.file.is_file():

                if err_user_answer:
                    user_answer = input("\nPlease answer only [yes/no] or in short way [y/n]\n"
                                        "Do you want set another path? [y/n]\n")
                else:
                    user_answer = input("\nFile not exits!\n"
                                        "Do you want set another path? [y/n]\n")

                if user_answer.lower() == "n" or user_answer.lower() == "no":
                    Terminator.exit(enums.ExitWith.Success)

                elif user_answer.lower() == "y" or user_answer.lower() == "yes":
                    args.file = input("Write down new path:\n")
                    err_user_answer = False
                    continue

                else:
                    err_user_answer = True

            else:
                break

    # If the file is None, then the program will be asking for SQL code through standard input

    # All args will be synchronized with "self" object.
    # But self.file now contains a Path version of a file path, not a string one.
    # So self.file needs to be passed to args.file otherwise self.file will be overwritten by old string input.

    args.file = self.file
    self.update_parameters(args=args)
