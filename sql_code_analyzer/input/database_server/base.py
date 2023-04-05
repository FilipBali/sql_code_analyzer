from __future__ import annotations

from sql_code_analyzer.input.database_server.oracle.base import oracle_handler

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from sql_code_analyzer.input.args_handler import CArgs


def parse_dll_to_statements(args: CArgs, ddl: list):
    for ddl_item in ddl:
        args.statements.append(ddl_item.string)


def database_connection_handler(args: CArgs):

    match args.connection_file_option.lower():
        case "oracle":
            ddl = oracle_handler(args.db_config)
            parse_dll_to_statements(args, ddl)

        case "postgresql":
            # import psycopg2
            ...
        case "mysql":
            # import pymysql
            ...
        case "mssql":
            # pip install pyodbc
            ...
