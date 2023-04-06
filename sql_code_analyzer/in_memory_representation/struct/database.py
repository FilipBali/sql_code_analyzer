#######################################
# File name: database.py
# Purpose: Database class represents instance of database
#
# Key features:
#     Database:
#        Stores: database name,
#                database schemas
#                index with points to every object in database providing shortcuts
#
#######################################


from __future__ import annotations

from sql_code_analyzer.in_memory_representation.struct.base import Base
from sql_code_analyzer.in_memory_representation.struct.table import Table

from typing import TYPE_CHECKING

from sql_code_analyzer.output.reporter.base import ProgramReporter

if TYPE_CHECKING:
    from sql_code_analyzer.in_memory_representation.struct.schema import Schema


class Database(Base):
    """
    TODO description
    """

    ###################################
    #              INIT
    ###################################
    def __init__(self,
                 db_name: str = ""):
        """
        TODO description
        :param db_name:
        """

        self.name = db_name
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
        TODO description
        :return:
        """

        from sql_code_analyzer.in_memory_representation.struct.schema import Schema

        schema = Schema(self, "dbo")
        self.schemas["dbo"] = schema
        self.index_registration(key="dbo",
                                reg_object=schema)
        return self

    ###########################
    #          INDEX
    ###########################
    def index_registration(self, key, reg_object) -> None:
        """
        TODO description
        :param key:
        :param reg_object:
        :return:
        """

        self.object_index[key] = reg_object

    def index_cancel_registration(self, key) -> None:
        """
        TODO description
        :param key:
        :return:
        """

        # list where are stored items that will be deleted from object_index
        to_delete = []

        # iterate through all items in object_index
        for o in self.object_index:

            # because algorithm works with __len__() then functionality is different
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
            # we need to delete all references to sub-level parts of deleted item
            # so all objects that have same attributes(on same level) as deleted one, they need to be deleted as well
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
        TODO description
        :param index_key:
        :return:
        """
        if index_key in self.object_index:
            return self.object_index[index_key]
        else:
            ProgramReporter.show_error_message("Item in indexed objects not exists.")

    ###########################
    #         CHECKS
    ###########################
    def check_if_schema_exists_bool(self, target_schema_name) -> bool:
        """
        TODO description
        :param target_schema_name:
        :return:
        """

        return self.check_if_exists(target_schema_name, self.schemas)

    ###########################
    #   SCHEMA MANIPULATION
    ###########################
    def get_schema_by_name_or_error(self, schema_name: str) -> Schema:
        """
        TODO description
        :param schema_name:
        :return:
        """

        if schema_name == "":
            schema_name = "dbo"

        schema_instance = self.get_instance_or_error(find_attr_val=schema_name,
                                                     find_in_struct=self.schemas,
                                                     error_message="Error: Schema not exists"
                                                     )
        return schema_instance

    def get_or_create_schema(self, database, schema_name) -> Schema:
        """
        Get schema from database if already exists there, or it will be created
        :param database:
        :param schema_name: Schema name
        :return: Schema object
        """
        instance = self.get_instance_or_none(find_attr_val=schema_name,
                                             find_in_struct=self.schemas
                                             )
        if instance is not None:
            return instance
        return Schema(database, schema_name)

    ###########################
    #    TABLE MANIPULATION
    ###########################
    def get_table_by_name_or_error(self, schema_name, table_name: str) -> Table:
        """
        TODO description
        :param schema_name:
        :param table_name:
        :return:
        """

        schema_instance = self.get_schema_by_name_or_error(schema_name)

        table_instance = self.get_instance_or_error(find_attr_val=table_name,
                                                    find_in_struct=schema_instance,
                                                    error_message="Error: Table not exists"
                                                    )
        return table_instance

    def get_or_create_table(self,
                            database,
                            schema_name,
                            table_name,
                            create_node=None) -> Table:
        """
        Get table from database if already exists there, or it will be created
        :param database:
        :param schema_name: Schema name
        :param table_name: Table name
        :param create_node: AST node of creation statement
        :return: Table object
        """

        schema_instance = self.get_instance_or_error(find_attr_val=schema_name,
                                                     find_in_struct=self.schemas,
                                                     error_message="Error: Schema not exists"
                                                     )

        table_instance = self.get_instance_or_none(find_attr_val=table_name,
                                                   find_in_struct=schema_instance
                                                   )
        if table_instance is not None:
            return table_instance
        return Table(database=database,
                     schema=schema_instance,
                     name=table_name,
                     node=create_node)

    ###########################
    #   BACKUP SERIALIZATION
    ###########################
    def load_deserialization_path(self, deserialization_path: str):
        # TODO
        pass

    def serialize_and_save(self, serialization_path: str):
        # TODO
        pass
