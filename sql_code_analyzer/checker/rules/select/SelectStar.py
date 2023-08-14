from sql_code_analyzer.checker.rules.base import BaseRule
from sql_code_analyzer.checker.tools.rule_decorators import include_class_reports
from sqlglot import expressions as exp

messages = {
    "select-star": {
        "message": "Select star."
    },
}


class SelectStar(BaseRule):

    restrict = {"select"}
    messages = messages

    def __init__(self):
        super().__init__()

    @include_class_reports()
    def select_visit(self):
        for selected_item in self.node.selects:
            if isinstance(selected_item, exp.Star):
                self.create_report("select-star", node=selected_item)


def register(checker) -> None:
    checker.register_rule(SelectStar)
