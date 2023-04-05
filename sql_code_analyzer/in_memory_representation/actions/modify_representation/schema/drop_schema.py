from __future__ import annotations
from queue import Queue

from sqlglot import expressions as exp
from sql_code_analyzer.in_memory_representation.tools.ast_manipulation import get_next_node


from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from sql_code_analyzer.in_memory_representation.struct.database import Database
    from sql_code_analyzer.in_memory_representation.struct.schema import Schema


def drop_schema(ast: exp, mem_rep: Database):
    ast_generator = ast.walk(bfs=False)
    visited_nodes = Queue()

    schema_name: str = ""

    node, nodes, stop_parse = get_next_node(visited_nodes=visited_nodes,
                                            ast_generator=ast_generator)

    if isinstance(node, exp.Drop):
        # Schema statement
        node, nodes, stop_parse = get_next_node(visited_nodes=visited_nodes,
                                                ast_generator=ast_generator)

        if isinstance(node, exp.Table):
            node, nodes, stop_parse = get_next_node(visited_nodes=visited_nodes,
                                                    ast_generator=ast_generator)

            if isinstance(node, exp.Identifier):
                schema_name = node.name

    schema: Schema = mem_rep.get_indexed_object(index_key=schema_name)
    schema.delete_schema()


def register(linter) -> None:
    linter.register_modify_representation_statement(
        modify_representation_function=drop_schema
    )

