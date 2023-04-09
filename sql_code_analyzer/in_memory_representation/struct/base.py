#######################################
# File name: base.py
# Purpose: Base class contains common functionality for every class which represent some database object
#
#######################################
from sql_code_analyzer.output.reporter.base import ProgramReporter


class Base:
    """
    Base class contains common functionality for every class which represent some database object
    """

    @staticmethod
    def check_if_exists(find_attr_val, struct, search_by_attr: str = None) -> bool:
        """
        Dynamically checks if exists value in structure
        :param find_attr_val: Value that will be searched for
        :param struct: Structure where the search will take place
        :param search_by_attr: Attribute name if necessary
        :return:
        """
        if isinstance(struct, list):
            if search_by_attr is None:
                ProgramReporter.show_error_message(
                    message="Internal error: check_if_exists method has not defined \n"
                            "search_by_attr parameter while searching in list structure."
                )

            for item in struct:
                if find_attr_val in getattr(item, search_by_attr):
                    return True
            return False

        elif isinstance(struct, dict):
            if find_attr_val in struct:
                return True
            return False

    @staticmethod
    def get_instance_or_error(find_attr_val, find_in_struct, error_message: str, search_by_attr: str = None):
        """
        Return instance of an object if exists or raise error
        :param find_attr_val: Value that will be searched for
        :param find_in_struct: Structure where the search will take place
        :param error_message: An error message in case instance not exists
        :param search_by_attr: Attribute name if necessary
        :return: Instance or raise error
        """
        if isinstance(find_in_struct, list):
            for item in find_in_struct:
                if find_attr_val in getattr(item, search_by_attr):
                    return item

        elif isinstance(find_in_struct, dict):
            if find_attr_val in find_in_struct:
                return find_in_struct[find_attr_val]

        ProgramReporter.show_error_message(error_message)

    @staticmethod
    def get_instance_or_none(find_attr_val, find_in_struct, search_by_attr: str = None):
        """
        Return instance of an object if exists or return None
        :param find_attr_val: Value that will be searched for
        :param find_in_struct: Structure where the search will take place
        :param search_by_attr: Attribute name if necessary
        :return: Instance or None
        """
        if isinstance(find_in_struct, list):
            for item in find_in_struct:
                if find_attr_val in getattr(item, search_by_attr):
                    return item

        elif isinstance(find_in_struct, dict):
            if find_attr_val in find_in_struct:
                return find_in_struct[find_attr_val]

        return None
