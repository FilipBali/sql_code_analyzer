##########################################################################################################
# CREATE SCHEMA { [ schemaName AUTHORIZATION user-name ] | [ schemaName ] |
# [ AUTHORIZATION user-name ] }
# Details
#   Source: https://docs.oracle.com/javadb/10.8.3.0/ref/rrefsqlj31580.html
##########################################################################################################
from __future__ import annotations
from queue import Queue

from sql_code_analyzer.in_memory_representation.struct.schema import Schema
from sql_code_analyzer.in_memory_representation.tool.ast_manipulation import get_next_node
from sqlglot import expressions as exp

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from sql_code_analyzer.in_memory_representation.struct.database import Database


def create_schema(ast: exp, mem_rep: Database):
    """
    TODO description
    :param ast:
    :param mem_rep:
    :return:
    """
    ast_generator = ast.walk(bfs=False)
    visited_nodes = Queue()

    schema_name: str = ""

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
                schema_name = node.name

    Schema(database=mem_rep, schema_name=schema_name)


