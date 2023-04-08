from sql_code_analyzer.output import enums


class Terminator:
    """
    A class that provides an interface for terminating a program.
    """

    @staticmethod
    def exit(exit_code: enums.ExitWith) -> None:
        """
        A method that terminates a program based on the value of an argument.
        :param exit_code: Exit value
        :return: None
        """

        exit(exit_code.value)
