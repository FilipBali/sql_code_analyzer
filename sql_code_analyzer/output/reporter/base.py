from sql_code_analyzer.output.enums import OutputType


class Reporter:
    """
    Base class providing interface to create a reporter class for a particular purpose.
    """

    _color = {"reset": "\033[0m",
              "green": "\33[92m",
              "red": "\33[91m"
              }

    report_output = OutputType.Stdout
    report_output_file = None
    verbose = False
    text = None

    def print(self) -> None:
        """
        A base method that provides a prescription for
        implementing a method that displays a message on standard output.

        :return: None
        """

        match self.report_output:
            case OutputType.Stdout:
                self._print_stdout()

            case OutputType.File:
                self._print_file()

            case OutputType.Silent:
                pass

    def _print_stdout(self):
        print(self.text)

    def _print_file(self):
        # Delete colors if any
        for key, value in self._color.items():
            self.text = self.text.replace(value.encode('latin1').decode('unicode_escape'), '')

        with open(self.report_output_file, 'a') as f:
            f.write(self.text)

    @staticmethod
    def set_output_file(path: str):
        Reporter.report_output = OutputType.File
        Reporter.report_output_file = path

        # Create file
        with open(Reporter.report_output_file, 'w') as f:
            pass


class _Message(Reporter):
    """
    Base class providing interface for creating messages.
    """

    _reset = "\033[0m"
    _wrap_length = 80
    text = None

    def print(self) -> None:
        """
        Encapsulate print method for _Message objects

        :return: None
        """

        super().print()
