from sql_code_analyzer.in_memory_representation.struct.database import Database
from sqlglot import Expression


def alter_schema(ast: Expression, mem_rep: Database):
    print("alter_schema not implemented")


def register(linter) -> None:
    linter.register_modify_representation_statement(
        modify_representation_function=alter_schema
    )

