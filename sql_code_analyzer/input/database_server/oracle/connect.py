from __future__ import annotations

from typing import TYPE_CHECKING
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

    print("Connecting to " + dialect.lower() + " database..")
    print("Using connection string: " + connection_string)

    engine = create_engine(connection_string)

    print("Connection succeed.")
    print("Generating DDL script..")

    meta = MetaData()
    meta.reflect(bind=engine)

    return engine, meta
