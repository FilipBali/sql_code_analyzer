from __future__ import annotations
from sql_code_analyzer.in_memory_representation.struct.base import Base

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from sql_code_analyzer.in_memory_representation.struct.column import Column
    from sql_code_analyzer.in_memory_representation.struct.table import Table


class Constrain(Base):
    """
    TODO Description
    """
    def set_name(self, name: str):
        """
        TODO Description
        :param name:
        :return:
        """
        self.name = name

    def set_property(self, attr: str, val):
        """
        TODO Description
        :param attr:
        :param val:
        :return:
        """
        setattr(self, attr, val)

    name: str = None
    node = None


class PreventNotNull(Constrain):
    """
    TODO Description
    """
    def __init__(self, column: Column | None, name=None):
        """
        TODO Description
        :param column:
        :param name:
        """
        self.set_name(name)

        self.column = column

    column: Column = None


class PrimaryKey(Constrain):
    """
    TODO Description
    """
    def __init__(self, column: Column | None, name=None):
        """
        TODO Description
        :param column:
        :param name:
        """
        self.set_name(name)

        self.column = column

    column: Column = None


class ForeignKey(Constrain):
    """
    TODO Description
    """
    def __init__(self,
                 fk_columns: [Column],
                 reference_columns: [Column],
                 table_fk,
                 table_ref,
                 name: str = None):
        """
        TODO Description
        :param fk_columns:
        :param reference_columns:
        :param table_fk:
        :param table_ref:
        :param name:
        """
        self.set_name(name)

        self.table_fk: Table = table_fk
        self.table_ref: Table = table_ref

        self.fk_columns = fk_columns
        self.reference_columns = reference_columns

    fk_columns = None
    reference_columns = None

    table_fk: Table = None
    table_ref: Table = None

    def delete_reference(self):
        """
        TODO Description
        :return:
        """
        table_fk_constrains: dict = self.table_fk.constrains
        table_ref_constrains: dict = self.table_ref.constrains

        table_fk_key: tuple = (self.table_fk, self.table_fk)
        table_ref_key: tuple = (self.table_ref, self.table_fk)

        table_fk_constrains[table_fk_key].remove(self)
        table_ref_constrains[table_ref_key].remove(self)

        if len(table_fk_constrains[table_fk_key]) == 0:
            table_fk_constrains.pop(table_fk_key, None)

        if len(table_ref_constrains[table_ref_key]) == 0:
            table_ref_constrains.pop(table_ref_key, None)


class UniqueValue(Constrain):
    """
    TODO Description
    """
    def __init__(self, column: Column, name=None):
        """
        TODO Description
        :param column:
        :param name:
        """
        self.set_name(name)
        self.column = column

    column: Column = None


class DefaultValue(Constrain):
    """
    TODO Description
    """
    def __init__(self, default_value, column: Column | None, name=None):
        """
        TODO Description
        :param default_value:
        :param column:
        :param name:
        """
        self.set_name(name)
        self.default_value = default_value
        self.column = column

    default_value = None
    column = None


class Index(Constrain):
    """
    TODO Description
    """
    def __init__(self, column: Column, name=None):
        """
        TODO Description
        :param column:
        :param name:
        """
        self.set_name(name)
        self.column = column

    column: Column = None


class CheckExpression(Constrain):
    """
    TODO Description
    """
    def __init__(self, expression, name=None):
        """
        TODO Description
        :param expression:
        :param name:
        """
        self.set_name(name)

        self.expression = expression

    expression: str = None


