##########################################################################################################
# CREATE SCHEMA { [ schemaName AUTHORIZATION user-name ] | [ schemaName ] |
# [ AUTHORIZATION user-name ] }
# Details
#   Source: https://docs.oracle.com/javadb/10.8.3.0/ref/rrefsqlj31580.html
##########################################################################################################
from __future__ import annotations
from queue import Queue

from sql_code_analyzer.in_memory_representation.struct.schema import Schema
from sql_code_analyzer.in_memory_representation.tools.ast_manipulation import get_next_node
from sql_code_analyzer.output.reporter.program_reporter import ProgramReporter
from sqlglot import expressions as exp

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from sql_code_analyzer.in_memory_representation.struct.database import Database


def create_schema(ast: exp, mem_rep: Database) -> None:
    """
    Create schema in memory representation
    :param ast: Abstract syntax tree of schema
    :param mem_rep: Reference to memory representation
    :return: None
    """

    ast_generator = ast.walk(bfs=False)
    visited_nodes = Queue()

    schema_name: str | None = None

    node, nodes, stop_parse = get_next_node(visited_nodes=visited_nodes,
                                            ast_generator=ast_generator)

    if isinstance(node, exp.Create):
        # Schema statement
        node, nodes, stop_parse = get_next_node(visited_nodes=visited_nodes,
                                                ast_generator=ast_generator)

        if isinstance(node, exp.Table):
            node, nodes, stop_parse = get_next_node(visited_nodes=visited_nodes,
                                                    ast_generator=ast_generator)

            if isinstance(node, exp.Identifier):
                # Get schema name
                schema_name = node.name

    if schema_name is None:
        ProgramReporter.show_error_message(
            message="Can not parse schema name from abstract syntax tree (CREATE SCHEMA)"
        )

    # Create schema with registration to the database
    Schema(database=mem_rep, schema_name=schema_name)


def register(linter) -> None:
    linter.register_modify_representation_statement(
        modify_representation_function=create_schema
    )
