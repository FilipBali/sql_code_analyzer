from sql_code_analyzer.checker.rules.base import BaseRule
from sql_code_analyzer.checker.tools.rule_decorators import include_class_reports

messages = {
    "alias-not-exists": {
        "message": "Table alias \"{alias}\" not exists."
    },
}


class UnknownAliasRule(BaseRule):

    restrict = {"select"}
    messages = messages

    def __init__(self):
        super().__init__()
        self.inside_select: int = 0
        self.depth_count: int = 0
        self.columns = []
        self.tables = []
        self.depth = 1

    def select_visit(self):
        self.depth_count += self.depth
        self.inside_select += self.depth
        if len(self.columns) < self.inside_select:
            self.columns.append([])
            self.tables.append([])

    def select_leave(self):
        self.inside_select -= self.depth

    def column_visit(self):
        self.columns[self.inside_select-1].append(self.node)

    def subquery_visit(self):
        self.tables[self.inside_select-1].append(self.node)

    def table_visit(self):
        self.tables[self.inside_select-1].append(self.node)

    @include_class_reports()
    def end_statement_lint(self):
        for i in range(0, self.depth_count):
            if len(self.columns[i]):

                tables_current_depth = self.tables[i]
                columns_current_depth = self.columns[i]

                for column in columns_current_depth:
                    found = False
                    if column.table != "":
                        for table in tables_current_depth:
                            if table.alias == column.table:
                                found = True
                                break

                        if not found:
                            self.create_report("alias-not-exists", node=column.args['table'], alias=column.table)


def register(checker) -> None:
    checker.register_rule(UnknownAliasRule)
