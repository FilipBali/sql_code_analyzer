from sql_code_analyzer.in_memory_representation.struct.database import Database
from sqlglot import Expression


def alter_index(ast: Expression, mem_rep: Database):
    ...

def register(linter) -> None:
    linter.register_modify_representation_statement(
        modify_representation_function=alter_index
    )
