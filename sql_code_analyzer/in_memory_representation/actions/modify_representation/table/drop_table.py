from __future__ import annotations

from queue import Queue

from sql_code_analyzer.in_memory_representation.struct.schema import Schema
from sql_code_analyzer.in_memory_representation.struct.table import Table
from sql_code_analyzer.in_memory_representation.tools.ast_manipulation import get_next_node
from sql_code_analyzer.output.reporter.program_reporter import ProgramReporter

from sqlglot import Expression
from sqlglot import expressions as exp

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from sql_code_analyzer.in_memory_representation.struct.database import Database


def drop_table(ast: Expression, mem_rep: Database) -> None:
    """
    Provides parsing of abstract syntax tree of DROP TABLE statement
    It deletes table in memory representation according to processed data

    :param ast: Abstract syntax tree of DROP talbe state,emt
    :param mem_rep: Reference to memory representation
    :return: None
    """

    ast_generator = ast.walk(bfs=False)
    visited_nodes = Queue()

    node, nodes, stop_parse = get_next_node(visited_nodes=visited_nodes,
                                            ast_generator=ast_generator)

    cascade = node.args["cascade"]
    materialized = node.args['materialized']
    temporary = node.args['temporary']
    kind = node.args['kind']
    exists = node.args['exists']

    schema_name = None
    table_name = None

    if isinstance(node, exp.Drop):
        # Drop statement
        node, nodes, stop_parse = get_next_node(visited_nodes=visited_nodes,
                                                ast_generator=ast_generator)

        if isinstance(node, exp.Table):
            # Target table

            # Trying to get scheme name
            if hasattr(node, "db"):
                schema_name = node.db

            # Trying to get table name
            if hasattr(node, "name"):
                table_name = node.name

    # Get schema name
    # If schema name is None, then the program will work with the default schema of a database
    if schema_name is not None and len(schema_name) > 1:
        schema: Schema = mem_rep.get_indexed_object(index_key=schema_name)
    else:
        schema: Schema = mem_rep.get_indexed_object(index_key=mem_rep.default_schema)

    # Get table from memory representation
    # If not exists, then its error state because we have nothing to delete
    table: Table | None = None
    if table_name is not None:
        table: Table = mem_rep.get_indexed_object(index_key=(schema.name,
                                                             table_name))
    else:
        ProgramReporter.show_missing_property_error_message(
            message="Missing table name while executing TABLE DROP."
        )

    # According to arguments in AST, the program
    # chooses an operation
    if cascade:
        # Delete table cascade
        table.delete_cascade().delete_table()

    elif materialized:
        pass

    elif temporary:
        pass

    else:
        # Delete table
        table.delete_table()


def register(linter) -> None:
    linter.register_modify_representation_statement(
        modify_representation_function=drop_table
    )
