import sqlglot as sg

from test_cases.sqlglot import test_suite

def run_tests():
    for name, test_sql in test_suite.__dict__.items():
        if name.startswith("test_sql_00") and callable(test_sql):
            print("==================== " + name + " ====================")
            sql = test_sql()
            # tokenizer_ret = Tokenizer().tokenize(sql)

            parsed_sql = sg.parse_one(sql)

            generator = parsed_sql.walk(bfs=True)

            counter = 1
            for content in generator:
                for val in content:
                    if not (val is None or isinstance(val, str)):
                        if not hasattr(val, 'code_location'):
                            print(str(counter) + " Error " + val.name)
                            counter = counter + 1
