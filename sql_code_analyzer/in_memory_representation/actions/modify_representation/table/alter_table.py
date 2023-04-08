from queue import Queue

from sql_code_analyzer.in_memory_representation.struct.database import Database
from sqlglot import Expression
from sql_code_analyzer.in_memory_representation.tools.ast_manipulation import get_next_node


from sqlglot import expressions as exp


def alter_table(ast: Expression, mem_rep: Database):

    # TODO problem, alter nemaju dorobeny v poriadku
    #
    # Vyhodnoti alter table spravne, ale column odignoruje a ide len do drop
    # ALTER TABLE table_name1
    # DROP COLUMN  index_name;

    ast_generator = ast.walk(bfs=False)
    visited_nodes = Queue()

    stop_parse = False
    while 1 and stop_parse is not True:
        node, nodes, stop_parse = get_next_node(visited_nodes=visited_nodes,
                                                ast_generator=ast_generator)

        if isinstance(node, exp.AlterTable):
            ...

        elif isinstance(node, exp.Table):

            ...

            node, nodes, stop_parse = get_next_node(visited_nodes=visited_nodes,
                                                    ast_generator=ast_generator)

            if isinstance(node, exp.Identifier):
                ...

        elif isinstance(node, exp.Drop):

            if node.args["kind"].lower() == "index":

                node, nodes, stop_parse = get_next_node(visited_nodes=visited_nodes,
                                                        ast_generator=ast_generator)

                if isinstance(node, exp.Table):
                    ...

                    node, nodes, stop_parse = get_next_node(visited_nodes=visited_nodes,
                                                            ast_generator=ast_generator)

                    if isinstance(node, exp.Identifier):
                        ...

            elif node.args["kind"].lower() == "column":

                node, nodes, stop_parse = get_next_node(visited_nodes=visited_nodes,
                                                        ast_generator=ast_generator)

                if isinstance(node, exp.Table):
                    ...

                    node, nodes, stop_parse = get_next_node(visited_nodes=visited_nodes,
                                                            ast_generator=ast_generator)

                    if isinstance(node, exp.Identifier):
                        ...

        else:
            ...


def register(linter) -> None:
    linter.register_modify_representation_statement(
        modify_representation_function=alter_table
    )
