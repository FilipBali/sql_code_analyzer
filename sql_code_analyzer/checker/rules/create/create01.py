from sql_code_analyzer.checker.rules.base import BaseRule
from sql_code_analyzer.checker.tools.rule_decorators import include_class_reports, include_reports


class HelpClass:

    def create_visit(self):
        ...

    def foo_func(self):
        ...


reports = {
    "dara-lora": {
        "id": "L150",
        "message": "Lorem Impum Hat"
    },
    "zveq-dmes-laranc": {
        "id": "L151",
        "message": "Lorem Impum Hat"
    },
    "darq-lard-mda": {
        "id": "L152",
        "message": "Lorem Impum Hat"
    },
    "fora-mora-gola": {
        "id": "L153",
        "message": "Lorem Impum Hat"
    }
}


class Create01(BaseRule):
    persistent = True

    restrict = {"drop", "select", "create_table"}

    reports = reports

    # @include_reports(reports=reports)
    @include_class_reports()
    def create_visit(self, node):
        self.create_report("darq-lard-mda", node)
        print("create_visit")

    @include_class_reports()
    def create_leave(self, node):
        print("create_leave")

    @include_class_reports()
    def identifier_visit(self, node):
        print("identifier_visit1 " + node.name)

    @include_class_reports()
    def identifier_leave(self, node):
        print("identifier_leave2 " + node.name)

    @include_class_reports()
    def table_visit(self, node):
        print("table_visit1 " + node.name)

    @include_class_reports()
    def table_leave(self, node):
        print("table_leave2 " + node.name)


def register(checker) -> None:
    checker.register_rule(Create01)
