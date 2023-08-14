from __future__ import annotations

from queue import Queue

from sql_code_analyzer.in_memory_representation.tools.ast_manipulation import get_next_node
from sqlglot import expressions as exp
from sqlglot import Expression

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from sql_code_analyzer.in_memory_representation.struct.database import Database
    from sql_code_analyzer.in_memory_representation.struct.table import Table
    from sqlglot import Expression


def drop_index(ast: Expression, mem_rep: Database):
    ast_generator = ast.walk(bfs=False)
    visited_nodes = Queue()

    index_name = None


    stop_parse = False
    while 1 and stop_parse is not True:
        node, nodes, stop_parse = get_next_node(visited_nodes=visited_nodes,
                                                ast_generator=ast_generator)

        if isinstance(node, exp.Drop):
            pass

        elif isinstance(node, exp.Table):

            # SQLGlot inconsistency, index name is under Table node
            index_name = node.name

            stop_parse = True

    # Delete all indexes with name "index_name"
    for key in mem_rep.object_index:
        # If two, its table, because (schema_name, table_name)
        if len(key) == 2:
            table: Table = mem_rep.object_index[key]
            if index_name in table.indexes:
                del table.indexes[index_name]


def register(linter) -> None:
    linter.register_modify_representation_statement(
        modify_representation_function=drop_index
    )
