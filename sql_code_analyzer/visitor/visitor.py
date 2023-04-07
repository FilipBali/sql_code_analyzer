from abc import ABC, abstractmethod


class Visitor(ABC):
    """
    Abstract class of visitor.
    Visitor visit the object to access their data.
    Then can be called visitor's function visit to execute a logic of visitor.
    Visitor have a specific function what to do with visited objects.
    """

    @abstractmethod
    def visit(self, node):
        """
        Abstract method visit.
        It is called inside visited object to run a specific logic of visitor.

        :param node: Visited object with their data
        :return: None
        """

        pass
