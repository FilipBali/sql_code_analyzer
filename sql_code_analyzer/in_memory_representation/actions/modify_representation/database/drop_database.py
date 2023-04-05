from __future__ import annotations

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from sql_code_analyzer.in_memory_representation.struct.database import Database
    from sqlglot import Expression


def drop_database(ast: Expression, mem_rep: Database):
    ...


def register(linter) -> None:
    linter.register_modify_representation_statement(
        modify_representation_function=drop_database
    )
