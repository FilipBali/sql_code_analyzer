from queue import Queue
from typing import List

from sql_code_analyzer.in_memory_representation.struct.column import Column
from sql_code_analyzer.in_memory_representation.struct.constrain import Index
from sql_code_analyzer.in_memory_representation.struct.database import Database
from sql_code_analyzer.in_memory_representation.struct.schema import Schema
from sql_code_analyzer.in_memory_representation.struct.table import Table
from sql_code_analyzer.in_memory_representation.tools.ast_manipulation import get_next_node
from sqlglot import Expression

from sqlglot import expressions as exp


def create_index(ast: Expression, mem_rep: Database):
    ast_generator = ast.walk(bfs=False)
    visited_nodes = Queue()

    schema: Schema | None = None
    table: Table | None = None
    index_name: str | None = None
    indexed_columns: List[Column] = []

    stop_parse = False
    while 1 and stop_parse is not True:
        node, nodes, stop_parse = get_next_node(visited_nodes=visited_nodes,
                                                ast_generator=ast_generator)

        if isinstance(node, exp.Create):
            pass

        elif isinstance(node, exp.Index):
            node, nodes, stop_parse = get_next_node(visited_nodes=visited_nodes,
                                                    ast_generator=ast_generator)

            if isinstance(node, exp.Identifier):
                index_name = node.name

        elif isinstance(node, exp.Table):
            schema_name = node.db
            if schema_name is not None and len(schema_name) > 1:
                schema: Schema = mem_rep.get_indexed_object(index_key=schema_name)
            else:
                schema: Schema = mem_rep.get_indexed_object(index_key=mem_rep.default_schema)

            table_name = node.name
            table: Table = mem_rep.get_indexed_object(index_key=(schema.name,
                                                                 table_name))

        elif isinstance(node, exp.Paren):
            # If there is only one indexed column

            while 1 and stop_parse is not True:
                node, nodes, stop_parse = get_next_node(visited_nodes=visited_nodes,
                                                        ast_generator=ast_generator)

                if isinstance(node, exp.Column):
                    node, nodes, stop_parse = get_next_node(visited_nodes=visited_nodes,
                                                            ast_generator=ast_generator)

                    if isinstance(node, exp.Identifier):
                        column_name = node.name
                        column: Column = mem_rep.get_indexed_object(index_key=(schema.name,
                                                                               table.name,
                                                                               column_name))
                        indexed_columns.append(column)

                    # Identifier
                    else:
                        visited_nodes.put(nodes)
                        break
                # Column
                else:
                    break

        elif isinstance(node, exp.Tuple):
            # If there are multiple indexed columns

            while 1 and stop_parse is not True:
                node, nodes, stop_parse = get_next_node(visited_nodes=visited_nodes,
                                                        ast_generator=ast_generator)

                if isinstance(node, exp.Column):
                    node, nodes, stop_parse = get_next_node(visited_nodes=visited_nodes,
                                                            ast_generator=ast_generator)

                    if isinstance(node, exp.Identifier):
                        column_name = node.name
                        column: Column = mem_rep.get_indexed_object(index_key=(schema.name,
                                                                               table.name,
                                                                               column_name))
                        indexed_columns.append(column)

                    # Identifier
                    else:
                        visited_nodes.put(nodes)
                        break
                # Column
                else:
                    break

        else:
            ...

    table.add_index(index=Index(name=index_name, columns=indexed_columns))


def register(linter) -> None:
    linter.register_modify_representation_statement(
        modify_representation_function=create_index
    )
