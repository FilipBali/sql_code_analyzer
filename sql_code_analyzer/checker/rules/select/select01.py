from sql_code_analyzer.checker.rules.base import BaseRule
from sql_code_analyzer.checker.tools.rule_decorators import include_class_reports
from sql_code_analyzer.in_memory_representation.exceptions import MissingTableException
from sqlglot import expressions as exp

from sql_code_analyzer.in_memory_representation.struct.table import Table

messages = {
    "table-not-exists": {
        "message": "Table \"{name}\" not exists."
    },
    "column-not-exists": {
        "message": "Column \"{name}\" not exists."
    },
}


class UnknownTableRule(BaseRule):
    # persistent = True
    # temporary = True
    # no_code_preview = False

    restrict = {"select"}
    messages = messages

    def __init__(self):
        super().__init__()
        self.inside_from = 0
        self.depth = 1

    @include_class_reports()
    def from_visit(self):
        self.inside_from += self.depth

    @include_class_reports()
    def from_leave(self):
        self.inside_from -= self.depth

    @include_class_reports()
    def table_visit(self):
        if self.inside_from:

            # Get schema name
            schema_name = self.node.db

            # Get table name
            table_name = self.node.name

            try:
                _ = self.mem_rep.get_table_by_name_or_error(schema_name=schema_name, table_name=table_name)
            except MissingTableException:
                self.create_report("table-not-exists", name=self.node.name)


class UnknownColumnRule(BaseRule):
    restrict = {"select"}
    messages = messages

    def __init__(self):
        super().__init__()
        self.inside_select: int = 0
        self.inside_from: int = 0
        self.columns = []
        self.tables = []
        self.depth = 1

    @include_class_reports()
    def select_visit(self):
        self.inside_select += 1
        if len(self.columns) < self.inside_select:
            self.columns.append([])

    @include_class_reports()
    def select_leave(self):
        self.inside_select -= self.depth

    @include_class_reports()
    def column_visit(self):
        if self.inside_select:
            self.columns[self.inside_select-1].append(self.node)

    @include_class_reports()
    def from_visit(self):
        self.inside_from += self.depth
        if len(self.tables) < self.inside_from:
            self.tables.append([])

    @include_class_reports()
    def subquery_visit(self):
        if self.inside_from:
            self.tables[self.inside_from-1].append(self.node)

    # @include_class_reports()
    def table_visit(self):
        if self.inside_from:
            self.tables[self.inside_from-1].append(self.node)

    @include_class_reports()
    def from_leave(self):
        self.inside_from -= 1

        if len(self.columns[self.inside_from]):
            ttables = self.tables[self.inside_from]
            tcolumns = self.columns[self.inside_from]

            for col in tcolumns:
                found = False
                col_alias = col.table
                col_name = col.name

                if col_alias == "":
                    for tab in ttables:

                        # Filter subquery
                        if not isinstance(tab, exp.Table):
                            continue

                        # Get schema name
                        schema_name = tab.db

                        # Get table name
                        table_name = tab.name

                        try:
                            table = self.mem_rep.get_table_by_name_or_error(schema_name=schema_name, table_name=table_name)
                        except MissingTableException:
                            continue

                        if table.check_if_column_exists(column_name=col_name):
                            found = True
                            break

                else:
                    for tab in ttables:
                        if tab.alias == col_alias:

                            # Subquery
                            if isinstance(tab, exp.Subquery):
                                subquery_columns = tab.args['this'].args['expressions']

                                for sub_col in subquery_columns:
                                    if sub_col.name == col_name:
                                        found = True
                                        break
                                continue

                            # Get schema name
                            schema_name = tab.db

                            # Get table name
                            table_name = tab.name

                            try:
                                table = self.mem_rep.get_table_by_name_or_error(schema_name=schema_name,
                                                                                table_name=table_name)
                            except MissingTableException:
                                continue

                            # Check colum in tab
                            if table.check_if_column_exists(column_name=col.name):
                                found = True
                        break

                if not found:
                    self.create_report("column-not-exists", node=col, name=col.name)


def register(checker) -> None:
    checker.register_rule(UnknownTableRule)
    checker.register_rule(UnknownColumnRule)
