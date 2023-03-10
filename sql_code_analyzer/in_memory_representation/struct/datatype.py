from sql_code_analyzer.in_memory_representation.struct.base import Base


class Datatype(Base):
    """
    TODO description
    """

    def __init__(self,
                 column_datatype,
                 value=None):
        """
        TODO description
        :param column_datatype:
        :param value:
        """
        self.column_datatype = column_datatype
        self.value = value

    column_datatype: None
    value: int = None
