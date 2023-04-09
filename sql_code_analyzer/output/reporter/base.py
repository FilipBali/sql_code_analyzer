from abc import ABC, abstractmethod

from sql_code_analyzer.adapter.freature_class.base_cast import BaseCast
from sql_code_analyzer.output import enums
from sql_code_analyzer.output.enums import OutputType, MessageType
from sql_code_analyzer.output.terminator.base import Terminator


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


class _ProgramMessage(_Message):
    """
    Provides an interface to create a message about program running.
    """

    def __init__(self,
                 color,
                 text
                 ):
        """
        Initialise of ProgramMessage instance

        :param color: Message color
        :param text: Message text
        """

        self.color = color
        self.text = text
        self.reset = "\033[0m"

    def print(self) -> None:
        """
        Implements print to standard output

        :return: None
        """

        print(self.color.value + self.text + self.reset + "\n")


class _RuleMessage(_Message):

    def __init__(self):
        ...

    def print(self):
        ...


class Reporter(ABC):
    """
    Abstract class providing interface to create a reporter class for a particular purpose.
    """

    report_output = OutputType.Stdout
    report_output_file = None


class ProgramReporter(Reporter):
    """
    Provides a way to create reports about the program events.
    """

    verbose = False

    @staticmethod
    def _create_message(message_type: MessageType, message_text: str):
        """
        Implements creating a message

        :param message_type: Message type (Warning, Error etc.)
        :param message_text: Message text
        :return: Program message object
        """

        return _ProgramMessage(message_type, message_text)

    @staticmethod
    def show_type_integrity_error_message(message: str) -> None:
        """
        Implementation of program error message
        The message is immediately displayed to the user.
        This occurs when the integrity of the code is compromised.
        For example, if function arguments are not met with requirements (Expected list but string is passed).

        :param message: Text message
        :return: None
        """

        ProgramReporter._create_message(message_type=MessageType.Error,
                                        message_text="Error (Type integrity): \n" + message).print()
        Terminator.exit(enums.ExitWith.TypeIntegrityError)

    @staticmethod
    def show_missing_property_error_message(message: str) -> None:
        """
        Implementation of program error message
        The message is immediately displayed to the user.
        This occurs when missing some property/attribute in user-defined input.

        :param message: Text message
        :return: None
        """

        ProgramReporter._create_message(message_type=MessageType.Error,
                                        message_text="Error (Missing property): \n" + message).print()
        Terminator.exit(enums.ExitWith.TypeIntegrityError)

    @staticmethod
    def show_error_message(message: str, exit_code: enums.ExitWith = enums.ExitWith.InternalError) -> None:
        """
        Implementation of program error message
        The message is immediately displayed to the user.

        :param message: Text message
        :param exit_code: Exit code with which the program will be terminated
        :return: None
        """

        ProgramReporter._create_message(message_type=MessageType.Error,
                                        message_text="Error: \n" + message).print()
        Terminator.exit(exit_code)

    @staticmethod
    def show_type_integrity_warning_message(message: str) -> None:
        """
        Implementation of a program type integrity warning message.
        The message is immediately displayed to the user.
        For example, if function arguments are not met with requirements (Expected list but string is passed).


        :param message: Text message
        :return: None
        """

        ProgramReporter._create_message(message_type=MessageType.Warning,
                                        message_text="Warning (Type integrity): \n"
                                                     + message).print()

    @staticmethod
    def show_missing_property_warning_message(message: str) -> None:
        """
        Implementation of a program type integrity warning message.
        The message is immediately displayed to the user.
        This occurs when missing some property/attribute in user-defined input.

        :param message: Text message
        :return: None
        """

        ProgramReporter._create_message(message_type=MessageType.Warning,
                                        message_text="Warning (Missing property): \n"
                                                     + message).print()

    @staticmethod
    def show_warning_message(message: str) -> None:
        """
        Implementation of a program warning message.
        The message is immediately displayed to the user.

        :param message: Text message
        :return: None
        """

        ProgramReporter._create_message(message_type=MessageType.Warning,
                                        message_text="Warning: \n" + message).print()

    @staticmethod
    def show_verbose_messages(message_list: [str],
                              origin: str = "Info",
                              head_message: str = "",
                              tail_message: str = "") -> None:
        """
        Implementation of a program verbose message.
        "Show additional info about program running."
        The message is immediately displayed to the user.

        :param message_list: List of message
        :param origin: Author/Source/Origin of the message
        :param head_message: Introductory message
        :param tail_message: Closing message
        :return: None
        """

        if not ProgramReporter.verbose:
            return

        if origin != "":
            ProgramReporter._create_message(message_type=MessageType.Info,
                                            message_text=origin + ": ").print()
        if head_message != "":
            ProgramReporter._create_message(message_type=MessageType.Info,
                                            message_text=head_message).print()

        for message in message_list:
            ProgramReporter._create_message(message_type=MessageType.Info,
                                            message_text=message).print()

        if tail_message != "":
            ProgramReporter._create_message(message_type=MessageType.Info,
                                            message_text=tail_message).print()


class RuleReporter(Reporter):
    """
    Class which provides a way of reporting rule reports to user.
    """

    def __init__(self):
        self.messages = []


class RuleReport:
    """
    Class of rule report which encapsulates the report generated by the rule.
    """

    def __init__(self,
                 rule_id,
                 rule_name,
                 message,
                 node):
        """
        Generate rule report object
        :param rule_id: Rule ID defined by rule.
        :param rule_name: Rule name defined by rule.
        :param message: Rule message defined by rule.
        :param node: The specific node where the message is created.
        """

        self.rule_id = rule_id
        self.rule_name = rule_name
        self.message = message
        self.node = node

        self._validate_report_data()

    def _validate_report_data(self) -> None:
        """
        Verify if all necessary class properties are set.
        :return: None
        """

        # TODO implements report deletion if the requirements are not met.

        if not isinstance(self.rule_id, str):
            ProgramReporter.show_type_integrity_warning_message(
                message="Rule ID must be string!"
            )

        if not isinstance(self.rule_name, str):
            ProgramReporter.show_type_integrity_warning_message(
                message="Rule name must be string!"
            )

        if not isinstance(self.message, str):
            ProgramReporter.show_type_integrity_warning_message(
                message="Rule message must be string!"
            )

        if not issubclass(type(self.node), BaseCast):
            ProgramReporter.show_type_integrity_warning_message(
                message="The node must be node of abstract syntax tree."
            )
