from queue import Queue

from sql_code_analyzer.in_memory_representation.struct.database import Database
from sql_code_analyzer.in_memory_representation.tools.ast_manipulation import get_next_node
from sqlglot import Expression

from sqlglot import expressions as exp


def create_index(ast: Expression, mem_rep: Database):
    ast_generator = ast.walk(bfs=False)
    visited_nodes = Queue()

    stop_parse = False
    while 1 and stop_parse is not True:
        node, nodes, stop_parse = get_next_node(visited_nodes=visited_nodes,
                                                ast_generator=ast_generator)

        if isinstance(node, exp.Create):
            ...

        elif isinstance(node, exp.Index):

            ...

            node, nodes, stop_parse = get_next_node(visited_nodes=visited_nodes,
                                                    ast_generator=ast_generator)

            if isinstance(node, exp.Identifier):
                ...

        elif isinstance(node, exp.Table):

            ...

            node, nodes, stop_parse = get_next_node(visited_nodes=visited_nodes,
                                                    ast_generator=ast_generator)

            if isinstance(node, exp.Identifier):
                ...

        elif isinstance(node, exp.Paren):
            ...

            while 1 and stop_parse is not True:

                node, nodes, stop_parse = get_next_node(visited_nodes=visited_nodes,
                                                        ast_generator=ast_generator)

                if isinstance(node, exp.Column):
                    ...

                    node, nodes, stop_parse = get_next_node(visited_nodes=visited_nodes,
                                                            ast_generator=ast_generator)

                    if isinstance(node, exp.Identifier):
                        ...

                    # Identifier
                    else:
                        visited_nodes.put(nodes)
                        break
                # Column
                else:
                    break

        elif isinstance(node, exp.Tuple):
            ...

            while 1 and stop_parse is not True:

                node, nodes, stop_parse = get_next_node(visited_nodes=visited_nodes,
                                                        ast_generator=ast_generator)

                if isinstance(node, exp.Column):
                    ...

                    node, nodes, stop_parse = get_next_node(visited_nodes=visited_nodes,
                                                            ast_generator=ast_generator)

                    if isinstance(node, exp.Identifier):
                        ...

                    # Identifier
                    else:
                        visited_nodes.put(nodes)
                        break
                # Column
                else:
                    break

        else:
            ...

def register(linter) -> None:
    linter.register_modify_representation_statement(
        modify_representation_function=create_index
    )
