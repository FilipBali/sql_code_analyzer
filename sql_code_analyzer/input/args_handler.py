import argparse
import os
import unittest
from pathlib import Path
from sys import stdin
import re

from sql_code_analyzer.input.database_server.base import database_connection_handler
from sql_code_analyzer.input.database_server.config import DBConfig
from sql_code_analyzer.output import enums
from sql_code_analyzer.output.reporter.base import OutputType, Reporter
from sql_code_analyzer.output.reporter.program_reporter import ProgramReporter
from sql_code_analyzer.output.terminator.base import Terminator
from sql_code_analyzer.tools.path import get_program_root_path, get_absolute_path, verify_path_access, \
    verify_path_exists, create_path_if_not_exists, ProgramPathConfig


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

        self.serialization_file: str | None = None
        self.serialization_path: str | None = None
        self.deserialization_file: str | None = None
        self.deserialization_path: str | None = None

        self.connection_file_create: bool = False
        self.connection_file_option: str | None = None
        self.connection_file: str | None = None
        self.connection_file_path: str | None = None

        self.db_config = None
        self.report_output_silent = None
        self.report_output_file = None

        args = parse_args()

        # If file path sets, then verify its correctness
        verify_file_path(self, args)

        ################################
        #        PROGRAM OUTPUT
        ################################
        ProgramReporter.verbose = args.verbose

        if self.report_output_silent and args.verbose:
            ProgramReporter.show_warning_message(
                message="The output on the program is set to silent(--report-output-silent). "
                        "Using the verbose parameter does not make sense."
            )

        if self.report_output_silent and self.report_output_file:
            ProgramReporter.show_error_message(
                message="Parameters --report-output-silent and --report-output-file are mutually exclusive."
            )

        if self.report_output_silent:
            Reporter.report_output = OutputType.Silent

        if self.report_output_file:

            # If an output file path is None, then use the default one
            # This also creates necessary folders!
            # if self.report_output_file is None:
            #     self.report_output_file = create_path_if_not_exists(
            #                 path=get_program_default_output_path() / self.report_output_file)

            Reporter.set_output_file(
                path=ProgramPathConfig.get_program_output_path() / self.report_output_file
            )

            # Reporter.report_output = OutputType.File

            # Reporter.report_output_file = get_program_default_output_path() / self.report_output_file
            # verify_path_exists(path=ProgramReporter.report_output_file)
            # verify_path_access(path=ProgramReporter.report_output_file)

        ################################
        #            TESTS
        ################################
        # Run tests
        if self.tests:
            import tests.tester
            test_suite = unittest.TestLoader().loadTestsFromModule(tests.tester)
            # buffer=True => Suppress program error messages
            unittest.TextTestRunner(buffer=True).run(test_suite)
            Terminator.exit(enums.ExitWith.Success)

        ################################
        #           DATABASE
        ################################
        # Create database connection file template
        if self.connection_file_create:
            self.create_database_connection_file()
            Terminator.exit(enums.ExitWith.Success)

        if self.connection_file_path is not None and self.deserialization_file is not None:
            ProgramReporter.show_error_message(
                message="Attributes --connection_file_path and --deserialization-file are mutually exclusive.\n"
                        "It possible to load memory representation either from serialized file or database server."
            )

        # If is section set, then its activates a database connection feature
        if self.connection_file_option is not None:

            # If a connection file path is None, then use the default one
            # This also creates necessary folders!
            if self.connection_file_path is None:
                self.connection_file_path = ProgramPathConfig.get_database_configuration_path()

            # load from an existing database
            self.db_config = DBConfig(path=get_absolute_path(path=self.connection_file_path),
                                      file=self.connection_file,
                                      option=self.connection_file_option)

            database_connection_handler(args=self)

        ################################
        #            INPUT
        ################################
        # Get SQL from file or standard input
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

        ################################
        #         SERIALIZATION
        ################################
        # If serialization file is set, the then program provides serialization
        if self.serialization_file is not None:

            # If a serialization path is None, then use the default one
            # This also creates necessary folders!
            if self.serialization_path is None:
                self.serialization_path = create_path_if_not_exists(
                            path=ProgramPathConfig.get_program_backup_path())

            # Make sure the path is absolute
            self.serialization_path = get_absolute_path(path=self.serialization_path)

            # Verify path
            verify_path_exists(path=self.serialization_path)
            verify_path_access(path=self.serialization_path)

        # If serialization file is set, the then program provides deserialization
        if self.deserialization_file is not None:

            # If a deserialization path is None, then use the default one
            # This also creates necessary folders!
            if self.deserialization_path is None:
                self.deserialization_path = create_path_if_not_exists(
                    path=ProgramPathConfig.get_program_backup_path())

            # Make sure the path is absolute
            self.deserialization_path = get_absolute_path(path=self.deserialization_path)

            # Verify path
            verify_path_exists(path=self.deserialization_path / self.deserialization_file)
            verify_path_access(path=self.deserialization_path / self.deserialization_file)

        ################################
        #            RULES
        ################################
        # If a rule path is not default, then process the user-defined path
        if self.rules_path != os.path.join(get_program_root_path(), "checker", "rules"):

            # Make sure the path is absolute
            self.rules_path = get_absolute_path(path=self.rules_path)

            # Verify path
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

        root_path = create_path_if_not_exists(
            path=ProgramPathConfig.get_database_configuration_path()
        )

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
        
        print("The configuration template has been successfully created.\n"
              f"Path: {root_path}\n"
              f"File: db_connection.cfg")


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

    # Delete everything between /* and */ but keeps newlines
    raw = re.sub(r'/\*.*?\*/', lambda x: x.group().count('\n') * '\n', raw, flags=re.DOTALL)

    # Delete everything between -- and newline but keeps newline
    raw = re.sub(r'--.*?\n', '\n', raw)

    lines = raw.split("\n")
    result = ""
    for i, line in enumerate(lines):
        result += line + " -- " + str(i + 1) + "\n"

    lines = result.split("\n")
    result = []
    temp = ""
    for line in lines:
        if ";" in line:
            temp += line + "\n"
            result.append(temp)
            temp = ""
        else:
            temp += line + "\n"

    for index, statement in enumerate(result):
        lines = statement.split("\n")
        tmp = ""
        for line in lines:
            if line.lstrip().find("--") > 0:
                tmp += line + "\n"
        result[index] = tmp

    lines = result
    result = []
    for line in lines:
        index = int(line.split("--")[1].split("\n")[0])
        result.append((line, index))

    args_data.statements += result


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

    ############################
    #         DATABASE
    ############################
    parser.add_argument("-cfc", "--connection-file-create",
                        action='store_true',
                        required=False,
                        help="Create template file for database connection.",
                        default=None)

    # Activates database-connection feature
    parser.add_argument("-cfo", "--connection-file-option",
                        required=False,
                        type=str,
                        help="Specify section in config file. Config file may contain several configurations "
                             "which can be selected by this parameter.",
                        default=None)

    parser.add_argument("-cf", "--connection-file",
                        required=False,
                        type=str,
                        help="Name of file where is expected to be a data for database connection.",
                        default="db_connection.cfg")

    parser.add_argument("-cfp", "--connection-file-path",
                        required=False,
                        type=str,
                        help="Path where is expected to be a file with data for database connection.",
                        default=None)

    ############################
    #       SERIALIZATION
    ############################
    # Activates serialization feature
    parser.add_argument("-sf", "--serialization-file",
                        required=False,
                        type=str,
                        help="If set, the program will provide a backup representation of the results in memory "
                             "to a file with the specified name and save them to selected/default path.",
                        default=None)

    # The default value will be set later
    # This avoids unnecessary directory creation for output.
    parser.add_argument("-sp", "--serialization-path",
                        required=False,
                        type=str,
                        help="If specified, then the serialization path will be changed to the specified path.",
                        default=None)

    # Activates deserialization feature
    parser.add_argument("-df", "--deserialization-file",
                        required=False,
                        type=str,
                        help="If set, the program reads the memory representation and initializes it "
                             "from a file with the specified name on the selected/default path.",
                        default=None)

    # The default value will be set later
    # This avoids unnecessary directory creation for output.
    parser.add_argument("-dp", "--deserialization-path",
                        required=False,
                        type=str,
                        help="If specified, then the deserialization path will be changed to the specified path.",
                        default=None)

    ############################
    #           RULES
    ############################
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

    ############################
    #          REPORT
    ############################
    parser.add_argument("-ros", "--report-output-silent",
                        action='store_true',
                        required=False,
                        help="If set, program will no store reports. "
                             "Mutually exclusive with parameter --report-output-file",
                        default=None)

    parser.add_argument("-rof", "--report-output-file",
                        type=str,
                        metavar="",
                        required=False,
                        help="If set, expects path where program will store reports."
                             ""
                             "Mutually exclusive with parameter --report-output-silent",
                        default=None)

    parser.add_argument("-v", "--verbose",
                        action='count',
                        required=False,
                        help="If set, program show information messages on standard input.",
                        default=0)

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
