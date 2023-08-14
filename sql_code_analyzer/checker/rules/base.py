import ast
import inspect

from sql_code_analyzer.adapter.freature_class.base_cast import BaseCast
from sql_code_analyzer.in_memory_representation.struct.database import Database
from sql_code_analyzer.output.reporter.program_reporter import ProgramReporter
from sql_code_analyzer.output.reporter.rule_reporter import RuleReport
from sql_code_analyzer.tools.path import get_path_object


def calls_create_report(func):
    source = inspect.getsource(func).lstrip()
    tree = ast.parse(source)
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and node.func.attr == 'create_report':
            if isinstance(node.func.value, ast.Name) and node.func.value.id == 'self':
                return True
    return False

class BaseRuleMetaclass(type):
    def __new__(cls, name, bases, dct):
        for item in dct:
            if item.endswith("_visit") or \
                    item.endswith("_leave") or \
                    item == "start_lint" or \
                    item == "end_lint" or \
                    item == "start_statement_lint" or \
                    item == "end_statement_lint":
                func = dct[item]
                if callable(func) and calls_create_report(func=func):
                    if not (getattr(func, 'include_reports_applied', False) or getattr(func, 'include_class_reports', False)):
                        ProgramReporter.show_error_message(
                            message=f"Rule function {item} does not use any decorator! \n"
                                    f"The function is located in the {name} class. \n"
                                    "Program expects to use decorator @include_class_reports or @include_reports. \n"
                                    "Also all functions that's name ends with \"_visit\" or \"_leave\" are expected \n"
                                    "to be use only as rules functions!"
                        )

        return super().__new__(cls, name, bases, dct)


class BaseRule(metaclass=BaseRuleMetaclass):

    def __init__(self):
        self.node = None
        self.mem_rep: Database | None = None
        self.statement: list | None = None
        self.raw_reports = []
        self.reports = []

    @property
    def node(self):
        return self._node

    @node.setter
    def node(self, value):
        self._node = value

    @property
    def mem_rep(self):
        return self._mem_rep

    @mem_rep.setter
    def mem_rep(self, value):
        self._mem_rep = value

    @property
    def statement(self):
        return self._statement

    @statement.setter
    def statement(self, value):
        self._statement = value

    @property
    def messages(self):
        return self._messages

    @messages.setter
    def messages(self, value):
        self._messages = value

    @property
    def raw_reports(self):
        return self._raw_reports

    @raw_reports.setter
    def raw_reports(self, value):
        self._raw_reports = value

    @property
    def reports(self):
        return self._reports

    @reports.setter
    def reports(self, value):
        self._reports = value

    def get_reports(self):
        self.raw_reports.clear()
        treports = []
        for report in self.reports:
            treports.append(report)

        self.reports.clear()

        return treports

    def create_report(self, report: str, node=None, statement=None, underline_entire_line=False, **kwargs):

        if hasattr(self, "no_code_preview"):
            if node is not None:
                self.raw_reports.append(
                   (report, node, not self.no_code_preview, statement, underline_entire_line, kwargs)
                )
            else:
                self.raw_reports.append(
                   (report, self.node, not self.no_code_preview, statement, underline_entire_line, kwargs)
                )
        else:

            if node is not None:
                self.raw_reports.append(
                   (report, node, True, statement, underline_entire_line, kwargs)
                )

            else:
                self.raw_reports.append(
                   (report, self.node, True, statement, underline_entire_line, kwargs)
                )

    def _create_reporter_reports(self):
        for raw_report in self.raw_reports:
            self._validate_raw_report_data(raw_report)
            self._create_rule_report(raw_report)

    @staticmethod
    def _validate_raw_report_data(raw_report):
        report_name = raw_report[0]
        node = raw_report[1]

        if not isinstance(report_name, str):
            ProgramReporter.show_type_integrity_warning_message(
                message="First parameter of create_report method must be name (string) of reporting message."
            )

        if not issubclass(type(node), BaseCast):
            ProgramReporter.show_type_integrity_warning_message(
                message="Second parameter of create_report method must be node of abstract syntax tree."
            )

    def _create_rule_report(self, raw_report):
        message_name = raw_report[0]
        node = raw_report[1]
        code_preview = raw_report[2]
        statement = raw_report[3]
        underline_entire_line = raw_report[4]

        try:
            report_data_dict = self.messages[message_name]

        except (Exception,):
            ProgramReporter.show_missing_property_warning_message(
                message=f"A report called {message_name} does not exists! The report can not be processed.\n"
                        f"Class name: {self._get_class_name()} \n"
                        f"Path: {self.__module__}"
            )
            return

        if not self._verify_messages_data_dict(message_name=message_name,
                                               messages_data_dict=report_data_dict):
            return

        message = report_data_dict["message"]
        for key, value in raw_report[5].items():
            message = report_data_dict["message"].replace("{"+key+"}", value)

        rule_report = RuleReport(
            rule_name=message_name,
            message=message,
            node=node,
            code_preview=code_preview,
            statement=statement,
            underline_entire_line=underline_entire_line,
            rule_class_name=self.__class__.__name__,
            rule_class_filename=get_path_object(self.__class__.__module__).name,
        )

        if rule_report.validate():
            self.reports.append(rule_report)

    def _get_class_name(self) -> str:
        return str(self.__class__.__name__)

    def _verify_presence_report_attr(self):
        if hasattr(self, "messages") and self.messages is not None:
            return

        else:
            ProgramReporter.show_missing_property_warning_message(
                message="Class attribute \"messages\" is not set! Messages from \n"
                        f"{self._get_class_name()} rule are not accepted for now. \n"
                        "Please create and set this attribute when using @include_class_reports decorator."
            )
            self.reports.clear()

    @staticmethod
    def _verify_messages_data_dict(message_name: str, messages_data_dict: dict) -> bool:
        if "message" not in messages_data_dict:
            ProgramReporter.show_missing_property_warning_message(
                message=f"In message {message_name} is missing the message key! \n"
                        "The message can not be processed."
            )
            return False

        if not isinstance(messages_data_dict["message"], str):
            ProgramReporter.show_type_integrity_warning_message(
                message=f"In message {message_name} the content of message key must be string! \n"
                        "The message can not be processed."
            )
            return False

        return True
