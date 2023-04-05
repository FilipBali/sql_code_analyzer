import glob
import importlib.util
import inspect
import os
import pickle
from queue import Queue

###############################################
#              sqlglot's IMPORT
###############################################
import sqlglot
from sql_code_analyzer.tools.get_program_root_path import get_program_root_path
from sql_code_analyzer.tools.get_value_based_on_key_dict import get_value_based_on_key_dict
from sqlglot import expressions as exp

###############################################
#          sql_code_analyzer's IMPORT
###############################################

from sql_code_analyzer.adapter.adapt_ast import adapt_ast
from sql_code_analyzer.checker.tools.rules_handler import CRules
from sql_code_analyzer.in_memory_representation.struct.database import Database
from sql_code_analyzer.in_memory_representation.tools.ast_manipulation import get_next_node
from sql_code_analyzer.input.args_handler import CArgs
from sql_code_analyzer.output import enums
from sql_code_analyzer.output.terminator.base import Terminator

################################
#    MODIFY DATABASE ACTIONS
################################
from sql_code_analyzer.in_memory_representation.actions.modify_representation.database.create_database import create_database
from sql_code_analyzer.in_memory_representation.actions.modify_representation.database.alter_database import alter_database
from sql_code_analyzer.in_memory_representation.actions.modify_representation.database.drop_database import drop_database

from sql_code_analyzer.in_memory_representation.actions.modify_representation.index.alter_index import alter_index
from sql_code_analyzer.in_memory_representation.actions.modify_representation.index.create_index import create_index
from sql_code_analyzer.in_memory_representation.actions.modify_representation.index.drop_index import drop_index
from sql_code_analyzer.in_memory_representation.actions.modify_representation.schema.alter_schema import alter_schema
from sql_code_analyzer.in_memory_representation.actions.modify_representation.schema.create_schema import create_schema
from sql_code_analyzer.in_memory_representation.actions.modify_representation.schema.drop_schema import drop_schema
from sql_code_analyzer.in_memory_representation.actions.modify_representation.table.alter_table import alter_table
from sql_code_analyzer.in_memory_representation.actions.modify_representation.table.drop_table import drop_table
from sql_code_analyzer.in_memory_representation.actions.modify_representation.table.create_table import create_table

################################
#           OUTPUT
################################
from sql_code_analyzer.output.reporter.base import ProgramReporter
from sql_code_analyzer.visitor.rules_visitor import RulesVisitor


