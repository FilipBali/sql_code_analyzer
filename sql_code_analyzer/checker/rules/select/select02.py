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
        self.inside_from: int = 0
        self.columns = []
        self.tables = []
        self.depth = 1

    @include_class_reports()
    def select_visit(self):
        self.inside_select += 1
        if len(self.columns) < self.inside_select:
            self.columns.append([])

    @include_class_reports()
    def select_leave(self):
        self.inside_select -= self.depth

    @include_class_reports()
    def column_visit(self):
        if self.inside_select:
            self.columns[self.inside_select-1].append(self.node)

    @include_class_reports()
    def from_visit(self):
        self.inside_from += self.depth
        if len(self.tables) < self.inside_from:
            self.tables.append([])

    @include_class_reports()
    def subquery_visit(self):
        if self.inside_from:
            self.tables[self.inside_from-1].append(self.node)

    # @include_class_reports()
    def table_visit(self):
        if self.inside_from:
            self.tables[self.inside_from-1].append(self.node)

    @include_class_reports()
    def from_leave(self):
        self.inside_from -= 1

        if len(self.columns[self.inside_from]):
            ttables = self.tables[self.inside_from]
            tcolumns = self.columns[self.inside_from]

            for tcolumn in tcolumns:
                found = False
                if tcolumn.table != "":
                    for ttable in ttables:
                        if ttable.alias == tcolumn.table:
                            found = True
                            break

                    if not found:
                        self.create_report("alias-not-exists", node=tcolumn.args['table'], alias=tcolumn.table)


def register(checker) -> None:
    checker.register_rule(UnknownAliasRule)
