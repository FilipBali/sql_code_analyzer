from sql_code_analyzer.in_memory_representation.struct.database import Database
from sqlglot import Expression


def alter_index(sql_ast: Expression, mem_rep: Database):
    ...