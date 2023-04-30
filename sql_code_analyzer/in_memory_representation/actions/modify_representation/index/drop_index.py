from __future__ import annotations

from queue import Queue

from sql_code_analyzer.in_memory_representation.tools.ast_manipulation import get_next_node
from sqlglot import expressions as exp
from sqlglot import Expression

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from sql_code_analyzer.in_memory_representation.struct.database import Database
    from sqlglot import Expression


def drop_index(ast: Expression, mem_rep: Database):
    ast_generator = ast.walk(bfs=False)
    visited_nodes = Queue()

    stop_parse = False
    while 1 and stop_parse is not True:
        node, nodes, stop_parse = get_next_node(visited_nodes=visited_nodes,
                                                ast_generator=ast_generator)

        if isinstance(node, exp.Drop):
            ...

        elif isinstance(node, exp.Table):

            ...

            node, nodes, stop_parse = get_next_node(visited_nodes=visited_nodes,
                                                    ast_generator=ast_generator)

            if isinstance(node, exp.Identifier):
                ...

    else:
        ...


def register(linter) -> None:
    linter.register_modify_representation_statement(
        modify_representation_function=drop_index
    )
