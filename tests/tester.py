import unittest
from pathlib import Path

import sqlglot

from sql_code_analyzer.in_memory_representation.struct.column import Column
from sql_code_analyzer.in_memory_representation.struct.constrain import PrimaryKey, Constrain
from sql_code_analyzer.in_memory_representation.struct.database import Database
from sql_code_analyzer.in_memory_representation.struct.datatype import Datatype
from sql_code_analyzer.in_memory_representation.struct.schema import Schema
from sql_code_analyzer.tools.path import get_absolute_path, get_path_object


class TestPath(unittest.TestCase):
    # function: get_absolute_path
    def test_get_absolute_path_with_valid_input(self):
        result = get_absolute_path('test.txt')
        self.assertIsInstance(result, Path)
        self.assertEqual(result.name, 'test.txt')

    def test_get_absolute_path_with_invalid_input(self):
        with self.assertRaises(SystemExit) as cm:
            get_absolute_path(123)
        self.assertEqual(cm.exception.code, -1)

    # function: get_path_object
    def test_get_path_object_with_valid_input(self):
        result = get_path_object('test.txt')
        self.assertIsInstance(result, Path)
        self.assertEqual(result.name, 'test.txt')

    def test_get_path_object_with_invalid_input(self):
        with self.assertRaises(SystemExit) as cm:
            get_path_object(123)
        self.assertEqual(cm.exception.code, -1)


class DatabaseObject(unittest.TestCase):

    def test_database_initialisation(self):
        result = Database("MemoryDB")
        self.assertIsInstance(result, Database)
        self.assertEqual(len(result.object_index), 0)
        self.assertEqual(len(result.schemas), 0)

    def test_database_initialisation_with_default_scheme(self):
        result = Database("MemoryDB").set_default_scheme()
        self.assertIsInstance(result, Database)
        self.assertEqual(len(result.object_index), 1)
        self.assertEqual("dbo" in result.object_index, True)
        self.assertIsInstance(result.object_index["dbo"], Schema)
        self.assertEqual(len(result.schemas), 1)
        self.assertIsInstance(result.schemas["dbo"], Schema)
        # Equal objects
        self.assertEqual(result.schemas["dbo"], result.object_index["dbo"])

        self.assertEqual(len(result.schemas["dbo"].tables), 0)

    def test_database_table(self):
        result = Database("MemoryDB").set_default_scheme()

        # Verify schema
        schema: Schema = result.get_schema_by_name_or_error("")
        self.assertIsInstance(schema, Schema)
        self.assertEqual(schema.name, "dbo")
        self.assertEqual(result.object_index["dbo"], schema)
        self.assertEqual(len(schema.tables), 0)

        # Create Table1
        result.get_or_create_table(database=result,
                                   schema_name="dbo",
                                   table_name="Table1")

        self.assertEqual(len(schema.tables), 1)
        self.assertEqual("Table1" in schema.tables, True)

        # Create Table2
        result.get_or_create_table(database=result,
                                   schema_name="dbo",
                                   table_name="Table2")

        self.assertEqual(len(schema.tables), 2)
        self.assertEqual("Table1" in schema.tables, True)
        self.assertEqual("Table2" in schema.tables, True)

        # Check if schema is not overwritten by get or create table function
        schema_dbo = result.get_or_create_schema(database=result,
                                                 schema_name="dbo")

        self.assertIsInstance(schema_dbo, Schema)
        self.assertEqual(len(schema_dbo.tables), 2)
        self.assertEqual("Table1" in schema_dbo.tables, True)
        self.assertEqual("Table2" in schema_dbo.tables, True)

        schema_new = result.get_or_create_schema(database=result, schema_name="NewSchema")

        self.assertIsInstance(schema_new, Schema)
        self.assertEqual(len(schema_new.tables), 0)
        self.assertEqual("Table1" in schema_new.tables, False)
        self.assertEqual("Table2" in schema_new.tables, False)

        # Check if table is not overwritten by get or create table function
        table1_obj = result.get_or_create_table(database=result,
                                                schema_name="dbo",
                                                table_name="Table1")

        self.assertEqual(len(schema.tables), 2)
        self.assertEqual("Table1" in schema.tables, True)
        self.assertEqual("Table2" in schema.tables, True)
        self.assertEqual(table1_obj, schema.tables["Table1"])

        table1_obj.delete_table()

        self.assertEqual(len(schema.tables), 1)
        self.assertEqual("Table1" in schema.tables, False)
        self.assertEqual("Table2" in schema.tables, True)

        result.get_or_create_table(database=result,
                                   schema_name="dbo",
                                   table_name="Table1")

        self.assertEqual(len(schema.tables), 2)
        self.assertEqual("Table1" in schema.tables, True)
        self.assertEqual("Table2" in schema.tables, True)
        # Test that new Table1 is not same as old one
        self.assertNotEqual(table1_obj, schema.tables["Table1"])


        result.get_or_create_table(database=result,
                                   schema_name="NewSchema",
                                   table_name="Table1")

        self.assertEqual(len(schema_new.tables), 1)
        self.assertEqual("Table1" in schema_new.tables, True)
        self.assertEqual("Table2" in schema_new.tables, False)

        self.assertNotEqual(schema_new.tables["Table1"], schema.tables["Table1"])

    def test_database_column(self):
        result = Database("MemoryDB").set_default_scheme()

        # Verify schema
        schema: Schema = result.get_schema_by_name_or_error("")

        # Create Table1
        table1 = result.get_or_create_table(database=result,
                                           schema_name=schema.name,
                                           table_name="Table1")

        # Create Table2
        table2 = result.get_or_create_table(database=result,
                                           schema_name=schema.name,
                                           table_name="Table2")

        statement = "CREATE TABLE Table1 (" \
                    "id INTEGER PRIMARY KEY, " \
                    "name VARCHAR(35)" \
                    ")"
        ast = list(sqlglot.parse_one(statement).walk(bfs=False))

        # Extract data
        ast_id = ast[5][0]
        ast_id_datatype = ast[6][0]

        datatype = Datatype(node=ast_id_datatype,
                            literals=[])


        Column(
            identifier=ast_id,
            datatype=datatype,
            table=table1,
            constrains=[],
        )

        self.assertEqual("id" in table1.columns, True)
        self.assertEqual("id" in table2.columns, False)

        self.assertEqual(schema.name in result.object_index, True)
        self.assertEqual((schema.name, table1.name) in result.object_index, True)
        self.assertEqual((schema.name, table2.name) in result.object_index, True)
        self.assertEqual((schema.name, table1.name, "id") in result.object_index, True)
        self.assertEqual((schema.name, table2.name, "id") in result.object_index, False)

        col1: Column = result.object_index[(schema.name, table1.name, "id")]
        self.assertEqual(len(col1.constrains), 0)

        col1.add_constrain(PrimaryKey(columns=[col1]))
        self.assertEqual(len(col1.constrains), 1)
        self.assertIsInstance(col1.constrains[0], PrimaryKey)

        pk: Constrain = col1.constrains[0]
        col1.delete_constrain(constrain=pk)

        self.assertEqual(len(col1.constrains), 0)

