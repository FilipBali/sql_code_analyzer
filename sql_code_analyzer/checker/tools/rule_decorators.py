def include_reports(reports: dict):
    """
    Wraps rule as decorator and provide support for reports creation.
    :param reports: Expecting dict based rules standardised by program manual.
    :return: Rule object
    """

    def decorator(function):
        def function_caller(self, *args):
            function(self, *args)
            return self
        function_caller.include_reports_applied = True
        return function_caller
    return decorator


def include_class_reports():
    """
    Wraps rule as decorator and provide support for reports creation.
    Rules are expected to be stored in class static variable called "reports".
    Expecting dict based rules standardised by program manual.
    :return: Rule object
    """
    def decorator(function):
        def function_caller(self, *args):
            function(self, *args)
            self._verify_presence_report_attr()
            self._create_reporter_reports()
            return self
        function_caller.include_class_reports = True
        return function_caller
    return decorator



