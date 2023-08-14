#######################################
# File name: schema.py
# Purpose: Schema class represents database schema
#
# Key features:
#     Schema:
#        Stores: schema name,
#                tables related to schema,
#                connection to a table database that belongs to
#
#######################################

from __future__ import annotations

from sql_code_analyzer.in_memory_representation.struct.base import Base

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from sql_code_analyzer.in_memory_representation.struct.database import Database


class Schema(Base):
    """
    Represents table schema in memory representation
    """

    ###################################
    #              INIT
    ###################################
    def __init__(self,
                 database: Database,
                 schema_name: str):
        """
        :param database: The database to which the schema belongs
        :param schema_name: The schema name
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
        Adds schema to a database in memory representation
        :return: None
        """

        if self.database.check_if_schema_exists_bool(self.name):
            self._rule_reporter.add_memory_representation_report(
                message=f"Schema {self.name} already exists."
            )
            return

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
        Check if target table exists in schema
        :param table: The table instance or its name
        :return: True/False
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
        Delete schema from memory representation
        :return: None
        """

        del self.database.schemas[self.name]
        self.database.index_cancel_registration(key=self.name)

    #########################
    #         API
    #########################

    ################
    #     GET
    ################

    def get_table_count(self) -> int:
        """
        # Return count of tables which are belonged to this schema
        :return: Count of tables
        """

        return len(self.tables)

    ################
    #    VERIFY
    ################

    def verify_name(self, expected_name) -> bool:
        """
        Return True if schema has this name otherwise False
        :param expected_name: The name
        :return: True/False
        """

        return self.name == expected_name

    def verify_table_count(self, expected_count) -> bool:
        """
        Return True if schema has this count of constrains otherwise False
        :param expected_count: Expected count
        :return: True/False
        """

        return len(self.tables) == expected_count
