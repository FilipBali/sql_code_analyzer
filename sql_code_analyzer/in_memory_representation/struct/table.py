#######################################
# File name: table.py
# Purpose: Table class represents database table
#
# Key features:
#     Table:
#        Stores: table name
#                table columns
#                table level constrains(foreign key, check constraint etc.)
#                table primary key
#                connection to the schema that belongs to
#                connection to the database that belongs to
#
#
#######################################

from __future__ import annotations

from sql_code_analyzer.in_memory_representation.struct.base import Base

from typing import TYPE_CHECKING, Dict

from sql_code_analyzer.in_memory_representation.struct.column import Column

if TYPE_CHECKING:
    from sql_code_analyzer.in_memory_representation.struct.constrain import PrimaryKey, ForeignKey, Index
    from sql_code_analyzer.in_memory_representation.struct.database import Database
    from sql_code_analyzer.in_memory_representation.struct.schema import Schema


class Table(Base):
    """
    Represents table in memory representation
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
        :param name: Table's name
        :param schema: The schema to which the table belongs
        :param database: The database to which the table belongs
        """
        self.name: str = name
        self.schema: Schema = schema
        self.database: Database = database
        self.columns: dict = {}
        self.primary_key: PrimaryKey | None = None
        self.constrains: dict = {}
        self.indexes: dict = {}

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
    def columns(self) -> Dict:
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
    def constrains(self) -> Dict:
        return self._constrains

    @constrains.setter
    def constrains(self, value):
        self._constrains = value

    @property
    def indexes(self) -> Dict:
        return self._indexes

    @indexes.setter
    def indexes(self, value):
        self._indexes = value

    def __repr__(self):
        return self.name

    ##################################################
    #                  PRIVATE METHODS
    ##################################################
    #########################
    #          ADD
    #########################

    def __add_table_to_schema(self) -> None:
        """
        Add table to the schema and memory representation index
        :return: None
        """

        if self.schema.check_if_table_exists(table=self):
            self.RuleReporter.add_memory_representation_report(
                message=f"Table {self.name} already exists."
            )
            return

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
        Verify if table has a column with that name
        :param column_name: The column name
        :return: True/False
        """

        return self.check_if_exists(find_attr_val=column_name,
                                    struct=self.columns)

    #########################
    #      PRIMARY KEY
    #########################

    def add_primary_key(self, primary_key: PrimaryKey) -> None:
        """
        Adds primary key to table
        :param primary_key: The primary key
        :return: None
        """

        if self.primary_key is not None:
            self.RuleReporter.add_memory_representation_report(
                message=f"Primary key in table {self.name} already exists."
            )
            return

        self.primary_key = primary_key

    def delete_primary_key(self) -> None:
        self.primary_key = None

    #########################
    #        INDEXES
    #########################

    def add_index(self, index: Index) -> None:
        if index.name in self.indexes:
            self.RuleReporter.add_memory_representation_report(
                message=f"An error occurred when trying to add a new index to the table {self.name} \n"
                        f"The index with name {index.name} already exists in this table."
            )
            return

        self.indexes[index.name] = index

    def delete_index(self, index_name) -> None:
        if index_name not in self.indexes:
            self.RuleReporter.add_memory_representation_report(
                message=f"An error occurred when trying to delete the index from the table {self.name} \n"
                        f"The index with name {index_name} does not exists in this table."
            )
            return

        self.indexes.pop(index_name)

    #########################
    #         DELETE
    #########################

    def delete_cascade(self) -> Table:
        constrain_key: tuple = (self, self)
        for constrain in self.constrains[constrain_key]:
            if isinstance(constrain, ForeignKey):
                constrain.delete_reference()

        return self

    def delete_table(self) -> None:
        """
        Delete table from memory representation
        :return: None
        """

        if not self.verify_can_be_deleted:
            self.RuleReporter.add_memory_representation_report(
                message=f"Table {self.name} can NOT be deleted because of relations with another tables."
            )
            return

        self.database.index_cancel_registration(key=(self.schema.name, self.name))
        del self.schema.tables[self.name]

    #########################
    #         API
    #########################

    ################
    #     GET
    ################

    def get_column(self, column_name: str) -> Column | None:
        """
        Return column by the name if exists
        :param column_name: Column name
        :return: Instance of column or none
        """

        if not self.verify_column(column_name=column_name):
            return None

        return self.columns[column_name]

    def get_columns_count(self) -> int:
        """
        Returns count of how many columns the table has
        :return: Count of columns
        """

        return len(self.columns)

    ################
    #    VERIFY
    ################

    def verify_column(self, column_name: str) -> bool:
        """
        Verify if the column with that name exists
        :param column_name: The column name
        :return: True/False
        """
        for colum in self.columns:
            colum: Column
            if colum.name == column_name:
                return True

        return False

    def verify_columns_count(self, expected_count) -> bool:
        """
        Return count of columns which are belonged to table
        :param expected_count:
        :return: True/False
        """
        return len(self.columns) == expected_count

    def verify_name(self, expected_name) -> bool:
        """
         Return True if table has this name otherwise False
        :param expected_name: The name
        :return: True/False
        """
        return self.name == expected_name

    def verify_can_be_deleted(self) -> bool:
        """
        Verify if the table meets requirements to be deleted from memory representation
        :return: True/False
        """
        if len(self.constrains) > 1:
            return False
        else:
            return True

    def verify_is_relationship_with_another_table(self) -> bool:
        """
        Verify if table has the relationship with another table
        :return: True/False
        """
        return self.verify_can_be_deleted()

    def verify_relationship_with_another_table(self, table: Table) -> bool:
        """
        Verify if table has the relationship with table provided in argument
        :param table: Table object
        :return: True/False
        """
        ...
