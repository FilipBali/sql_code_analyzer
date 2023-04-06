#######################################
# File name: table.py
# Purpose: Table class represents database table
#
# Key features:
#     Table:
#        Stores: table name
#                table columns
#                table level constrains(foreign key, check constrain etc.)
#                table primary key
#                connection to the schema that belongs to
#                connection to the database that belongs to
#
#        TODO: change table name, add constrain, delete constrain
#
#
#######################################

from __future__ import annotations

from sql_code_analyzer.in_memory_representation.struct.base import Base

from typing import TYPE_CHECKING

from sql_code_analyzer.output.reporter.base import ProgramReporter

if TYPE_CHECKING:
    from sql_code_analyzer.in_memory_representation.struct.constrain import PrimaryKey
    from sql_code_analyzer.in_memory_representation.struct.database import Database
    from sql_code_analyzer.in_memory_representation.struct.schema import Schema


class Table(Base):
    """
    TODO Table Description
    Description
    """

    ###################################
    #              INIT
    ###################################
    def __init__(self,
                 name: str,
                 schema: Schema,
                 database: Database,
                 node=None):
        """
        TODO description
        :param name:
        :param schema:
        :param database:
        """
        self.name: str = name
        self.schema: Schema = schema
        self.database: Database = database
        self.columns: dict = {}
        self.primary_key: PrimaryKey | None = None
        self.constrains: dict = {}

        self.args = {}
        if node is not None:
            for arg in node.args:
                if arg not in ["this", "kind","expressions"]:
                    self.args[arg] = node.args[arg]

        self.__add_table_to_schema()

    def __repr__(self):
        """
        TODO description
        :return:
        """
        return self.name

    ##################################################
    #                  PRIVATE METHODS
    ##################################################
    #########################
    #          ADD
    #########################
    def __add_table_to_schema(self) -> None:
        if self.schema.check_if_table_exists(table=self):
            ProgramReporter.show_error_message("Table already exists")

        self.schema.tables[self.name] = self
        self.schema.database.index_registration(key=(self.name, self.name),
                                                reg_object=self)

    ##################################################
    #                  PUBLIC METHODS
    ##################################################
    #########################
    #         CHECKS
    #########################
    def check_if_column_exists(self, column_name) -> bool:
        """
        TODO description check_if_column_exists
        :param column_name:
        :return:
        """

        return self.check_if_exists(find_attr_val=column_name,
                                    struct=self.columns)

    #########################
    #          ADD
    #########################
    def add_primary_key(self, primary_key: PrimaryKey) -> None:
        if self.primary_key is not None:
            ProgramReporter.show_error_message("Primary key already exists")

        self.primary_key = primary_key

    def delete_primary_key(self) -> None:
        self.primary_key = None

    #########################
    #         DELETE
    #########################
    def delete_table(self) -> None:
        """
        TODO Description
        :return:
        """

        if len(self.constrains) > 1:
            ProgramReporter.show_error_message("Table can NOT be deleted because of relations with another tables")

        self.database.index_cancel_registration(key=(self.schema.name, self.name))
        del self.schema.tables[self.name]
