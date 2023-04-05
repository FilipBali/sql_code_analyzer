from sql_code_analyzer.output import enums


class Terminator:

    @staticmethod
    def exit(exit_code: enums.ExitWith):
        exit(exit_code.value)
