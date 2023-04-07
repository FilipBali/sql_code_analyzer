from __future__ import annotations

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from sql_code_analyzer.visitor.rules_visitor import RulesVisitor


class AcceptVisitor:
    """
    Visitor class which provides accept method.
    This class is inherited by new node classes derived from library node classes.
    The node classes are created dynamically from library classes.
    Library classes provides abstract syntax tree of SQL code.
    """

    def accept(self, visitor: RulesVisitor):
        """
        It is called when visitor want to visit the object.
        The visitor is accepted by object by this function.
        So visited object must have this method.
        In accept method the visitor call its function relevant to object.

        :param visitor: Visitor object
        :return: None
        """
        visitor.visit(node=self)
