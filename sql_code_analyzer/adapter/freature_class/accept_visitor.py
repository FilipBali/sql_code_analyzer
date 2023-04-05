from __future__ import annotations

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from sql_code_analyzer.visitor.rules_visitor import RulesVisitor


class AcceptVisitor:
    def accept(self, visitor: RulesVisitor):
        visitor.visit(node=self)
