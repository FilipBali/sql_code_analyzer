from abc import ABC, abstractmethod


class Visitor(ABC):
    """
    Abstract class of a visitor.
    Visitor visits the object to access their data.
    Then can be called visitor's function visit to execute the logic of visitor.
    Visitor has a specific function what to do with visited objects.
    """

    @abstractmethod
    def visit(self, node):
        """
        Abstract method visit.
        It is called inside a visited object to run specific logic of a visitor.

        :param node: Visit an object with their data
        :return: None
        """

        pass
