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
    #             INIT
    ###################################

    name: str = ""
    tables: dict = {}
    database: Database = None

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
        ...
    ###################################
    #             CHECKS
    ###################################

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

    ###################################
    #              ADD
    ###################################
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

    def add_table(self, table) -> None:
        """
        TODO description
        :param table:
        :return: None
        """
        # Check if already exists
        if self.check_if_table_exists(table):
            raise "Table already exists"

        self.tables[table.name] = table
        self.database.index_registration(key=(self.name, table.name),
                                         reg_object=table)

    ###################################
    #             DELETE
    ###################################
    def delete_schema(self) -> None:
        """
        TODO description
        :return: None
        """
        # TODO error ak je tabulka?
        del self.database.schemas[self.name]
        self.database.index_cancel_registration(key=self.name)


