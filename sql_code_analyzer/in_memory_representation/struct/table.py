from __future__ import annotations

from sql_code_analyzer.in_memory_representation.struct.base import Base

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from sql_code_analyzer.in_memory_representation.struct.column import Column
    from sql_code_analyzer.in_memory_representation.struct.database import Database
    from sql_code_analyzer.in_memory_representation.struct.schema import Schema


class Table(Base):
    """
    TODO Table Description
    Description
    """

    # Table name
    name: str = None

    # Schema which table belong to
    schema: Schema = None

    # Database which table belong to
    database: Database = None

    # Table columns
    columns: dict = {}

    # Table constrains (which affect whole table like CheckConstrain or ForeignKey)
    constrains: dict = []

    def __init__(self,
                 name: str,
                 schema: Schema,
                 database: Database):
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
        self.constrains: dict = {}

    def __repr__(self):
        """
        TODO description
        :return:
        """
        return self.name

    ###################################
    #             CHECK
    ###################################

    def check_if_column_exists(self, column_name) -> bool:
        """
        TODO description check_if_column_exists
        :param column_name:
        :return:
        """

        return self.check_if_exists(find_attr_val=column_name,
                                    struct=self.columns)

    ###################################
    #              ADD
    ###################################

    def add_column(self, new_column: Column) -> None:
        """
        TODO description add_column
        :param new_column:
        :return:
        """

        # Check if not already exists
        if self.check_if_column_exists(new_column.name):
            raise "Column already exists"

        self.columns[new_column.name] = new_column
        self.database.index_registration(key=(self.schema.name, self.name, new_column.name),
                                         reg_object=new_column)

    ###################################
    #             DELETE
    ###################################
    def delete_table(self) -> None:
        """
        TODO Description
        :param schema:
        :param table:
        :return:
        """

        if len(self.constrains) > 1:
            raise "Table can NOT be deleted because of relations with another tables"

        self.database.index_cancel_registration(key=(self.schema.name, self.name))
        del self.schema.tables[self.name]


