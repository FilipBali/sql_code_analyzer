from sql_code_analyzer.linter.linter import Linter
from sql_code_analyzer.output import enums
from sql_code_analyzer.output.terminator.base import Terminator

if __name__ == "__main__":

    Linter()
    Terminator.exit(enums.ExitWith.Success)