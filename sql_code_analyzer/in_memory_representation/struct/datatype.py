from sql_code_analyzer.in_memory_representation.struct.base import Base


class Datatype(Base):
    """
    Represents column datatype in memory representation
    """

    def __init__(self, node, literals: list):
        """
        :param node: Datatype node from abstract syntax tree
        :param literals: List of literal which are define datatype arguments
        """
        self.column_datatype = node.this

        self.literals: list = literals

        self.args = {}
        for arg in node.args:
            if arg not in ["this", "kind", "expressions"]:
                self.args[arg] = node.args[arg]

    @property
    def column_datatype(self):
        return self._column_datatype

    @column_datatype.setter
    def column_datatype(self, value):
        self._column_datatype = value

    @property
    def literals(self) -> list:
        return self._literals

    @literals.setter
    def literals(self, value):
        self._literals = value
