from sql_code_analyzer.adapter.base_class import BaseClass
from sql_code_analyzer.adapter.freature_class.base_cast import BaseCast
from sql_code_analyzer.output.reporter.program_reporter import ProgramReporter
from sql_code_analyzer.output.reporter.rule_reporter import RuleReport


class BaseRuleMetaclass(type):
    def __new__(cls, name, bases, dct):
        for item in dct:
            if item.endswith("_visit") or item.endswith("_leave"):
                func = dct[item]
                if callable(func):
                    if not (getattr(func, 'include_reports_applied', False) or getattr(func, 'include_class_reports', False)):
                        ProgramReporter.show_error_message(
                            message="Rule function " + item + " does not use any decorator! \n"
                                    "The function is located in the " + name + " class. \n"
                                    "Program expects to use decorator @include_class_reports or @include_reports. \n"
                                    "Also all functions that's name ends with \"_visit\" or \"_leave\" are expected \n"
                                    "to be use only as rules functions!"
                        )

        return super().__new__(cls, name, bases, dct)


class BaseRule(metaclass=BaseRuleMetaclass):

    _raw_reports = []
    _reports = []

    reports = None

    def get_reports(self):
        self._raw_reports.clear()
        return [self._reports.pop() for _ in self._reports]

    def create_report(self, report: str, node: BaseClass):
        self._raw_reports.append(
           (report, node)
        )

    def _create_reporter_reports(self):
        for raw_report in self._raw_reports:
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
        report_name = raw_report[0]
        node = raw_report[1]

        try:
            report_data_dict = self.reports[report_name]

        except (Exception,):
            ProgramReporter.show_missing_property_warning_message(
                message="A report called " + report_name + " does not exists! The report can not be processed.\n"
                        "Class name: " + self._get_class_name() + "\n"
                        "Path: " + self.__module__
            )
            return

        if not self._verify_report_data_dict(report_name=report_name,
                                             report_data_dict=report_data_dict):
            return

        self._reports.append(
            RuleReport(
                rule_id=report_data_dict["id"],
                rule_name=report_name,
                message=report_data_dict["message"],
                node=node
            )
        )

    def _get_class_name(self) -> str:
        return str(self.__class__.__name__)

    def _verify_presence_report_attr(self):
        if hasattr(self, "reports") and self.reports is not None:
            return

        else:
            ProgramReporter.show_missing_property_warning_message(
                message="Class attribute \"reports\" is not set! Reports from \n"
                        + self._get_class_name() + " rule are not accepted for now. \n" +
                        "Please create and set this attribute when using @include_class_reports decorator."
            )
            self._reports.clear()

    @staticmethod
    def _verify_report_data_dict(report_name: str, report_data_dict: dict) -> bool:
        if "id" not in report_data_dict:
            ProgramReporter.show_missing_property_warning_message(
                message="In report " + report_name + " is missing the id key! \n"
                        "The report can not be processed."
            )
            return False

        if not isinstance(report_data_dict["id"], str):
            ProgramReporter.show_type_integrity_warning_message(
                message="In report " + report_name + " the content of id key must be string! \n"
                        "The report can not be processed."
            )
            return False

        if "message" not in report_data_dict:
            ProgramReporter.show_missing_property_warning_message(
                message="In report " + report_name + " is missing the message key! \n"
                        "The report can not be processed."
            )
            return False

        if not isinstance(report_data_dict["message"], str):
            ProgramReporter.show_type_integrity_warning_message(
                message="In report " + report_name + " the content of message key must be string! \n"
                        "The report can not be processed."
            )
            return False

        return True
