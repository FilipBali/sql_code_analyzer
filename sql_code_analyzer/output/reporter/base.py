from abc import ABC, abstractmethod

from sql_code_analyzer.output.enums import OutputType


class _Message(ABC):
    """
    Abstract class providing interface for creating messages.
    """

    @abstractmethod
    def print(self) -> None:
        """
        An abstract method that provides a prescription for
        implementing a method that displays a message on standard output.

        :return: None
        """

        pass


class Reporter(ABC):
    """
    Abstract class providing interface to create a reporter class for a particular purpose.
    """

    report_output = OutputType.Stdout
    report_output_file = None
