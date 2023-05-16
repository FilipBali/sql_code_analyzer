from __future__ import annotations
from sql_code_analyzer.in_memory_representation.struct.base import Base

from typing import TYPE_CHECKING, List

if TYPE_CHECKING:
    from sql_code_analyzer.in_memory_representation.struct.column import Column
    from sql_code_analyzer.in_memory_representation.struct.table import Table


class Constrain(Base):
    """
    This class provides a constraint-specific interface to children classes
    """

    def __init__(self):
        self.name: str = ""

    def set_name(self, name: str) -> None:
        """
        Set name of constraint if needed
        :param name: Name of constraint if needed
        :return: None
        """

        self.name: str = name

    def set_property(self, attr: str, val) -> None:
        """
        Dynamically set property in instance
        :param attr: Attribute name
        :param val: Attribute value
        :return: None
        """

        setattr(self, attr, val)


class PreventNotNull(Constrain):
    """
    Represent NOT NULL constraint in memory representation
    """

    def __init__(self, column: Column | None, name=None):
        """
        :param column: Column to which the restriction applies
        :param name: Name of constraint if needed
        """

        super().__init__()
        self.set_name(name)

        self.column = column


class PrimaryKey(Constrain):
    """
    Represent constraint PRIMARY KEY in memory representation
    """
    def __init__(self, columns: list):
        """
        :param columns: Columns to which the restriction applies
        """

        super().__init__()
        if len(columns) > 1:
            self.composite = True

        self.columns = columns


class ForeignKey(Constrain):
    """
    Represent FOREIGN KEY constraint in memory representation
    """
    def __init__(self, fk_columns: [Column], reference_columns: [Column], table_fk, table_ref, name: str = None):
        """
        :param fk_columns: List of columns represents foreign key
        :param reference_columns: List of columns to which foreign key references
        :param table_fk: Table that have foreign key
        :param table_ref: Table that have reference columns
        :param name: Name of constraint if needed
        """

        super().__init__()
        self.set_name(name)

        self.table_fk: Table = table_fk
        self.table_ref: Table = table_ref

        self.fk_columns = fk_columns
        self.reference_columns = reference_columns

    def delete_reference(self) -> None:
        """
        Deletes reference of FOREIGN KEY in memory representation
        :return: None
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
    Represent UNIQUE constraint in memory representation
    """
    def __init__(self, column: Column, primary_key=False, name=None):
        """
        :param column: Column to which the restriction applies
        :param name: Constraint name if needed
        """

        super().__init__()
        self.set_name(name)
        self.column = column
        self.primary_key = primary_key

        if self.primary_key:
            self.column.constrains.append(PreventNotNull(column=self.column))


class DefaultValue(Constrain):
    """
    Represent DEFAULT constraint in memory representation
    """
    def __init__(self, default_value, column: Column | None, name=None):
        """
        :param default_value: Default value of constraint
        :param column: Column to which the restriction applies
        :param name: Constraint name if needed
        """

        super().__init__()
        self.set_name(name)
        self.default_value = default_value
        self.column = column


class Index(Constrain):
    """
    Represent INDEX in memory representation
    """
    def __init__(self, name: str, columns: List[Column]):
        """
        :param columns: Columns to which the restriction applies
        :param name: Constraint name if needed
        """

        super().__init__()
        self.set_name(name)
        self.columns = columns


class CheckExpression(Constrain):
    """
    Represent CHECK constraint in memory representation
    """
    def __init__(self, expression, name=None):
        """
        :param expression: Representation of condition
        :param name: Constraint name if needed
        """

        super().__init__()
        self.set_name(name)

        self.expression = expression
