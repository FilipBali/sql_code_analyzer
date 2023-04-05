from __future__ import annotations

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from sql_code_analyzer.input.database_server.config import DBConfig


def make_connection(db_config: DBConfig):
    # do import if necessary
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

    connection_string = dialect + '+' + sql_driver + \
                        '://' + username + ':' + password + '@' + host + ':' + str(port) + \
                        '/?service_name=' + service

    print("Connecting to " + dialect.lower() + " database..")
    print("Using connection string: " + connection_string)

    engine = create_engine(connection_string)

    print("Connection succeed.")
    print("Generating DDL script..")

    meta = MetaData()
    meta.reflect(bind=engine)

    return engine, meta
