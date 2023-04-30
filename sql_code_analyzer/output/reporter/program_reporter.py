from sql_code_analyzer.output import enums
from sql_code_analyzer.output.enums import MessageType, OutputType
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

    def print(self) -> None:
        """
        Implements print of a program message

        :return: None
        """

        self.text = self.color.value + self.text + self._reset + "\n"
        super().print()


class ProgramReporter(Reporter):
    """
    Provides a way to create reports about the program events.
    """

    @staticmethod
    def _create_message(message_type: MessageType, message_text: str):
        """
        Implements creating a message

        :param message_type: Message type (Warning, Error etc.)
        :param message_text: Message text
        :return: Program message object
        """

        return _ProgramMessage(message_type, message_text)

    ##################################
    #         ERROR MESSAGES
    ##################################
    # Error messages terminate the program after giving the reason for the error to the user.
    # Error messages should be used if the program is unable to operate after an event occurs.
    # Message color: red

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
                                        message_text=f"Error (Type integrity): \n{message}").print()

        Terminator.exit(enums.ExitWith.TypeIntegrityError)

    @staticmethod
    def show_missing_property_error_message(message: str) -> None:
        """
        Implementation of a program error message.
        The message is immediately displayed to the user.
        This occurs when missing some property/attribute in user-defined input.

        :param message: Text message
        :return: None
        """

        ProgramReporter._create_message(message_type=MessageType.Error,
                                        message_text=f"Error (Missing property): \n{message}").print()

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
                                        message_text=f"Error: \n{message}").print()

        Terminator.exit(exit_code)

    ##################################
    #        WARNING MESSAGES
    ##################################
    # Warning messages do not terminate the program after giving the reason for the error to the user.
    # Warning messages should be used if the program is able to work after an event occurs.
    # Message color: orange

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
                                        message_text=f"Warning (Type integrity): \n{message}").print()

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
                                        message_text=f"Warning (Missing property): \n{message}").print()

    @staticmethod
    def show_warning_message(message: str) -> None:
        """
        Implementation of a program warning message.
        The message is immediately displayed to the user.

        :param message: Text message
        :return: None
        """

        ProgramReporter._create_message(message_type=MessageType.Warning,
                                        message_text=f"Warning: \n{message}").print()

    ##################################
    #         VERBOSE MESSAGES
    ##################################
    @staticmethod
    def show_verbose_messages(message: str | None,
                              origin: str | None = "Info") -> None:
        """
        Implementation of a program verbose message.
        "Show additional info about the program running."
        The message is immediately displayed to the user.

        :param message: The message
        :param origin: Author/Source/Origin of the message
        :return: None
        """

        if ProgramReporter.verbose < 2:
            return

        if message is None:
            message = ""

        if origin is None:
            origin = ""
        else:
            origin = origin + ": \n"

        ProgramReporter._create_message(message_type=MessageType.Info,
                                        message_text=f"{origin}{message}").print()
