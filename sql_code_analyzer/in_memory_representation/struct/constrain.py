from __future__ import annotations
from sql_code_analyzer.in_memory_representation.struct.base import Base

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from sql_code_analyzer.in_memory_representation.struct.column import Column
    from sql_code_analyzer.in_memory_representation.struct.table import Table


class Constrain(Base):
    """
    This class provides constrain specific interface to children classes
    """

    def __init__(self):
        self.name: str = ""

    def set_name(self, name: str) -> None:
        """
        Set name of constrain if needed
        :param name: Name of constrain if needed
        :return: None
        """

        self.name: str = name

    def set_property(self, attr: str, val) -> None:
        """
        Dynamically set property in instnace
        :param attr: Attribute name
        :param val: Attribute value
        :return: None
        """

        setattr(self, attr, val)


class PreventNotNull(Constrain):
    """
    Represent NOT NULL constrain in memory representation
    """

    def __init__(self, column: Column | None, name=None):
        """
        :param column: Column to which the restriction applies
        :param name: Name of constrain if needed
        """

        super().__init__()
        self.set_name(name)

        self.column = column


class PrimaryKey(Constrain):
    """
    Represent constrain PRIMARY KEY in memory representation
    """
    def __init__(self, columns: list):
        """
        :param columns: Columns to which the restriction applies
        """

        super().__init__()
        if len(columns) > 1:
            self.composite = True

            # TODO set COLUMN UNIQUE if not already
            # TODO set COLUMN NOT NULL if not already
            # TODO pri vymazavani not null alebo unique pozri ci neni samostatny primary key !!

        self.columns = columns


class ForeignKey(Constrain):
    """
    Represent FOREIGN KEY constrain in memory representation
    """
    def __init__(self, fk_columns: [Column], reference_columns: [Column], table_fk, table_ref, name: str = None):
        """
        TODO Description
        :param fk_columns:
        :param reference_columns:
        :param table_fk:
        :param table_ref:
        :param name: Name of constrain if needed
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
    Represent UNIQUE constrain in memory representation
    """
    def __init__(self, column: Column, primary_key=False, name=None):
        """
        :param column: Column to which the restriction applies
        :param name: Name of constrain if needed
        """

        super().__init__()
        self.set_name(name)
        self.column = column
        self.primary_key = primary_key

        if self.primary_key:
            self.column.constrains.append(PreventNotNull(column=self.column))


class DefaultValue(Constrain):
    """
    Represent DEFAULT constrain in memory representation
    """
    def __init__(self, default_value, column: Column | None, name=None):
        """
        :param default_value: Default value of constrain
        :param column: Column to which the restriction applies
        :param name: Name of constrain if needed
        """

        super().__init__()
        self.set_name(name)
        self.default_value = default_value
        self.column = column


class Index(Constrain):
    """
    Represent INDEX in memory representation
    """
    def __init__(self, column: Column, name=None):
        """
        :param column: Column to which the restriction applies
        :param name: Name of constrain if needed
        """

        super().__init__()
        self.set_name(name)
        self.column = column


class CheckExpression(Constrain):
    """
    Represent CHECK constrain in memory representation
    """
    def __init__(self, expression, name=None):
        """
        :param expression: Representation of condition
        :param name: Name of constrain if needed
        """

        super().__init__()
        self.set_name(name)

        self.expression = expression
