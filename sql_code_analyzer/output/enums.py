import enum


class OutputType(enum.Enum):
    Stdout = 1
    File = 2
    NoReport = 3


class MessageType(enum.Enum):
    Info = "\033[0m"
    Warning = '\033[1;33;48m'
    Error = "\033[31m"


class ExitWith(enum.Enum):
    Success = 0
    InternalError = -1
    ArgumentError = -2
    ParsingError = -3
    ContextError = -4
