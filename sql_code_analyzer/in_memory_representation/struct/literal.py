from sql_code_analyzer.in_memory_representation.struct.base import Base


class Literal(Base):

    def __init__(self,
                 node,
                 ):

        self.value = node.name

        self.is_int = node.is_int
        self.is_number = node.is_number
        self.is_star = node.is_star
        self.is_string = node.is_string
        self.args = node.args

    @property
    def value(self) -> str:
        return self._value

    @value.setter
    def value(self, val):
        self._value = val

    @property
    def is_int(self) -> str:
        return self._is_int

    @is_int.setter
    def is_int(self, val):
        self._is_int = val

    @property
    def is_number(self) -> str:
        return self._is_number

    @is_number.setter
    def is_number(self, val):
        self._is_number = val

    @property
    def is_star(self) -> str:
        return self._is_star

    @is_star.setter
    def is_star(self, val):
        self._is_star = val

    @property
    def is_string(self) -> str:
        return self._is_string

    @is_string.setter
    def is_string(self, val):
        self._is_string = val

    @property
    def args(self) -> str:
        return self._args

    @args.setter
    def args(self, val):
        self._args = val

