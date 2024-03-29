from __future__ import annotations

from typing import TYPE_CHECKING

from sql_code_analyzer.output.reporter.program_reporter import ProgramReporter

if TYPE_CHECKING:
    from sql_code_analyzer.input.database_server.config import DBConfig


def make_connection(db_config: DBConfig):
    """
    Makes connection with a database with the entered login details.
    :param db_config: Login details
    :return: Engine and MetaData obtained after connection to a database.
    """

    # do import here if necessary
    #
    from sqlalchemy import create_engine, MetaData

    sql_driver = {
        "oracle": "cx_oracle",
        "postgresql": "",
        "mysql": "",
        "mssql": ""
    }

    dialect = db_config.dialect
    sql_driver = sql_driver[dialect]
    username = db_config.username
    password = db_config.password
    host = db_config.host
    port = db_config.port
    service = db_config.service

    database_specific = dialect + '+' + sql_driver
    user_credential = '://' + username + ':' + password
    database_home = '@' + host + ':' + str(port) + '/?service_name=' + service

    connection_string = database_specific + user_credential + database_home

    ProgramReporter.show_verbose_messages(message="Connecting to " + dialect.lower() + " database..")
    ProgramReporter.show_verbose_messages(message="Using connection string: " + connection_string)

    engine = create_engine(connection_string)

    ProgramReporter.show_verbose_messages(message="Connection succeed.")
    ProgramReporter.show_verbose_messages(message="Generating DDL script..")

    meta = MetaData()
    meta.reflect(bind=engine)

    return engine, meta
