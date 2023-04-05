from sql_code_analyzer.checker.rules.base import BaseRule


class Create02(BaseRule):
    ...


def register(checker) -> None:
    checker.register_rule(Create02)

