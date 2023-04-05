#######################################
# File name: column.py
# Purpose: Column class represents database column in table
#
# Key features:
#     Column:
#        Stores: column name, datatype, constrains, related table
#
#        Methods:
#           Private:
#               __add_column_to_table(self) -> None
#
#           Public:
#               add_constrain(self, constrain: Constrain) -> None
#               delete_constrain(self, constrain_type: Constrain) -> None
#
#               delete_column(self) -> None:
#
#        TODO: Manage datatype, change column name,
#
#
#######################################

from __future__ import annotations

from sql_code_analyzer.in_memory_representation.struct.base import Base
from sql_code_analyzer.output.reporter.base import ProgramReporter
from sqlglot import expressions as exp

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from sql_code_analyzer.in_memory_representation.struct.constrain import Constrain
    from sql_code_analyzer.in_memory_representation.struct.table import Table
    from sql_code_analyzer.in_memory_representation.struct.datatype import Datatype


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
        self.name = identifier.args['this']
        self.is_name_quoted = identifier.args['quoted']
        self.datatype = datatype
        self.constrains = constrains
        self.table = table
        self.__add_column_to_table()

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
    def __add_column_to_table(self) -> None:
        # Check if not already exists
        if self.table.check_if_column_exists(self.name):
            ProgramReporter.show_error_message("Column " + self.name+ " already exists.")

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
        # TODO skontroluj ci dany typ contrainu uz neexistuje
        self.constrains.append(constrain)

    def delete_constrain(self, constrain_type: Constrain) -> None:
        # TODO skontroluj ci dany constrain existuje, potom vymaz
        pass

    #########################
    #         DELETE
    #########################
    def delete_column(self) -> None:
        """

        :return:
        """
        # Check if column is not part of composite primary key
        if self.table.primary_key.composite:
            if self in self.table.primary_key.columns:
                ProgramReporter.show_error_message("Column to delete is part of primary key.")

        self.table.database.index_cancel_registration(key=(self.table.schema.name, self.table.name, self.name))
        del self.table.columns[self.name]


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
