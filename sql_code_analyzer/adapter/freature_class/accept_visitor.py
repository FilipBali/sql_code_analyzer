from __future__ import annotations

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from sql_code_analyzer.visitor.rules_visitor import RulesVisitor


class AcceptVisitor:
    """
    Visitor class which provides accept method.
    This class is inherited by new node classes derived from library node classes.
    The node classes are created dynamically from library classes.
    Library classes provide abstract syntax tree of SQL code.
    """

    def accept(self, visitor: RulesVisitor):
        """
        It is called when a visitor wants to visit the object.
        Object accepts the visitor by this function.
        So a visited object must have this method.
        In accepted method, the visitor calls its function relevant to object.

        :param visitor: Visitor object
        :return: None
        """
        visitor.visit(node=self)
