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
    Represents table column in memory representation
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
        :param identifier: Node
        :param datatype: Column datatype
        :param constrains: List of column constrains
        :param table: The table to which the column belongs
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
        return repr("Column "+str(self.name)+" "+str(self.datatype))

    ##################################################
    #                  PRIVATE METHODS
    ##################################################

    #########################
    #          ADD
    #########################
    def _add_column_to_table(self) -> None:
        """
        Adds a column to the table to which it belongs
        :return: None
        """

        # Check if not already exists
        if self.table.check_if_column_exists(self.name):
            ProgramReporter.show_error_message(
                message="Column " + self.name + " already exists."
            )

        self.table.columns[self.name] = self
        self.table.database.index_registration(key=(self.table.schema.name, self.table.name, self.name),
                                         reg_object=self)

    ##################################################
    #                 PUBLIC METHODS
    #############################   #####################

    #########################
    #      CONSTRAINT
    #########################

    def add_constrain(self, constrain: Constrain) -> None:
        """
        Adds a constraint to the column
        :param constrain: The constraint object
        :return: None
        """

        if self.verify_constrain(constrain_type=constrain.__class__):
            ProgramReporter.show_error_message(
                message="Column: " + self.name + "\n"
                        "Constraint " + constrain.__class__.__name__ + " already exists!\n"
                        "This kind modification to memory representation is not allowed."
            )

        self.constrains.append(constrain)

    def delete_constrain(self, constrain: Constrain) -> None:
        """
        Delete a column to the table to which it belongs
        :param constrain: The constraint object
        :return: None
        """

        if not self.verify_constrain(constrain_type=constrain.__class__):
            ProgramReporter.show_error_message(
                message="Column: " + self.name + "\n"
                        "Constrain " + constrain.__class__.__name__ + " in not exists!\n"
                        "Your code try to delete a constraint that is not exists.\n"
                        "This kind modification to memory representation is not allowed."
            )
        self.get_constrain(constrain_type=constrain.__class__)

    #########################
    #        DATATYPE
    #########################

    def change_datatype(self, new_datatype: Datatype) -> None:
        """
        Change datatype of column
        :param new_datatype: The datatype object
        :return: None
        """

        self.datatype = new_datatype

    #########################
    #      DELETE COLUMN
    #########################

    def delete_column(self) -> None:
        """
        Delete column from memory representation
        :return: None
        """

        # Check if column is not part of a composite primary key
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

    def get_constrain(self, constrain_type: Type[Constrain]) -> Constrain | None:
        """
        Get constraint from a list of constrained
        :param constrain_type: Constraint type (for example, PreventNotNull)
        :return: The constraint or None
        """

        for constrain in self._constrains:
            if type(constrain) is constrain_type:
                return constrain

        return None

    def get_constrains_count(self) -> int:
        """
        Return count of constraint which is belonged to column
        :return: Count of constrains
        """

        return len(self.constrains)

    def schema(self):
        """
        Returns the schema to which it belongs
        :return:
        """

        return self.table.schema

    def database(self):
        """
        Returns the database to which it belongs
        :return:
        """

        return self.table.database

    ################
    #    VERIFY
    ################

    def verify_datatype(self, datatype: DataType.Type) -> bool:
        """
        Return True if column has this datatype otherwise False
        :param datatype: The datatype
        :return: True/False
        """

        return datatype is self.datatype.column_datatype

    def verify_constrain(self, constrain_type: Type[Constrain]) -> bool:
        """
        Return True if column has this type of constraint otherwise False
        :param constrain_type: The constraint type
        :return: True/False
        """

        for constrain in self._constrains:
            if type(constrain) is constrain_type:
                return True

        return False

    def verify_constrains_count(self, expected_count) -> bool:
        """
        Return True if column has this count of constrains otherwise False
        :param expected_count: Expected count
        :return: True/False
        """
        return len(self.constrains) == expected_count

    def verify_name(self, expected_name) -> bool:
        """
        Return True if column has this name otherwise False
        :param expected_name: The name
        :return: True/False
        """

        return self.name == expected_name
