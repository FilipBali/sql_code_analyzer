from __future__ import annotations
from queue import Queue

from sql_code_analyzer.output.reporter.program_reporter import ProgramReporter
from sqlglot import expressions as exp
from sql_code_analyzer.in_memory_representation.tools.ast_manipulation import get_next_node


from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from sql_code_analyzer.in_memory_representation.struct.database import Database
    from sql_code_analyzer.in_memory_representation.struct.schema import Schema


def drop_schema(ast: exp, mem_rep: Database):
    """

    :param ast:
    :param mem_rep:
    :return:
    """

    ast_generator = ast.walk(bfs=False)
    visited_nodes = Queue()

    schema_name: str | None = None

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
                # Get schema name
                schema_name = node.name

    if schema_name is None:
        ProgramReporter.show_error_message(
            message="Can not parse schema name from abstract syntax tree (DROP SCHEMA)"
        )

    schema: Schema = mem_rep.get_indexed_object(index_key=schema_name)
    schema.delete_schema()


def register(linter) -> None:
    linter.register_modify_representation_statement(
        modify_representation_function=drop_schema
    )
