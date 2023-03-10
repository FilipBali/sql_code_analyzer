from sql_code_analyzer.in_memory_representation.struct.schema import Schema
from sql_code_analyzer.in_memory_representation.struct.table import Table


class Database:

    def __init__(self,
                 db_name):
        self.name = db_name
        self.schemas = {}
        self.object_index = {}

    name: str = None
    schemas: dict = {}
    object_index = {}

    def index_registration(self, key, reg_object):
        self.object_index[key] = reg_object

    def index_cancel_registration(self, key):
        to_delete = []
        for o in self.object_index:
            if o is str and key is str:
                if o == key:
                    to_delete.append(o)
            elif isinstance(o, str) and not isinstance(key, str):
                continue
            elif not isinstance(o, str) and isinstance(key, str):
                continue
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

    def set_default_scheme(self):
        schema = Schema(self, "Default")
        self.schemas["Default"] = schema
        self.index_registration(key="Default",
                                reg_object=schema)
        return self

    @staticmethod
    def init_memory_representation(db_name: str = "default"):
        """
        Create memory representation
        :param db_name: Database name
        :return: Object of memory representation
        """
        return Database(db_name=db_name)

    def check_if_schema_exists(self, target_schema_name) -> bool:
        """
        Checks if schema is already present in database
        :param target_schema_name: Schema name
        :return: True if present, otherwise false
        """
        if target_schema_name in self.schemas:
            return True
        return False

    def check_if_table_in_schema_exists(self,
                                        target_schema_name,
                                        target_table_name) -> bool:
        """
        Checks if table in given schema is already present
        :param target_schema_name: Schema name
        :param target_table_name: Table name
        :return:
        """
        db_schema = self.get_schema_by_name(target_schema_name)

        if target_table_name in db_schema.tables:
            return True
        return False

    def get_schema_by_name(self, target_schema_name: str) -> Schema:
        """
        Get schema object from database by given name
        :param target_schema_name: Schema name
        :return: Schema object
        """
        if target_schema_name == "":
            return self.schemas["Default"]

        if not self.check_if_schema_exists(target_schema_name):
            raise "Schema not exists"

        return self.schemas[target_schema_name]

    def get_table_by_name(self, target_schema_name, target_table_name: str) -> Table:
        """
        Get table object from database by given name and schema name
        :param target_schema_name: Schema name
        :param target_table_name: Table name
        :return: Table object
        """
        if not self.check_if_table_in_schema_exists(target_schema_name, target_table_name):
            raise "Table or schema no exists"
        db_schema = self.schemas[target_schema_name]
        return db_schema[target_table_name]

    def get_or_create_table(self, database, target_schema_name, target_table_name):
        """
        Get table from database if already exists there, or it will be created
        :param target_schema_name: Schema name
        :param target_table_name: Table name
        :return: Table object
        """
        if self.check_if_table_in_schema_exists(target_schema_name, target_table_name):
            db_schema = self.schemas[target_schema_name]
            return db_schema[target_table_name]

        return Table(database=database,
                     schema=self.get_schema_by_name(target_schema_name),
                     name=target_table_name)

    def get_or_create_schema(self, database, target_schema_name):
        """
        Get schema from database if already exists there, or it will be created
        :param database:
        :param target_schema_name: Schema name
        :return: Schema object
        """
        # Check if not already exists
        if self.check_if_schema_exists(target_schema_name):
            return self.get_schema_by_name(target_schema_name)

        return Schema(parent=database,
                      schema_name=target_schema_name)

    #########################
    # s
    #########################

    def delete_table(self, schema, table):
        if schema is not None and schema is not str:
            schema = schema.name
        if schema is None or schema == "":
            schema = "Default"

        db_schema = self.get_schema_by_name(schema)
        self.index_cancel_registration(key=(db_schema.name, table.name))
        db_schema.delete_table(table.name)



















