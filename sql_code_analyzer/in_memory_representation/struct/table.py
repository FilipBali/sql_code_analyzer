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
#        TODO: add constrain, delete constrain
#
#
#######################################

from __future__ import annotations

from sql_code_analyzer.in_memory_representation.struct.base import Base

from typing import TYPE_CHECKING

from sql_code_analyzer.in_memory_representation.struct.column import Column
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
                if arg not in ["this", "kind", "expressions"]:
                    self.args[arg] = node.args[arg]

        self.__add_table_to_schema()

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, value):
        self._name = value

    @property
    def schema(self) -> Schema:
        return self._schema

    @schema.setter
    def schema(self, value):
        self._schema = value

    @property
    def database(self) -> Database:
        return self._database

    @database.setter
    def database(self, value):
        self._database = value

    @property
    def columns(self) -> dict:
        return self._columns

    @columns.setter
    def columns(self, value):
        self._columns = value

    @property
    def primary_key(self) -> PrimaryKey | None:
        return self._primary_key

    @primary_key.setter
    def primary_key(self, value):
        self._primary_key = value

    @property
    def constrains(self) -> dict:
        return self._constrains

    @constrains.setter
    def constrains(self, value):
        self._constrains = value

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
            ProgramReporter.show_error_message(
                message="Table " + self.name + " already exists."
            )

        self.schema.tables[self.name] = self
        self.schema.database.index_registration(key=(self.schema.name, self.name),
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
    #      PRIMARY KEY
    #########################

    def add_primary_key(self, primary_key: PrimaryKey) -> None:
        if self.primary_key is not None:
            ProgramReporter.show_error_message(
                message="Primary key already exists."
            )

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

        if not self.verify_can_be_deleted:
            ProgramReporter.show_error_message(
                message="Table can NOT be deleted because of relations with another tables."
            )

        self.database.index_cancel_registration(key=(self.schema.name, self.name))
        del self.schema.tables[self.name]

    #########################
    #         API
    #########################

    ################
    #     GET
    ################

    def get_column(self, column_name: str) -> Column | None:
        if not self.verify_column(column_name=column_name):
            return None

        return self.columns[column_name]

    def get_columns_count(self) -> int:
        return len(self.columns)

    ################
    #    VERIFY
    ################

    def verify_column(self, column_name: str) -> bool:
        for colum in self.columns:
            colum: Column
            if colum.name == column_name:
                return True

        return False

    def verify_columns_count(self, expected_count) -> bool:
        return len(self.columns) == expected_count

    def verify_name(self, expected_name) -> bool:
        return self.name == expected_name

    def verify_can_be_deleted(self) -> bool:
        if len(self.constrains) > 1:
            return False
        else:
            return True

    def verify_is_relationship_with_another_table(self) -> bool:
        return self.verify_can_be_deleted()

    def verify_relationship_with_another_table(self, table: Table) -> bool:
        ...

