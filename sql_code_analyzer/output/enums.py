import enum


class OutputType(enum.Enum):
    """
    Enumerator for where the program output will be stored.
    """

    Stdout = 1
    File = 2
    Silent = 3


class MessageType(enum.Enum):
    """
    Enumerator for message level/importance.
    Used by Reporter class.
    """

    Info = "\033[0m"
    Warning = '\033[1;33;48m'
    Error = "\033[31m"


class ExitWith(enum.Enum):
    """
    Enumerator for different types of program termination.
    Used by Terminator Class
    """

    Success = 0
    InternalError = -1
    ArgumentError = -2
    ParsingError = -3
    ContextError = -4
    TypeIntegrityError = -5
