from sql_code_analyzer.output import enums
from sql_code_analyzer.output.enums import MessageType
from sql_code_analyzer.output.reporter.base import _Message, Reporter
from sql_code_analyzer.output.terminator.base import Terminator


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

