import sqlglot
from sql_code_analyzer.checker.tools.rules_handler import CRules

from sql_code_analyzer.in_memory_representation.actions.modify_representation.index.alter_index import alter_index
from sql_code_analyzer.in_memory_representation.actions.modify_representation.index.create_index import create_index
from sql_code_analyzer.in_memory_representation.actions.modify_representation.index.drop_index import drop_index
from sql_code_analyzer.in_memory_representation.actions.modify_representation.schema.alter_schema import alter_schema
from sql_code_analyzer.in_memory_representation.actions.modify_representation.schema.create_schema import create_schema
from sql_code_analyzer.in_memory_representation.actions.modify_representation.schema.drop_schema import drop_schema
from sql_code_analyzer.in_memory_representation.actions.modify_representation.table.alter_table import alter_table
from sql_code_analyzer.in_memory_representation.actions.modify_representation.table.drop_table import drop_table
from sql_code_analyzer.in_memory_representation.actions.modify_representation.table.create_table import create_table
from sql_code_analyzer.in_memory_representation.actions.select.select import select_statement
from sql_code_analyzer.in_memory_representation.struct.database import Database
from sql_code_analyzer.input.args_handler import CArgs

# from example import Database # cython


available_methods = (
    ##################################
    # MODIFY IN-MEMORY REPRESENTATION
    ##################################

    #########
    # CREATE
    #########
    create_schema.__name__,
    create_table.__name__,
    create_index.__name__,

    #########
    # ALTER
    #########
    alter_schema.__name__,
    alter_table.__name__,
    alter_index.__name__,

    #########
    # DROP
    #########
    drop_schema.__name__,
    drop_table.__name__,
    drop_index.__name__,

    #########
    # INSERT
    #########

    #########
    # UPDATE
    #########

    #########
    # DELETE
    #########

    ##################################
    #        QUERY STATEMENTS
    ##################################
    select_statement.__name__,
)


def modify_representation():
    """
    TODO description
    :return:
    """
    if hasattr(ast, "key") and "kind" in ast.args:
        if ast.key+"_"+ast.args["kind"].lower() in available_methods:
            eval(ast.key+"_"+ast.args["kind"].lower()+"(ast, mem_rep)")
        else:
            print(ast.key.upper() + " " + ast.args["kind"].upper() + " is not supported")

    elif hasattr(ast, "key"):
        eval(ast.key + "_statement(ast, mem_rep)")
    else:
        raise "Unknown command."


if __name__ == "__main__":
    # Get data from program input and init class for arguments
    args_data = CArgs()

    # Init rules class
    rules_args_data = CRules(path_to_rules_folder=args_data.path_to_rules_folder,
               include_folders=args_data.include_folders,
               exclude_folders=args_data.exclude_folders)

    # Initialise in memory representation
    mem_rep = Database("MemoryDB").set_default_scheme()

    # Iterate over SQL statements
    for statement in args_data.statements:

        # Parse statement, get AST
        ast = sqlglot.parse_one(statement)

        # Provide changes based on SQL statement to memory representation
        modify_representation()

    ...
