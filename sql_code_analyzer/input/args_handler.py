import argparse
from dataclasses import dataclass, field
from operator import methodcaller
from pathlib import Path
from sys import stdin
import re

from test_cases.sqlglot.tester import run_tests


class CArgs:
    """
    TODO description
    """

    def __init__(self):
        args = parse_args()
        process_args(self, args)

        # run tests
        if self.tests:
            run_tests()
            exit(0)

        if self.file:
            # load sql from file
            with open(self.file, 'r') as file:
                self.raw_sql = file.read()

        else:
            # check stdin
            print("Enter target SQL:")
            self.raw_sql = stdin.read()

        parse_raw_sql_to_statement(self)

    dialect: str = ""
    file: str = ""
    tests: bool = False
    raw_sql: str = ""
    statements:  list = []
    path_to_rules_folder: str = None
    include_folders: list = []
    exclude_folders: list = []


def parse_raw_sql_to_statement(args_data):
    """
    TODO description
    :param args_data:
    :return:
    """
    raw = args_data.raw_sql

    # match two or more lines
    regex = r"(?:\r?\n){2,}"
    statements = re.split(regex, raw.strip())
    # call lstrip method on every single statement
    statements = list(map(methodcaller("lstrip"), statements))

    regex = r"(?:\r?\n){1,}"
    to_remove = []

    #####################################################################
    # Find and delete all blocks of comments
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

    delimited_statements = []
    d = ";"
    for statement in statements:
        delimited_statements.append([e + d for e in statement.split(d) if e])

    statements = [item for sublist in delimited_statements for item in sublist]

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

    args_data.statements = keep_statements


def parse_args() -> argparse:
    """
    TODO description
    :return:
    """
    parser = argparse.ArgumentParser()
    # parser.add_argument("-h", "--help", metavar="", help="Show help message.")
    parser.add_argument("-t", "--tests",
                        action='store_true',
                        required=False,
                        help="Run tests.")

    parser.add_argument("-p", "--rules-path",
                        type=str,
                        required=False,
                        help="Specify folder with rules. If not set then default is "
                             "..\\sql_code_analyzer\\checker\\rules",
                        default=None)

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

    parser.add_argument("-d", "--dialect",
                        metavar="",
                        required=False,
                        help="Expect target dialect.")

    parser.add_argument("-f", "--file",
                        type=str,
                        metavar="",
                        required=False,
                        help="Expect file with target SQL, "
                             "if this parameter is not present "
                             "then the program expects it on standard input.")

    args = parser.parse_args()
    return args


def get_sql_from_source(file):
    """
    TODO description
    :param file:
    :return:
    """
    if file:
        # load sql from file
        with open(file, 'r') as rfile:
            return rfile.read()

    else:
        # check stdin
        print("Enter target SQL:")
        return stdin.read()


def process_args(self, args: argparse):
    """
    TODO description
    :return:
    """

    err_user_answer = False
    if args.file is not None:
        while 1:
            path = Path(args.file)
            if not path.is_file():

                if err_user_answer:
                    user_answer = input("\nPlease answer only [yes/no] or in short way [y/n]\n"
                                        "Do you want set another path? [y/n]\n")
                else:
                    user_answer = input("\nFile not exits!\n"
                                     "Do you want set another path? [y/n]\n")

                if user_answer.lower() == "n" or user_answer.lower() == "no":
                    exit(0)

                elif user_answer.lower() == "y" or user_answer.lower() == "yes":
                    args.file = input("Write down new path:\n")
                    err_user_answer = False
                    continue

                else:
                    err_user_answer = True

            else:
                break

    self.dialect = args.dialect
    self.file = args.file
    self.tests = args.tests
    self.raw_sql = get_sql_from_source(args.file)
    self.path_to_rules_folder = args.rules_path
    self.include_folders = args.include_folders
    self.exclude_folders = args.exclude_folders
