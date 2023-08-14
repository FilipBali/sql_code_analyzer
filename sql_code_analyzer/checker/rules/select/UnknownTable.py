from sql_code_analyzer.checker.rules.base import BaseRule
from sql_code_analyzer.checker.tools.rule_decorators import include_class_reports, include_reports
from sql_code_analyzer.in_memory_representation.exceptions import MissingTableException
from sqlglot import expressions as exp

messages = {
    "table-not-exists": {
        "message": "Table \"{name}\" not exists."
    }
}


class UnknownTableRule(BaseRule):

    restrict = {"select"}
    messages = messages

    def __init__(self):
        super().__init__()
        self.inside_from = 0
        self.depth = 1

    def from_visit(self):
        self.inside_from += self.depth

    def from_leave(self):
        self.inside_from -= self.depth

    @include_class_reports()
    def table_visit(self):

        if self.inside_from:

            # Get schema name
            schema_name = self.node.db

            # Get table name
            table_name = self.node.name

            try:
                _ = self.mem_rep.get_table_by_name_or_error(schema_name=schema_name, table_name=table_name)
            except MissingTableException:
                self.create_report("table-not-exists", name=self.node.name)


def register(checker) -> None:
    checker.register_rule(UnknownTableRule)
