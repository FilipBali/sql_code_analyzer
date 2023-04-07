from __future__ import annotations

from queue import Queue

from sql_code_analyzer.in_memory_representation.struct.constrain import ForeignKey
# from sql_code_analyzer.in_memory_representation.struct.database import Database
from sql_code_analyzer.in_memory_representation.struct.schema import Schema
from sql_code_analyzer.in_memory_representation.struct.table import Table
from sql_code_analyzer.in_memory_representation.tools.ast_manipulation import get_next_node
from sql_code_analyzer.output.reporter.base import ProgramReporter
from sqlglot import Expression
from sqlglot import expressions as exp

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from sql_code_analyzer.in_memory_representation.struct.database import Database


def drop_table(ast: Expression, mem_rep: Database):
    """
    TODO description
    :param ast:
    :param mem_rep:
    :return:
    """

    ast_generator = ast.walk(bfs=False)
    visited_nodes = Queue()

    node, nodes, stop_parse = get_next_node(visited_nodes=visited_nodes,
                                            ast_generator=ast_generator)

    cascade = node.args["cascade"]
    materialized = node.args['materialized']
    temporary = node.args['temporary']
    kind = node.args['kind']
    exists = node.args['exists']

    schema_name = None
    table_name = None

    if isinstance(node, exp.Drop):
        # Drop statement
        node, nodes, stop_parse = get_next_node(visited_nodes=visited_nodes,
                                                ast_generator=ast_generator)

        if isinstance(node, exp.Table):
            # Target table

            # Trying to get table name
            if hasattr(node, "name"):
                table_name = node.name

            while 1 and stop_parse is not True:
                # Iterate over Table details
                node, nodes, stop_parse = get_next_node(visited_nodes=visited_nodes,
                                                        ast_generator=ast_generator)

                if isinstance(node, exp.Identifier) and node.arg_key == "db":
                    # Trying to get scheme name
                    schema_name = node.name

    if schema_name is not None:
        schema: Schema = mem_rep.get_indexed_object(index_key=schema_name)
    else:
        schema: Schema = mem_rep.get_indexed_object(index_key="Default")

    if table_name is not None:
        table: Table = mem_rep.get_indexed_object(index_key=(schema.name,
                                                             table_name))
    else:
        ProgramReporter.show_error_message(
            message="Missing table name while executing TABLE DROP."
        )

    if cascade:
        constrain_key: tuple = (table, table)
        for constrain in table.constrains[constrain_key]:
            if isinstance(constrain, ForeignKey):
                constrain.delete_reference()

    elif materialized:
        ...

    elif temporary:
        ...

    else:
        # Delete table
        # mem_rep.delete_table(table)
        table.delete_table()


def register(linter) -> None:
    linter.register_modify_representation_statement(
        modify_representation_function=drop_table
    )
