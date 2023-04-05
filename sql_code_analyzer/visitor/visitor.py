from abc import ABC, abstractmethod


class Visitor(ABC):

    @abstractmethod
    def visit(self, node):
        pass
