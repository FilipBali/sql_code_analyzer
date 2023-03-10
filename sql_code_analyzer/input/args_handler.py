import argparse
from dataclasses import dataclass, field
from operator import methodcaller
from pathlib import Path
from sys import stdin
import re

from test_cases.sqlglot.tester import run_tests


@dataclass
class CArgs:
    """
    TODO description
    """
    dialect: str = ""
    file: str = ""
    tests: bool = False
    raw_sql: str = ""
    statements:  list = field(default_factory=list)


def manager_args() -> CArgs:
    """
    TODO description
    :return:
    """
    # get program args
    args = parse_args()
    args_data = process_args(args)

    # run tests
    if args_data.tests:
        run_tests()
        exit(0)

    if args_data.file:
        # load sql from file

        with open(args_data.file, 'r') as file:
            args_data.raw_sql = file.read()

    else:
        # check stdin
        print("Enter target SQL:")
        args_data.raw_sql = stdin.read()

    parse_raw_sql_to_statement(args_data)

    return args_data


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


def process_args(args: argparse) -> CArgs:
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

    return CArgs(
        dialect=args.dialect,
        file=args.file,
        tests=args.tests,
        raw_sql=get_sql_from_source(args.file),
    )
