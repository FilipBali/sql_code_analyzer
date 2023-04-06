#######################################
# File name: schema.py
# Purpose: Schema class represents database schema
#
# Key features:
#     Schema:
#        Stores: schema name,
#                tables related to schema,
#                connection to table database that belongs to

#        TODO: change schema name
#######################################

from __future__ import annotations

from sql_code_analyzer.in_memory_representation.struct.base import Base

from typing import TYPE_CHECKING

from sql_code_analyzer.output.reporter.base import ProgramReporter

if TYPE_CHECKING:
    from sql_code_analyzer.in_memory_representation.struct.database import Database


class Schema(Base):
    """
    TODO description
    """

    ###################################
    #              INIT
    ###################################
    def __init__(self,
                 database: Database,
                 schema_name: str):
        """
        TODO description
        :param database:
        :param schema_name:
        """
        self.name = schema_name
        self.tables: dict = {}
        self.database: Database = database
        self.__add_schema_to_database()

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, value):
        self._name = value

    @property
    def tables(self) -> dict:
        return self._tables

    @tables.setter
    def tables(self, value):
        self._tables = value

    @property
    def database(self) -> Database:
        return self._database

    @database.setter
    def database(self, value):
        self._database = value

    ##################################################
    #                  PRIVATE METHODS
    ##################################################
    #########################
    #          ADD
    #########################
    def __add_schema_to_database(self) -> None:
        """
        TODO description
        :return: None
        """
        if self.database.check_if_schema_exists_bool(self.name):
            ProgramReporter.show_error_message("Schema already exists")

        self.database.schemas[self.name] = self
        self.database.index_registration(key=self.name,
                                         reg_object=self)

    ##################################################
    #                  PUBLIC METHODS
    ##################################################
    #########################
    #         CHECKS
    #########################
    def check_if_table_exists(self, table) -> bool:
        """
        TODO description
        :param table:
        :return:
        """
        if not isinstance(table, str):
            table = table.name

        return self.check_if_exists(find_attr_val=table,
                                    struct=self.tables)

    #########################
    #         DELETE
    #########################
    def delete_schema(self) -> None:
        """
        TODO description
        :return: None
        """
        # TODO error ak je tabulka?
        del self.database.schemas[self.name]
        self.database.index_cancel_registration(key=self.name)
