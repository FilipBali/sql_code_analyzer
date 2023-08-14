from sql_code_analyzer.checker.rules.base import BaseRule
from sql_code_analyzer.checker.tools.rule_decorators import include_class_reports, include_reports
from sqlglot import expressions as exp

messages = {
    "fk-index-not-exists": {
        "message": "There is no index on foreign key in table {table}."
    },
}


class MissingFKIndex(BaseRule):

    persistent = True
    restrict = {"create_table", "create_index"}
    messages = messages

    def __init__(self):
        super().__init__()
        self.depth = 1
        self.table: str = ""
        self.table_with_fk = []
        self.fk_index = []

    def create_visit(self):
        # Store index
        if self.node.args['kind'].lower() == "index":
            self.fk_index.append(
                (self.node.args['this'].args['table'].name,
                 self.node.args['this'].args['columns'],
                 self.statement)
            )
        # Get table name
        elif self.node.args['kind'].lower() == "table":
            self.table = self.node.this.this.name

    def foreignkey_visit(self):
        # Store table if has foreign key
        self.table_with_fk.append(
            (self.table, self.node.args['expressions'], self.statement)
        )

    @include_class_reports()
    def end_lint(self):
        for table, columns_fk, statement in self.table_with_fk:
            index_list = [x for x in self.fk_index if x[0] == table]

            if len(index_list) == 0:
                ...

            found = False
            for index in index_list:
                indexed_col = index[1]

                if isinstance(indexed_col, exp.Paren):
                    # Only one column

                    # If foreign key has multiple columns,
                    # then it is nonsense to search for its index in index with only one column
                    if len(columns_fk) != 1:
                        continue

                    col_name = indexed_col.this.name
                    table_col = columns_fk[0]
                    if table_col.name == col_name:
                        found = True
                        break  # Break from iterating over indexes

                elif isinstance(indexed_col, exp.Tuple):
                    # Multiple columns

                    cols = indexed_col.expressions
                    cols_names = [x.this.name for x in cols]

                    if len(cols_names) != len(columns_fk):
                        continue

                    c = 1
                    for table_col in columns_fk:
                        if table_col.name not in cols_names:
                            c = 0
                            break

                    found = bool(c)

            if not found:
                self.create_report(report="fk-index-not-exists",
                                   node=columns_fk[0].parent.args['reference'],
                                   statement=statement,
                                   underline_entire_line=True,
                                   table=table
                                   )


def register(checker) -> None:
    checker.register_rule(MissingFKIndex)
