#######################################
# File name: column.py
# Purpose: Column class represents database column in table
#
# Key features:
#     Column:
#        Stores: column name
#                column datatype
#                column constrains
#                connection to the table that belongs to
#
######################################

from __future__ import annotations

from sql_code_analyzer.in_memory_representation.struct.base import Base
from sql_code_analyzer.output.reporter.base import ProgramReporter
from sqlglot import expressions as exp

from typing import TYPE_CHECKING, Type

from sqlglot.expressions import DataType

if TYPE_CHECKING:
    from sql_code_analyzer.in_memory_representation.struct.constrain import Constrain
    from sql_code_analyzer.in_memory_representation.struct.table import Table
    from sql_code_analyzer.in_memory_representation.struct.datatype import Datatype


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


class Column(Base):
    """
    TODO Column Description
    Description
    """

    ###################################
    #              INIT
    ###################################

    def __init__(self,
                 identifier,
                 datatype: Datatype,
                 constrains: [Constrain],
                 table: Table,
                 ):
        """
        TODO Description
        :param name:
        :param datatype:
        :param constrains:
        :param table:
        """
        self.name: str = identifier.args['this']
        self.is_name_quoted: bool = identifier.args['quoted']
        self.datatype: Datatype = datatype
        self.constrains: list = constrains
        self.table: Table = table
        self._add_column_to_table()

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, value):
        self._name = value

    @property
    def is_name_quoted(self) -> bool:
        return self._is_name_quoted

    @is_name_quoted.setter
    def is_name_quoted(self, value):
        self._is_name_quoted = value

    @property
    def datatype(self) -> Datatype:
        return self._datatype

    @datatype.setter
    def datatype(self, value):
        self._datatype = value

    @property
    def constrains(self) -> list:
        return self._constrains

    @constrains.setter
    def constrains(self, value):
        self._constrains = value

    @property
    def table(self) -> Table:
        return self._table

    @table.setter
    def table(self, value):
        self._table = value

    def __repr__(self):
        """
        TODO description
        :return:
        """
        return repr("Column "+str(self.name)+" "+str(self.datatype))

    ##################################################
    #                  PRIVATE METHODS
    ##################################################

    #########################
    #          ADD
    #########################
    def _add_column_to_table(self) -> None:
        # Check if not already exists
        if self.table.check_if_column_exists(self.name):
            ProgramReporter.show_error_message(
                message="Column " + self.name+ " already exists."
            )

        self.table.columns[self.name] = self
        self.table.database.index_registration(key=(self.table.schema.name, self.table.name, self.name),
                                         reg_object=self)

    ##################################################
    #                 PUBLIC METHODS
    ##################################################

    #########################
    #      CONSTRAIN
    #########################

    def add_constrain(self, constrain: Constrain) -> None:
        if self.verify_constrain(constrain_type=constrain.__class__):
            ProgramReporter.show_error_message(
                message="Column: " + self.name + "\n"
                        "Constrain " + constrain.__class__.__name__ + " already exists!\n"
                        "This kind modification to memory representation is not allowed."
            )

        self.constrains.append(constrain)

    def delete_constrain(self, constrain: Constrain) -> None:
        if not self.verify_constrain(constrain_type=constrain.__class__):
            ProgramReporter.show_error_message(
                message="Column: " + self.name + "\n"
                        "Constrain " + constrain.__class__.__name__ + " in not exists!\n"
                        "Your code try to delete a constrain that is not exists.\n"
                        "This kind modification to memory representation is not allowed."
            )
        self.get_constrain(constrain_type=constrain.__class__)

    #########################
    #        DATATYPE
    #########################

    def change_datatype(self, new_datatype: Datatype):
        self.datatype = new_datatype

    #########################
    #      DELETE COLUMN
    #########################

    def delete_column(self) -> None:
        """

        :return:
        """
        # Check if column is not part of composite primary key
        if self.table.primary_key.composite:
            if self in self.table.primary_key.columns:
                ProgramReporter.show_error_message(
                    message="Column " + self.name + " is part of primary key and can not be deleted!."
                )

        self.table.database.index_cancel_registration(key=(self.table.schema.name, self.table.name, self.name))
        del self.table.columns[self.name]

    #########################
    #         API
    #########################

    ################
    #     GET
    ################

    def get_constrain(self, constrain_type: Type[Constrain]):
        for constrain in self._constrains:
            if type(constrain) is constrain_type:
                return constrain

        return None

    def get_constrains_count(self) -> int:
        return len(self.constrains)

    def schema(self):
        return self.table.schema

    def database(self):
        return self.table.database

    ################
    #    VERIFY
    ################

    def verify_datatype(self, datatype: DataType.Type) -> bool:
        return datatype is self.datatype.column_datatype

    def verify_constrain(self, constrain_type: Type[Constrain]) -> bool:
        for constrain in self._constrains:
            if type(constrain) is constrain_type:
                return True

        return False

    def verify_constrains_count(self, expected_count) -> bool:
        return len(self.constrains) == expected_count

    def verify_name(self, expected_name) -> bool:
        return self.name == expected_name
