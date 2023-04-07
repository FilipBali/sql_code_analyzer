from __future__ import annotations

from sql_code_analyzer.in_memory_representation.struct.column import Column, column_constrains_list
from sql_code_analyzer.in_memory_representation.struct.constrain import CheckExpression, \
    PreventNotNull, UniqueValue, DefaultValue, ForeignKey, PrimaryKey
from sql_code_analyzer.in_memory_representation.struct.datatype import Datatype
from sql_code_analyzer.in_memory_representation.struct.literal import Literal

from sql_code_analyzer.in_memory_representation.tools.ast_manipulation import get_next_node, skip_lower_nodes
from sql_code_analyzer.output.reporter.base import ProgramReporter
from sqlglot import Expression
from sqlglot import expressions as exp
from queue import Queue

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from sql_code_analyzer.in_memory_representation.struct.table import Table
    from sql_code_analyzer.in_memory_representation.struct.schema import Schema
    from sql_code_analyzer.in_memory_representation.struct.database import Database


def parse_foreign_key(visited_nodes,
                      ast_generator,
                      mem_rep,
                      schema,
                      table) -> None:

    fk_columns: list = []

    ref_table: Table | None = None
    ref_columns: list = []

    stop_parse = False
    while 1 and stop_parse is not True:
        node, nodes, stop_parse = get_next_node(visited_nodes=visited_nodes,
                                                ast_generator=ast_generator)

        if isinstance(node, exp.ForeignKey):
            pass

        elif isinstance(node, exp.Identifier):
            column_fk: Column = mem_rep.get_indexed_object(index_key=(schema.name,
                                                                      table.name,
                                                                      node.name))
            # SET foreign key pri vytvarani
            # column_fk.set_foreign_key()
            fk_columns.append(column_fk)

        elif isinstance(node, exp.Reference):
            while 1 and stop_parse is not True:
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

                # Identifier
                else:
                    break

        # Reference
        else:
            break

    constr_fk = ForeignKey(fk_columns=fk_columns,
                           reference_columns=ref_columns,
                           table_fk=table,
                           table_ref=ref_table)

    table.constrains.setdefault((table, table), []).append(constr_fk)
    ref_table.constrains.setdefault((ref_table, table), []).append(constr_fk)


