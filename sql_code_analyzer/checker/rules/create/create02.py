from sql_code_analyzer.checker.rules.base import BaseRule
from sql_code_analyzer.checker.tools.rule_decorators import include_class_reports

messages = {
    "aaaa": {
        "message": "Table not exists"
    },
    "bbbb": {
        "message": "Column not exists"
    },
    "cccc": {
        "message": "Column has wrong datatype"
    },
}

class Create02(BaseRule):

    messages = messages

    @include_class_reports()
    def create_visit(self):
        self.create_report("cccc", self.node)
        # print("create_visit")
        self.nieco = 15
        ...


def register(checker) -> None:
    checker.register_rule(Create02)
