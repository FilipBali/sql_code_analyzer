from __future__ import annotations

from sqlalchemy.sql.ddl import CreateTable, CreateIndex

from sql_code_analyzer.input.database_server.oracle.connect import make_connection

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from sqlalchemy import MetaData, create_engine


def generate_dll(engine: create_engine, meta: MetaData):
    """

    :param engine:
    :param meta:
    :return:
    """

    ddl = []
    for table in meta.sorted_tables:
        ddl.append(CreateTable(table).compile(engine))
        for index in table.indexes:
            ddl.append(CreateIndex(index).compile(engine))

    # TODO print if user wants
    ...
    return ddl


def oracle_handler(db_config):
    """
    Makes connection

    :param db_config:
    :return:
    """

    engine, meta = make_connection(db_config)
    return generate_dll(engine=engine, meta=meta)