def create_table(ast: Expression, mem_rep: Database) -> None:
    """
    
    :param ast:
    :param mem_rep:
    :return:
    """

    ast_generator = ast.walk(bfs=False)
    visited_nodes = Queue()

    schema: Schema | None = None
    table: Table | None = None

    create_node = None

    stop_parse = False
    while 1 and stop_parse is not True:
        node, nodes, stop_parse = get_next_node(visited_nodes=visited_nodes,
                                                ast_generator=ast_generator)

        if isinstance(node, exp.Create):
            ###############################
            # Node layer: root -> CREATE
            ###############################

            # In creation node we expect info about statement creation properties like:
            # -> with, exists, properties, replace, unique, volatile, indexes, no_schema_binding, begin
            # Available properties can be found in exp.Create class
            create_node = node

        elif isinstance(node, exp.Schema):
            ###############################
            # Node layer: CREATE -> SCHEMA
            ###############################
            # Schema node can be skipped
            # Provides no additional information, but contains nodes that will be traversed in the future

            node, nodes, stop_parse = get_next_node(visited_nodes=visited_nodes,
                                                    ast_generator=ast_generator)
            context_layer_node_depth = node.depth

            # Getting table node
            # Here we expect schema and table name arguments

            # get schema by schema name
            schema: Schema = mem_rep.get_schema_by_name_or_error(node.db)
            # get table by database, schema, table name
            table: Table = mem_rep.get_or_create_table(database=mem_rep,
                                                       schema_name=schema.name,
                                                       table_name=node.name,
                                                       create_node=create_node)

            skip_lower_nodes(visited_nodes,
                             ast_generator,
                             context_layer_node_depth)

        elif isinstance(node, exp.ColumnDef):
            ###############################
            # Node layer: SCHEMA -> COLUMN
            ###############################

            # ColumnDef node can be skipped
            # Provides no additional information, but contains nodes specifying
            # column's properties that will be traversed in the future

            identifier = None
            datatype = None
            constrains = []
            primary_key: bool = False

            while 1 and stop_parse is not True:
                node, nodes, stop_parse = get_next_node(visited_nodes=visited_nodes,
                                                        ast_generator=ast_generator)
                if isinstance(node, exp.Identifier):
                    ####################################
                    # Node layer: COLUMN -> IDENTIFIER
                    ####################################
                    # Here we expect info about column identifier (name) like:
                    # -> name and if it's quoted
                    identifier = node

                elif isinstance(node, exp.DataType):
                    #################################
                    # Node layer: COLUMN -> DATATYPE
                    #################################
                    # Here we expect info about column datatype like:
                    # -> datatype
                    datatype_node = node

                    literals = []
                    while 1 and stop_parse is not True:
                        node, nodes, stop_parse = get_next_node(visited_nodes=visited_nodes,
                                                                ast_generator=ast_generator)

                        if isinstance(node, exp.Literal):
                            ##################################
                            # Node layer: DATATYPE -> LITERAL
                            ##################################
                            # Here we expect info about datatype literal like:
                            # -> datatype value, is_int, is_number, is_star, is_string
                            # Creating literal object and save it into literals lists
                            # List of literals will be added later in datatype object

                            # Literals are in fact datatype argument, there can be more arguments like:
                            # Datatype with one literal(15): VARCHAR(15)
                            # Datatype with two literals(10,20): NUMBER(10,20)

                            literals.append(
                                Literal(node=node)
                            )

                        else:
                            # Here we expect node that is not part of datatype information anymore
                            # So we create datatype object which will be stored in column object later
                            datatype = Datatype(node=datatype_node,
                                                literals=literals)
                            visited_nodes.put(nodes)
                            break

                elif isinstance(node, exp.ColumnConstraint):
                    #########################################
                    # Node layer: COLUMN -> COLUMN CONSTRAIN
                    #########################################
                    # ColumnConstraint node can be skipped
                    # Provides no additional information, but contains nodes specifying
                    # column's properties that will be traversed in the future

                    context_layer_node_depth = node.depth

                    node, nodes, stop_parse = get_next_node(visited_nodes=visited_nodes,
                                                            ast_generator=ast_generator)

                    if isinstance(node, exp.NotNullColumnConstraint):
                        ###########################################
                        # Node layer: COLUMN CONSTRAIN -> Not Null
                        ###########################################
                        constrains.append((PreventNotNull(column=None), "column"))

                    elif isinstance(node, exp.PrimaryKeyColumnConstraint):
                        ##############################################
                        # Node layer: COLUMN CONSTRAIN -> Primary key
                        ##############################################
                        primary_key = True

                    elif isinstance(node, exp.DefaultColumnConstraint):
                        ################################################
                        # Node layer: COLUMN CONSTRAIN -> Default value
                        ################################################
                        constrains.append((DefaultValue(column=None, default_value=str(node.name)), "column"))

                    elif isinstance(node, exp.GeneratedAsIdentityColumnConstraint):
                        ...

                    else:

                        ...

                    skip_lower_nodes(visited_nodes=visited_nodes,
                                     ast_generator=ast_generator,
                                     context_layer_node_depth=context_layer_node_depth)

                else:
                    ##################################
                    # Node layer: COLUMN -> Not Found
                    ##################################
                    visited_nodes.put(nodes)
                    break

            ##################################
            #    ADD COLUMN TO THE TABLE
            ##################################

            # As we have all info to create column object, lets create it
            new_col = Column(
                        identifier=identifier,
                        datatype=datatype,
                        table=table,
                        constrains=[],
                    )

            # As we do not have column object as soon as we traverse all column's nodes
            # we do not have enough information to fulfill all column constrain data
            # due to column constrain has reference to Column object which not exists
            # in time when we traversed column constrain nodes

            # So now we must dynamically add constrains to column

            for constrain in constrains:
                t_constrain = constrain[0]
                set_attr = constrain[1]

                # delayed assignment of properties for constrain
                t_constrain.set_property(set_attr, new_col)

                # add constrain to new column
                new_col.add_constrain(t_constrain)

            if primary_key:
                table.add_primary_key(PrimaryKey(columns=[new_col]))

        elif isinstance(node, column_constrains_list):
            ###################################
            # Node layer: SCHEMA -> CONSTRAIN
            ###################################
            if "expressions" in node.args and \
                    node.args["expressions"].__len__() > 0 and \
                    isinstance(node.args["expressions"][0], exp.ForeignKey):
                ##################################################################
                # Node layer: SCHEMA -> TABLE CONSTRAIN ForeignKey (Relationship)
                ##################################################################

                node, nodes, stop_parse = get_next_node(visited_nodes=visited_nodes,
                                                        ast_generator=ast_generator)
                if isinstance(node, exp.Identifier):
                    parse_foreign_key(
                        visited_nodes=visited_nodes,
                        ast_generator=ast_generator,
                        mem_rep=mem_rep,
                        schema=schema,
                        table=table
                    )

            elif isinstance(node, exp.CheckColumnConstraint):
                ################################################################################
                # Node layer: SCHEMA -> TABLE CONSTRAIN CheckColumnConstraint (CheckExpression)
                ################################################################################

                table.constrains.setdefault((table, table), []).append(CheckExpression(expression=str(node.this)))

                context_layer_node_depth = node.depth
                skip_lower_nodes(visited_nodes,
                                 ast_generator,
                                 context_layer_node_depth)

        elif isinstance(node, exp.PrimaryKey):
            ###################################################################
            # Node layer: SCHEMA -> COLUMN CONSTRAIN PrimaryKey
            # Defined on CREATE TABLE level (outside the definition of column)
            ###################################################################
            primary_key: list = []
            while 1 and stop_parse is not True:
                node, nodes, stop_parse = get_next_node(visited_nodes=visited_nodes,
                                                        ast_generator=ast_generator)

                if isinstance(node, exp.Identifier):
                    column_pk: Column = mem_rep.get_indexed_object(index_key=(schema.name,
                                                                              table.name,
                                                                              node.name))
                    # Create primary key constrain object
                    # constr_pk = UniqueValue(column=column_pk, primary_key=True)

                    # Set constrain in column
                    # column_pk.set_primary_key(constr_pk=constr_pk)
                    primary_key.append(column_pk)
                else:
                    break

            table.add_primary_key(
                primary_key=PrimaryKey(columns=primary_key)
            )

        elif isinstance(node, exp.ForeignKey):
            ###################################
            # Node layer: SCHEMA -> TABLE CONSTRAIN ForeignKey
            ###################################
            parse_foreign_key(
                visited_nodes=visited_nodes,
                ast_generator=ast_generator,
                mem_rep=mem_rep,
                schema=schema,
                table=table
            )

        elif isinstance(node, exp.Unique):
            ################################################
            # Node layer: SCHEMA -> COLUMN CONSTRAIN Unique
            ################################################
            node, nodes, stop_parse = get_next_node(visited_nodes=visited_nodes,
                                                    ast_generator=ast_generator)

            column_unique: Column = mem_rep.get_indexed_object(index_key=(schema.name,
                                                                          table.name,
                                                                          node.name))
            column_unique.add_constrain(constrain=UniqueValue(column=column_unique))

        else:
            ##################################
            # Node layer: SCHEMA -> Not found
            ##################################
            if node is not None:
                ProgramReporter.show_warning_message(
                    message="Unexpected expression in CREATE TABLE statement: " + node.name + " " + node.key + "."
                )
    ...

def register(linter) -> None:
    linter.register_modify_representation_statement(
        modify_representation_function=create_table
    )

