#######################################
# File name: schema.py
# Author: Filip Bali
# Purpose: Schema class represents database schema
#
# Key features:
#     Schema:
#        Stores: schema name, tables, related database
#
#        Methods:
#           Private:
#               __add_schema_to_database(self) -> None
#
#           Public:
#               check_if_table_exists(self, table) -> bool
#
#               delete_schema(self) -> None
#
#
#        TODO: change schema name
#
#
#######################################

from __future__ import annotations

from sql_code_analyzer.in_memory_representation.struct.base import Base

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from sql_code_analyzer.in_memory_representation.struct.database import Database


class Schema(Base):
    """
    TODO description
    """

    ###################################
    #          CLASS PROPERTIES
    ###################################
    name: str = ""
    tables: dict = {}
    database: Database = None

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
        self.tables = {}
        self.database = database
        self.__add_schema_to_database()

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
            raise "Error: schema already exists"

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
