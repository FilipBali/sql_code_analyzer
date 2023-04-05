from sql_code_analyzer.adapter.class_factory import class_factory
from sql_code_analyzer.in_memory_representation.tools.ast_manipulation import get_next_node
from queue import Queue


def adapt_ast(ast):
    ast_generator = ast.walk(bfs=False)
    visited_nodes = Queue()

    stop_parse = False
    while 1 and stop_parse is not True:
        node, nodes, stop_parse = get_next_node(visited_nodes=visited_nodes,
                                                ast_generator=ast_generator)

        if stop_parse:
            break

        class_factory(name=node.__class__.__name__ + "_", from_class=node.__class__).cast(node)

    return ast