class Linter:

    def __init__(self):

        self._modify_representation_functions = {}

        self._init_program_argument_class()
        self._init_rules_class()
        self._init_memory_database_representation()
        self._get_modify_representation_statements()
        self._sql_statements_processing()
        self._make_serialization()
        Terminator.exit(enums.ExitWith.Success)

    def _init_program_argument_class(self):
        # get data from program input and init class for arguments
        self.args_data = CArgs()

    def _init_rules_class(self):
        # init rules class
        self.rules_args_data = CRules(path_to_rules_folder=self.args_data.rules_path,
                                      include_folders=self.args_data.include_folders,
                                      exclude_folders=self.args_data.exclude_folders)

    def _init_memory_database_representation(self):
        if self.args_data.deserialization_path is not None:
            # Provide deserialization memory representation from file and initialise database structure
            self.mem_rep: Database = Database() \
                .load_deserialization_path(deserialization_path=self.args_data.deserialization_path)
        else:
            # initialise in memory representation
            self.mem_rep: Database = Database("MemoryDB").set_default_scheme()

    def _check_if_modifying_statement(self) -> bool:
        # TODO Refractor to check if isinstance of class for example exp.Create?
        # Before doing that it must be done problem with alter statements
        # Because they have inconsistent naming.. key=AlterTable not key=Alter, kind=Table
        if hasattr(self.ast, "key"):
            if self.ast.key.lower() in ["create_", "alter_", "altertable_", "drop_", "insert_", "update_", "delete_"]:
                return True

        return False

    def _sql_statements_processing(self):
        # iterate over SQL statements
        for statement in self.args_data.statements:

            self.ast, self.tokens = sqlglot.parse_one(statement)

            self._include_code_locations()

            ast_ast = self.ast.walk(bfs=False)

            for nodes in ast_ast:
                if nodes is not None:
                    node = nodes[0]
                    if node.code_location is None:
                        print(node)
                    else:
                        print(str(node) + " " + str(node.code_location))

            self.ast = adapt_ast(self.ast)
            self._lint_statement()

            # provide changes based on SQL statement to memory representation
            if self._check_if_modifying_statement():
                self._modify_representation()

    def _include_code_locations(self):
        ast_gen = self.ast.walk(bfs=False)

        for nodes in ast_gen:
            if nodes is not None:
                nodes[0].code_location = None

        ast_gen = self.ast.walk(bfs=False)

        seen_tokens = []
        for nodes in ast_gen:
            if nodes is not None:
                node = nodes[0]
                node_name = node.name
                node_key = node.key

                to_del = []

                found = False
                for token in self.tokens:
                    if token.text.lower() == node_name.lower() or \
                            token.text.lower() == node_key.lower():
                        node.code_location = {"line": token.line,
                                              "col": token.col}
                        found = True
                        break

                    to_del.append(token)

                if found:
                    seen_tokens = to_del + seen_tokens
                    for token_to_del in to_del:
                        self.tokens.remove(token_to_del)

                else:
                    for stoken in seen_tokens:
                        if stoken.text.lower() == node_name.lower() or \
                                stoken.text.lower() == node_key.lower():
                            node.code_location = {"line": stoken.line,
                                                  "col": stoken.col}
                            break

    def _lint_statement(self):
        ast_generator = self._get_generator_based_on_statement()
        visited_nodes = Queue()

        expect_set = self._create_restriction_set_from_statement()

        rules_visitor = RulesVisitor(rules_args_data=self.rules_args_data,
                                     expect_set=expect_set)

        stop_parse = False
        while 1 and stop_parse is not True:

            # get node
            node, nodes, stop_parse = get_next_node(visited_nodes=visited_nodes,
                                                    ast_generator=ast_generator)

            if node is None:
                rules_visitor.traversing_ast_done()
            else:
                node.accept(rules_visitor)

    def _create_restriction_set_from_statement(self):
        expect_set = set()
        if hasattr(self.ast, "key") and \
                "kind" in self.ast.args and \
                self.ast.args["kind"] is not None:

            statement: str = self.ast.key.lower() + self.ast.args["kind"].lower()
            expect_set.add(statement)
            head, tail = statement.split("_")
            expect_set.add(head)
            expect_set.add(tail)

        elif hasattr(self.ast, "key"):
            statement: str = self.ast.key.lower()
            expect_set.add(statement)
            head, tail = statement.split("_")
            expect_set.add(head)

        return expect_set

    def _modify_representation(self):
        """
        TODO description
        :return:
        """
        if hasattr(self.ast, "key") and "kind" in self.ast.args and self.ast.args["kind"] is not None:

            statement: str = self.ast.key.lower() + self.ast.args["kind"].lower()

            if statement in self._modify_representation_functions:
                function = self._modify_representation_functions[statement]
                function(ast=self.ast, mem_rep=self.mem_rep)

            else:
                print(self.ast.key.upper()[:-1] + " " + self.ast.args["kind"].upper() + " is not supported")

        elif hasattr(self.ast, "key") and self.ast.key == "altertable_":
            function = self._modify_representation_functions["alter_table"]
            function(self.ast, self.mem_rep)

        else:
            ProgramReporter.show_error_message("Unknown command.")

    def _get_generator_based_on_statement(self):
        if not isinstance(self.ast, exp.Select):
            return self.ast.walk(bfs=False)

        clause = {
            "SELECT": [],
            "FROM": [],
            "WHERE": [],
            "GROUP_BY": [],
            "HAVING": [],
            "ORDER_BY": []
        }

        visited_nodes = Queue()
        ast_generator = self.ast.walk(bfs=False)

        branch = None
        known_branch = [exp.Select,
                        exp.From,
                        exp.Where,
                        exp.Group,
                        exp.Having,
                        exp.Order]

        stop_parse = False
        while 1 and stop_parse is not True:
            # get node
            node, nodes, stop_parse = get_next_node(visited_nodes=visited_nodes,
                                                    ast_generator=ast_generator)

            if node is None:
                break

            if any([isinstance(node, item) for item in known_branch]):
                branch = node

            if isinstance(branch, exp.Select):
                clause["SELECT"].append(nodes)

            elif isinstance(branch, exp.From):
                clause["FROM"].append(nodes)

            elif isinstance(branch, exp.Where):
                clause["WHERE"].append(nodes)

            elif isinstance(branch, exp.Group):
                clause["GROUP_BY"].append(nodes)

            elif isinstance(branch, exp.Having):
                clause["HAVING"].append(nodes)

            elif isinstance(branch, exp.Order):
                clause["ORDER_BY"].append(nodes)

            else:
                print(node.key)

        database_evaluate_order = clause["FROM"] + \
            clause["WHERE"] + \
            clause["GROUP_BY"] + \
            clause["HAVING"] + \
            clause["SELECT"] + \
            clause["ORDER_BY"]

        return self._create_generator_from_list(database_evaluate_order)

    @staticmethod
    def _create_generator_from_list(list_instance: list):
        for item in list_instance:
            yield item

    @staticmethod
    def _modify_representation_statements_path():
        return os.path.join(get_program_root_path(),
                            "in_memory_representation",
                            "actions",
                            "modify_representation")

    def _get_modify_representation_statements(self):
        statements_code_root_path = self._modify_representation_statements_path()
        statements_paths = list(glob.glob(statements_code_root_path + "\\**\\*.py", recursive=True))

        for path in statements_paths:
            # Load file as module
            # Necessary to access the content
            spec = importlib.util.spec_from_file_location(path, path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            # Check if the file has register method
            if "register" in dir(module):
                # Get method
                register_method = getattr(module, "register")

                # Apply registration to this visitor
                register_method(self)

    def register_modify_representation_statement(self, modify_representation_function):

        if modify_representation_function.__name__ in self._modify_representation_functions:
            new_func_name = modify_representation_function.__name__
            new_file_name = os.path.basename(inspect.getfile(modify_representation_function))

            existing_func = self._modify_representation_functions[new_func_name]
            existing_func_file_name = os.path.basename(inspect.getfile(existing_func))
            ProgramReporter.show_warning_message(
                message="Conflict detected during registering functions for representation modifying, "
                        "registration failed. \n" +
                        "Function " + new_func_name + " which is stored in file " + new_file_name +
                        " has same the name as already registered function in file " + existing_func_file_name + ".\n" +
                        "This is not allowed, function names must be unique, please change the name one of them. "
            )
            return

        function_args_info = inspect.getfullargspec(modify_representation_function)

        if "ast" not in function_args_info.annotations or \
                "mem_rep" not in function_args_info.annotations:

            new_func_name = modify_representation_function.__name__

            ProgramReporter.show_warning_message(
                message="During registration of function for representation modifying was found that\n"
                        "the function " + new_func_name + " has incorrect (inconsistent with the rest of program)\n"
                        "function arguments. This leads to unsuccessfull registration of this function.\n"
                        "The function needs to have arguments \"ast\" and \"mem_rep\".\n"
                        "Please change function declaration to " + new_func_name + "(ast, mem_rep)\n"
                        "or more specifically " + new_func_name + "(ast: Expression, mem_rep: Database)\n"
                        "where:\n"
                        "\t\"ast\" stands for abstract syntax tree of statement\n"
                        "\t\"mem_rep\" stands for reference to the in memory database representation"
            )
            return

        self._modify_representation_functions[modify_representation_function.__name__] = modify_representation_function

    def _make_serialization(self):
        # Provide serialization memory representation and store to serialization path
        if self.args_data.serialization_path is not None:
            self.mem_rep.serialize_and_save(
                serialization_path=self.args_data.serialization_path
            )
        aa = pickle.dumps(self.mem_rep)
        bb = pickle.loads(aa)
