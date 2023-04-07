#######################################
# File name: base.py
# Purpose: Base class contains common functionality for every class which represent some database object
#
# Key features:
#     Base:
#        Stores:
#
#        TODO:
#
#######################################
from sql_code_analyzer.output.reporter.base import ProgramReporter


class Base:
    """
    TODO Description
    """

    @staticmethod
    def check_if_exists(find_attr_val, struct, search_by_attr: str = None) -> bool:
        """
        TODO Description
        :param find_attr_val:
        :param struct:
        :param search_by_attr:
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
    def get_or_create(obj, struct, created_object):
        """
        TODO Description
        :param obj:
        :param struct:
        :param created_object:
        :return:
        """
        is_exists = obj.check_if_exists(obj, struct)

        object_name = obj
        if not isinstance(obj, str):
            object_name = obj.name

        if isinstance(struct, list):
            if is_exists:
                for item in struct:
                    if item.name == object_name:
                        return item
            return created_object

        elif isinstance(struct, dict):
            if is_exists:
                return struct[object_name]
            return created_object

    @staticmethod
    def get_instance_or_error(find_attr_val, find_in_struct, error_message: str, search_by_attr: str = None):
        """
        TODO Description
        :param find_attr_val:
        :param find_in_struct:
        :param error_message:
        :param search_by_attr:
        :return:
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
        TODO Description
        :param find_attr_val:
        :param find_in_struct:
        :param search_by_attr:
        :return:
        """
        if isinstance(find_in_struct, list):
            for item in find_in_struct:
                if find_attr_val in getattr(item, search_by_attr):
                    return item

        elif isinstance(find_in_struct, dict):
            if find_attr_val in find_in_struct:
                return find_in_struct[find_attr_val]

        return None



