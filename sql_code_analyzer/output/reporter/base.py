from abc import ABC, abstractmethod

from sql_code_analyzer.adapter.freature_class.base_cast import BaseCast
from sql_code_analyzer.output import enums
from sql_code_analyzer.output.enums import OutputType, MessageType
from sql_code_analyzer.output.terminator.base import Terminator


class _Message(ABC):

    @abstractmethod
    def print(self):
        pass


class _ProgramMessage(_Message):

    def __init__(self,
                 color,
                 text
                 ):
        self.color = color
        self.text = text
        self.reset = "\033[0m"

    def print(self):
        print(self.color.value + self.text + self.reset + "\n")


class _RuleMessage(_Message):

    def __init__(self):
        ...

    def print(self):
        ...


class Reporter(ABC):
    report_output_loc = OutputType.Stdout


class ProgramReporter(Reporter):
    """
    TODO
    """

    @staticmethod
    def _create_message(message_type: MessageType, message_text: str):
        return _ProgramMessage(message_type, message_text)

    @staticmethod
    def show_error_message(message: str, exit_code: enums.ExitWith = enums.ExitWith.InternalError):
        ProgramReporter._create_message(message_type=MessageType.Error,
                                        message_text="Error: " + message).print()
        Terminator.exit(exit_code)

    @staticmethod
    def show_warning_message(message: str):
        ProgramReporter._create_message(message_type=MessageType.Warning,
                                        message_text="Warning: " + message).print()


class RuleReporter(Reporter):
    """
    TODO
    """

    def __init__(self):
        self.messages = []


class RuleReport:
    def __init__(self,
                 rule_id,
                 rule_name,
                 message,
                 node):
        self.rule_id = rule_id
        self.rule_name = rule_name
        self.message = message
        self.node = node

        self._validate_report_data()

    def _validate_report_data(self):
        if not isinstance(self.rule_id, str):
            ProgramReporter.show_warning_message(
                message="Rule ID must be string!"
            )

        if not isinstance(self.rule_name, str):
            ProgramReporter.show_warning_message(
                message="Rule name must be string!"
            )

        if not isinstance(self.message, str):
            ProgramReporter.show_warning_message(
                message="Rule message must be string!"
            )

        if not issubclass(type(self.node), BaseCast):
            ProgramReporter.show_warning_message(
                message="The node must be node of abstract syntax tree."
            )

