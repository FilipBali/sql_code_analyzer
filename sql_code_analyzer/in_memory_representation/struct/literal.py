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
