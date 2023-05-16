#######################################
# File name: database.py
# Purpose: Database class represents instance of database
#
# Key features:
#     Database:
#        Stores: database name,
#                database schemas
#                index with points to every object in a database providing shortcuts
#
#######################################


from __future__ import annotations

from sql_code_analyzer.in_memory_representation.exceptions import MissingTableException, MissingSchemaException
from sql_code_analyzer.in_memory_representation.struct.base import Base
from sql_code_analyzer.in_memory_representation.struct.table import Table
from sql_code_analyzer.in_memory_representation.struct.schema import Schema
from typing import TYPE_CHECKING

from sql_code_analyzer.output.reporter.program_reporter import ProgramReporter

if TYPE_CHECKING:
    ...


class Database(Base):
    """
    Represents a database in memory representation.
    """

    ###################################
    #              INIT
    ###################################
    def __init__(self, db_name: str = ""):
        """
        :param db_name: Database name
        """

        self.name = db_name
        self.default_schema = "dbo"
        self.schemas = {}
        self.object_index = {}

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, value):
        self._name = value

    @property
    def schemas(self) -> dict:
        return self._schemas

    @schemas.setter
    def schemas(self, value):
        self._schemas = value

    @property
    def object_index(self) -> dict:
        return self._object_index

    @object_index.setter
    def object_index(self, value):
        self._object_index = value

    @property
    def default_schema(self):
        return self._default_schema

    @default_schema.setter
    def default_schema(self, value):
        self._default_schema = value

    ##################################################
    #                  PRIVATE METHODS
    ##################################################

    ##################################################
    #                  PUBLIC METHODS
    ##################################################

    #########################
    #        INTERNAL
    #########################

    def set_default_scheme(self) -> Database:
        """
        Sets a default scheme to database instance
        In a database system is common to have a database scheme,
        But the name can be different based on the implementation of database system
        :return: Database instance
        """

        from sql_code_analyzer.in_memory_representation.struct.schema import Schema

        schema = Schema(self, self.default_schema)
        self.schemas[self.default_schema] = schema
        self.index_registration(key=self.default_schema,
                                reg_object=schema)
        return self

    ###########################
    #          INDEX
    ###########################
    def index_registration(self, key, reg_object) -> None:
        """
        Register an object to database index.
        Database index is focusing on faster access to database objects
        :param key: The registration key
        :param reg_object: Reference to the object
        :return: None
        """

        self.object_index[key] = reg_object

    def index_cancel_registration(self, key) -> None:
        """
        Delete an object from database index
        :param key: The key of object in database index
        :return: None
        """

        # list where are stored items that will be deleted from object_index
        to_delete = []

        # iterate through all items in object_index
        for o in self.object_index:

            # because the algorithm works with __len__() then functionality is different
            # when str, then __len__() counts number of chars
            # when tuple, then __len() counts number of items in tuple

            # if strings are same
            if o is str and key is str:
                if o == key:
                    to_delete.append(o)

            # not same type, cant be same, continue
            elif isinstance(o, str) and not isinstance(key, str):
                continue

            # not same type, cant be same, continue
            elif not isinstance(o, str) and isinstance(key, str):
                continue

            # check if tuples have mutual attributes in structure like
            # we need to delete all references to sublevel parts of deleted item
            # so all objects that have the same attributes(on the same level) as deleted one,
            # they need to be deleted as well
            #
            #       |level0|  |level1|  |level2| ... |level n||
            # 1) (  schema1,  table1,    col1   )
            # 2) (  schema1,  table1,    col2   )
            # 3) (  schema1,  table2,    col1   )
            #
            # 1) and 2) have same schema1, table1 => same table, different columns (object points to columns)
            # 1), 2), 3) have same schema, but different table, then they are differs from table level
            elif o.__len__() >= key.__len__():
                mutual_parents = True
                for i in range(0, key.__len__()):
                    if o[i] != key[i]:
                        mutual_parents = False
                        break
                if mutual_parents:
                    to_delete.append(o)

        for reg in to_delete:
            self.object_index.pop(reg)

    def get_indexed_object(self, index_key):
        """
        Get an object from a database using database index
        :param index_key: The database index key which refers to the object
        :return:
        """
        if index_key in self.object_index:
            return self.object_index[index_key]
        else:
            ProgramReporter.show_missing_property_error_message(
                message=f"Item {str(index_key)} is not exists in indexed objects."
            )

    ###########################
    #         CHECKS
    ###########################
    def check_if_schema_exists_bool(self, target_schema_name) -> bool:
        """
        Verify if target schema exists in database
        :param target_schema_name: The schema name
        :return: True/False
        """

        return self.check_if_exists(target_schema_name, self.schemas)

    ###########################
    #   SCHEMA MANIPULATION
    ###########################
    def get_schema_by_name_or_error(self, schema_name: str) -> Schema:
        """
        Return schema if exists in a database or raise error
        :param schema_name: Schema name
        :return: The instance of schema or raised error
        """

        if schema_name == "":
            schema_name = self.default_schema

        schema_instance = self.get_instance_or_error(find_attr_val=schema_name,
                                                     find_in_struct=self.schemas,
                                                     exception=MissingSchemaException
                                                     )
        return schema_instance

    def get_or_create_schema(self, database, schema_name) -> Schema:
        """
        Get schema from database if already exists there, or it will be created
        :param database: TODO neda sa nahradit self?
        :param schema_name: Schema name
        :return: Schema object
        """
        instance = self.get_instance_or_none(find_attr_val=schema_name,
                                             find_in_struct=self.schemas
                                             )
        if instance is not None:
            return instance

        return Schema(database=database, schema_name=schema_name)

    ###########################
    #    TABLE MANIPULATION
    ###########################
    def get_table_by_name_or_error(self, schema_name, table_name: str) -> Table:
        """
        Get instance of table or raise error
        :param schema_name: Schema name
        :param table_name: Table name
        :return: Returns table instance if exists otherwise raised error
        """

        schema_instance = self.get_schema_by_name_or_error(schema_name)

        table_instance = self.get_instance_or_error(find_attr_val=table_name,
                                                    find_in_struct=schema_instance.tables,
                                                    exception=MissingTableException
                                                    )
        return table_instance

    def get_or_create_table(self,
                            database,
                            schema_name,
                            table_name,
                            create_node=None) -> Table:
        """
        Get table from a database if already exists there, or it will be created
        :param database:
        :param schema_name: Schema name
        :param table_name: Table name
        :param create_node: AST node of creation statement
        :return: Table object
        """

        schema_instance = self.get_instance_or_error(find_attr_val=schema_name,
                                                     find_in_struct=self.schemas,
                                                     exception=MissingSchemaException
                                                     )

        table_instance = self.get_instance_or_none(find_attr_val=table_name,
                                                   find_in_struct=schema_instance.tables
                                                   )
        if table_instance is not None:
            return table_instance
        return Table(database=database,
                     schema=schema_instance,
                     name=table_name,
                     node=create_node)
