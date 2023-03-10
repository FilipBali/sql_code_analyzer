from __future__ import annotations

from sql_code_analyzer.in_memory_representation.struct.base import Base
from sqlglot import expressions as exp

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from sql_code_analyzer.in_memory_representation.struct.constrain import PrimaryKey
    from sql_code_analyzer.in_memory_representation.struct.table import Table
    from sql_code_analyzer.in_memory_representation.struct.datatype import Datatype


class Column(Base):
    """
    TODO Column Description
    Description
    """
    def __init__(self,
                 name: str,
                 datatype: Datatype,
                 table: Table,
                 constrains,
                 primary_key=None,
                 foreign_key=None,
                 unique=None
                 ):
        """
        TODO Description
        :param name:
        :param datatype:
        :param table:
        :param constrains:
        :param primary_key:
        :param foreign_key:
        :param unique:
        """
        self.name = name
        self.datatype = datatype
        self.table = table
        self.constrains = constrains

        if primary_key is not None:
            self.primary_key = primary_key

        if foreign_key is not None:
            self.foreign_key = foreign_key

        if unique is not None:
            self.unique = unique

    def __repr__(self):
        """
        TODO description
        :return:
        """
        return repr("Column "+str(self.name)+" "+str(self.datatype))

    name: str = None
    datatype: Datatype = None
    table: Table = None
    constrains: list = []

    primary_key: bool = False
    foreign_key: bool = False
    unique: bool = False

    def set_primary_key(self, bool_val: bool, constr_pk: PrimaryKey):
        self.primary_key = bool_val
        self.constrains.append(constr_pk)

    def set_foreign_key(self, bool_val: bool):
        self.foreign_key = bool_val

    def set_unique_key(self, bool_val: bool):
        self.unique = bool_val

    def add_constrain(self, constrain) -> None:
        # Pridaj obmedzenie
        self.constrains.append(constrain)


#####################################
#   Column's expected constrains
#####################################
column_constrains_list = (
        exp.Constraint,
        exp.ColumnConstraint,
        exp.AutoIncrementColumnConstraint,
        exp.CaseSpecificColumnConstraint,
        exp.CharacterSetColumnConstraint,
        exp.CheckColumnConstraint,
        exp.CollateColumnConstraint,
        exp.CommentColumnConstraint,
        exp.CompressColumnConstraint,
        exp.DateFormatColumnConstraint,
        exp.DefaultColumnConstraint,
        exp.EncodeColumnConstraint,
        exp.GeneratedAsIdentityColumnConstraint,
        exp.InlineLengthColumnConstraint,
        exp.NotNullColumnConstraint,
        exp.PrimaryKeyColumnConstraint,
        exp.TitleColumnConstraint,
        exp.UniqueColumnConstraint,
        exp.UppercaseColumnConstraint,
        exp.PathColumnConstraint)

