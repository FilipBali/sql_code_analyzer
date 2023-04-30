from sql_code_analyzer.checker.rules.base import BaseRule
from sql_code_analyzer.checker.tools.rule_decorators import include_class_reports, include_reports


class HelpClass:

    def create_visit(self):
        ...

    def foo_func(self):
        ...


messages = {
    "table-not-exists": {
        "message": "Table not exists"
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

    restrict = {"create_table", "select", "drop"}
    messages = messages

    # @include_reports(reports=reports)
    @include_class_reports()
    def create_visit(self):
        self.create_report("table-not-exists", self.node)
        # print("create_visit")
        self.nieco = 15
        ...

    @include_class_reports()
    def create_leave(self):
        # print("create_leave")
        ...

    @include_class_reports()
    def identifier_visit(self):
        self.create_report("column-not-exists", self.node)
        # print("identifier_visit1 " + self.node.name)

    @include_class_reports()
    def identifier_leave(self):
        # print("identifier_leave2 " + self.node.name)
        ...

    @include_class_reports()
    def table_visit(self):
        # print("table_visit1 " + self.node.name)
        ...

    @include_class_reports()
    def table_leave(self):
        # print("table_leave2 " + self.node.name)
        ...

def register(checker) -> None:
    checker.register_rule(Create01)
