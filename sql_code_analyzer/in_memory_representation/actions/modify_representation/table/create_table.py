from __future__ import annotations

from sql_code_analyzer.in_memory_representation.struct.column import Column, column_constrains_list
from sql_code_analyzer.in_memory_representation.struct.constrain import CheckExpression, PrimaryKey, \
    PreventNotNull, UniqueValue, DefaultValue, ForeignKey
from sql_code_analyzer.in_memory_representation.struct.datatype import Datatype

from sql_code_analyzer.in_memory_representation.tool.ast_manipulation import get_next_node, skip_lower_nodes
from sqlglot import Expression
from sqlglot import expressions as exp
from queue import Queue

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from sql_code_analyzer.in_memory_representation.struct.table import Table
    from sql_code_analyzer.in_memory_representation.struct.schema import Schema
    from sql_code_analyzer.in_memory_representation.struct.database import Database


def create_table(ast: Expression, mem_rep: Database) -> None:
    """
    
    :param ast:
    :param mem_rep:
    :return:
    """

    def parse_foreign_key(name: str = None) -> None:
        fk_columns: list = []

        ref_table: Table | None = None
        ref_columns: list = []

        while 1:
            node, nodes, stop_parse = get_next_node(visited_nodes=visited_nodes,
                                                    ast_generator=ast_generator)

            if isinstance(node, exp.ForeignKey):
                pass
            elif isinstance(node, exp.Identifier):
                column_fk: Column = mem_rep.get_indexed_object(index_key=(schema.name,
                                                                          table.name,
                                                                          node.name))
                column_fk.set_foreign_key(True)
                fk_columns.append(column_fk)

            elif isinstance(node, exp.Reference):
                while 1:
                    node, nodes, stop_parse = get_next_node(visited_nodes=visited_nodes,
                                                            ast_generator=ast_generator)

                    if isinstance(node, exp.Identifier):
                        if ref_table is None:
                            ref_table: Table = mem_rep.get_indexed_object(index_key=(schema.name,
                                                                                              node.name))
                        else:
                            fk_reference_column: Column = mem_rep.get_indexed_object(index_key=(schema.name,
                                                                                                ref_table.name,
                                                                                                node.name))
                            ref_columns.append(fk_reference_column)

                    else:
                        break

            else:
                break

        constr_fk = ForeignKey(fk_columns=fk_columns,
                               reference_columns=ref_columns,
                               table_fk=table,
                               table_ref=ref_table)

        table.constrains.setdefault((table, table), []).append(constr_fk)
        ref_table.constrains.setdefault((ref_table, table), []).append(constr_fk)

        # table.constrains.append(constr_fk)
        # ref_table.constrains.append(constr_fk)

    ast_generator = ast.walk(bfs=False)
    visited_nodes = Queue()

    #################################
    # Variables as temporary memory
    #################################
    schema: Schema = None
    table: Table = None

    stop_parse = False
    while 1 and stop_parse is not True:
        node, nodes, stop_parse = get_next_node(visited_nodes=visited_nodes,
                                                ast_generator=ast_generator)
        node_root = node

        if isinstance(node, exp.Create):
            ###############################
            # Node layer: root -> CREATE
            ###############################
            pass

        elif isinstance(node, exp.Schema):
            ###############################
            # Node layer: CREATE -> SCHEMA
            ###############################
            node, nodes, stop_parse = get_next_node(visited_nodes=visited_nodes,
                                                    ast_generator=ast_generator)
            context_layer_node_depth = node.depth

            # get schema name
            schema: Schema = mem_rep.get_schema_by_name_or_error(node.db)
            # get table object
            table: Table = mem_rep.get_or_create_table(database=mem_rep,
                                                       schema_name=schema.name,
                                                       table_name=node.name)

            skip_lower_nodes(visited_nodes,
                             ast_generator,
                             context_layer_node_depth)

        elif isinstance(node, exp.ColumnDef):
            ###############################
            # Node layer: SCHEMA -> COLUMN
            ###############################
            column_name = ""
            column_type = ""
            column_datatype = None
            constrains = []
            node_col = node
            while 1:
                node, nodes, stop_parse = get_next_node(visited_nodes=visited_nodes,
                                                        ast_generator=ast_generator)
                if isinstance(node, exp.Identifier):
                    ####################################
                    # Node layer: COLUMN -> IDENTIFIER
                    ####################################
                    column_name = node.name

                elif isinstance(node, exp.DataType):
                    #################################
                    # Node layer: COLUMN -> DATATYPE
                    #################################
                    column_datatype = node.this

                    node, nodes, stop_parse = get_next_node(visited_nodes=visited_nodes,
                                                            ast_generator=ast_generator)
                    if isinstance(node, exp.Literal):
                        #################################
                        # Node layer: DATATYPE -> LITERAL
                        #################################
                        column_datatype_value = node.name
                        column_type = Datatype(column_datatype, column_datatype_value)
                    else:
                        column_type = Datatype(column_datatype)
                        visited_nodes.put(nodes)

                elif isinstance(node, exp.ColumnConstraint):
                    ##################################
                    # Node layer: COLUMN -> CONSTRAIN
                    ##################################
                    context_layer_node_depth = node.depth

                    node, nodes, stop_parse = get_next_node(visited_nodes=visited_nodes,
                                                            ast_generator=ast_generator)

                    if isinstance(node, exp.NotNullColumnConstraint):
                        constrains.append((PreventNotNull(None), "column"))

                    elif isinstance(node, exp.PrimaryKeyColumnConstraint):
                        constrains.append((PrimaryKey(column=None), "column"))

                    elif isinstance(node, exp.DefaultColumnConstraint):
                        constrains.append((DefaultValue(default_value=str(node.name), column=None), "column"))

                    elif isinstance(node, exp.GeneratedAsIdentityColumnConstraint):
                        ...
                    else:
                        ...

                    skip_lower_nodes(visited_nodes,
                                     ast_generator,
                                     context_layer_node_depth)

                else:
                    ##################################
                    # Node layer: COLUMN -> Not Found
                    ##################################
                    visited_nodes.put(nodes)
                    break

            ##################################
            #    ADD COLUMN TO THE TABLE
            ##################################
            new_col = Column(
                        name=column_name,
                        datatype=column_type,
                        table=table,
                        constrains=[],
                    )

            table.add_column(new_col)
            for constrain in constrains:
                t_constrain = constrain[0]
                set_attr = constrain[1]

                # add to columns constrain structure
                new_col.add_constrain(t_constrain)

                # add to scheme constrain structure
                t_constrain.set_property(set_attr, new_col)

        elif isinstance(node, column_constrains_list):
            ###################################
            # Node layer: SCHEMA -> CONSTRAIN
            ###################################
            if "expressions" in node.args and \
                    node.args["expressions"].__len__() > 0 and \
                    isinstance(node.args["expressions"][0], exp.ForeignKey):
                ################################################################
                # Node layer: SCHEMA -> ForeignKey (Relationship)
                ################################################################

                node, nodes, stop_parse = get_next_node(visited_nodes=visited_nodes,
                                                        ast_generator=ast_generator)
                if isinstance(node, exp.Identifier):
                    parse_foreign_key(name=node.name)

            elif isinstance(node, exp.CheckColumnConstraint):
                ################################################################
                # Node layer: SCHEMA -> CheckColumnConstraint (CheckExpression)
                ################################################################

                table.constrains.setdefault((table, table), []).append(CheckExpression(expression=str(node.this)))

                context_layer_node_depth = node.depth
                skip_lower_nodes(visited_nodes,
                                 ast_generator,
                                 context_layer_node_depth)

        elif isinstance(node, exp.PrimaryKey):
            ###################################
            # Node layer: SCHEMA -> PrimaryKey
            ###################################
            # primary_key = []
            while 1:
                node, nodes, stop_parse = get_next_node(visited_nodes=visited_nodes,
                                                        ast_generator=ast_generator)

                if isinstance(node, exp.Identifier):
                    column_pk: Column = mem_rep.get_indexed_object(index_key=(schema.name,
                                                                              table.name,
                                                                              node.name))
                    # Create primary key constrain object
                    constr_pk = PrimaryKey(column=column_pk)

                    # Set constrain in column
                    column_pk.set_primary_key(bool_val=True, constr_pk=constr_pk)

                else:
                    break
            # table.primary_key = primary_key

        elif isinstance(node, exp.ForeignKey):
            ###################################
            # Node layer: SCHEMA -> ForeignKey
            ###################################
            parse_foreign_key()

        elif isinstance(node, exp.Unique):
            ###################################
            # Node layer: SCHEMA -> Unique
            ###################################
            node, nodes, stop_parse = get_next_node(visited_nodes=visited_nodes,
                                                    ast_generator=ast_generator)

            column_unique: Column = mem_rep.get_indexed_object(index_key=(schema.name,
                                                                          table.name,
                                                                          node.name))
            column_unique.set_unique_key(True)

            uniqCon = UniqueValue(column=column_unique)
            schema.constrains.setdefault((table, table), []).append(uniqCon)

            column_unique.add_constrain(uniqCon)

        else:
            ##################################
            # Node layer: SCHEMA -> Not found
            ##################################
            if node is not None:
                repr(node)
                print("else node: " + node.name + " " + node.key)

    ##################################
    #   CREATE TABLE & STORE TABLE
    ##################################
    schema.add_table(table=table)

