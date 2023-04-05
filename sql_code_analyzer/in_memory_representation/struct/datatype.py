from sql_code_analyzer.in_memory_representation.struct.base import Base


class Datatype(Base):
    """
    TODO description
    """

    def __init__(self,
                 node,
                 literals: list):
        """
        TODO description
        :param column_datatype:
        :param value:
        """
        self.column_datatype = node.this

        self.literals = literals

        self.args = {}
        for arg in node.args:
            if arg not in ["this", "kind", "expressions"]:
                self.args[arg] = node.args[arg]
