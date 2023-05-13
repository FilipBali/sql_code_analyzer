from sql_code_analyzer.checker.rules.base import BaseRule
from sql_code_analyzer.checker.tools.rule_decorators import include_class_reports, include_reports

messages = {
    "table-not-exists": {
        "message": "Table {name} not exists"
    },
    "column-not-exists": {
        "message": "Column not exists"
    },
    "column-wrong-datatype": {
        "message": "Column has wrong datatype"
    },
}


class Create01(BaseRule):
    # persistent = True
    # temporary = True
    # no_code_preview = False

    restrict = {"create_table"}
    messages = messages

    # @include_reports(reports=reports)
    @include_class_reports()
    def table_visit(self):
        # self.create_report("table-not-exists", name=self.node.name)
        ...

    @include_class_reports()
    def create_leave(self):
        ...

    @include_class_reports()
    def identifier_visit(self):
        ...

    @include_class_reports()
    def identifier_leave(self):
        ...


def register(checker) -> None:
    checker.register_rule(Create01)
