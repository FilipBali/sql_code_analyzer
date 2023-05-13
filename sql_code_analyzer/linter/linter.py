import glob
import importlib.util
import inspect
import os
import pickle
from queue import Queue
from typing import Generator

###############################################
#              SQLGlot IMPORT
###############################################
import sqlglot
from sqlglot import Tokenizer
from sql_code_analyzer.output.reporter.rule_reporter import RuleReporter
from sql_code_analyzer.tools.path import get_program_root_path  
from sqlglot import expressions as exp

###############################################
#          sql_code_analyzer IMPORT
###############################################

from sql_code_analyzer.adapter.adapt_ast import adapt_ast
from sql_code_analyzer.checker.tools.rules_handler import CRules
from sql_code_analyzer.in_memory_representation.struct.database import Database
from sql_code_analyzer.in_memory_representation.tools.ast_manipulation import get_next_node
from sql_code_analyzer.input.args_handler import CArgs
from sql_code_analyzer.output import enums
from sql_code_analyzer.output.terminator.base import Terminator

################################
#           OUTPUT
################################
from sql_code_analyzer.output.reporter.program_reporter import ProgramReporter
from sql_code_analyzer.visitor.rules_visitor import RulesVisitor


class Linter:
    """
    Encapsulates program logic.
    Contains data about:
        Program arguments parsed to a program arguments object.
        Parsed rules data represents location where are expected to find rules, which rules are allowed to use or
        are need to exclude/skipped.
        List of functions which can be used to parse and modify memory representation.
        Reference to tokens of a statement.
        Reference to abstract syntax tree of a statement.
        Reference to memory representation.

    Features:
        Initialise memory database (or memory representation) which is used to simulate database schema objects.
        Create a copy of real database schema if user provides connection credentials.
        Load previous used and serialized memory representation.
        Call SQLGlot library to parse statements to abstract syntax tree
        Provide linting of abstract syntax tree
        Makes a modification of memory representation based on statement
        Serialization and deserialization of memory representation for future use
    """

    def __init__(self):

        # TODO Prepisat v praci: connection_file_option -> connection_file_section

        self._modify_representation_functions = {}
        self._parse_error_occurred = False
        self.rule_reporter = RuleReporter()
        self.statement = None

        self._init_program_argument_class()
        self._init_rules_class()
        self._init_memory_database_representation()
        self._get_modify_representation_statements()
        self._apply_statements_from_database_server()
        self._sql_statements_processing()

        # If serialization path is None
        # Program assume that serialization is not wanted.
        if self.args_data.serialization_file is not None:
            self._make_serialization()

        self._show_reports()

    def _init_program_argument_class(self) -> None:
        """
        Creates an object from CArgs class which encapsulate parsed program arguments data and save it to linter object
        :return: None
        """

        # get data from program input and init class for arguments
        self.args_data = CArgs()

    def _init_rules_class(self) -> None:
        """
        Creates an object from CRules class which encapsulate parsed rule data and save it to linter object
        :return: None
        """

        # init rules class
        self.rules_args_data = CRules(path_to_rules_folder=self.args_data.rules_path,
                                      include_folders=self.args_data.include_folders,
                                      exclude_folders=self.args_data.exclude_folders)

    def _init_memory_database_representation(self) -> None:
        """
        Creates an object from Database class which providing simulation of database representation which is created
        by SQL statements.

        Default database name is called MemoryDB
        Default schema in every database instance is called dbo
        :return:
        """

        if self.args_data.deserialization_file is not None:
            # Provide deserialization memory representation from file and initialise database structure
            path = self.args_data.deserialization_path / self.args_data.deserialization_file

            try:
                with open(path, 'rb') as f:
                    self.mem_rep = pickle.load(f)

            except FileNotFoundError:
                ProgramReporter.show_error_message(
                    message=f"Deserialization failed, file not found!\nPath: {path}"
                )
            except pickle.UnpicklingError:
                ProgramReporter.show_error_message(
                    message=f"Deserialization failed, can not unpickle file!\nPath: {path}"
                )

            except (Exception,):
                ProgramReporter.show_error_message(
                    message=f"Deserialization failed!\nPath: {path}"
                )

        else:
            # initialise in memory representation
            self.mem_rep: Database = Database("MemoryDB").set_default_scheme()

    def _check_if_modifying_statement(self) -> bool:
        """
        Determines whether the command now being processed is suitable for changing the memory representation.
        :return: True/False
        """

        # Before doing that, it must be done a problem with alter statements
        # Because they have inconsistent naming.. key=AlterTable not key=Alter, kind=Table
        if hasattr(self.ast, "key"):
            # if self.ast.key.lower() in ["create_", "alter_", "altertable_", "drop_", "insert_", "update_", "delete_"]:
            # if self.ast.key.lower() in ["create", "alter", "altertable", "drop", "insert", "update", "delete"]:

            modifying_classes = (exp.Create, exp.Drop,
                                 exp.AlterTable, exp.AlterColumn,
                                 exp.Insert, exp.Update, exp.Delete)

            if isinstance(self.ast, modifying_classes):
                return True

        return False

    def _parse_statement(self) -> bool:
        try:
            self.tokens = Tokenizer().tokenize(self.statement)
            self.ast = sqlglot.parse_one(self.statement)
            return True

        except (Exception,) as e:
            ProgramReporter.show_warning_message(
                message="An error occurred during SQL statement processing by the SQLGlot library."
                        f"SQLGlot library report: {e}"
            )

            self._parse_error_occurred = True
            return False

    def _apply_statements_from_database_server(self) -> None:
        """

        :return: None
        """
        # iterate over database SQL statements
        for self.statement in self.args_data.database_statements:

            success = self._parse_statement()

            if not success:
                # Next statement
                ProgramReporter.show_warning_message(
                    message=f"An error occurred while processing an SQL statement from database.\n"
                            "This statement will be skipped.\n"
                            f"Statement: \n{self.statement}"
                )
                continue

            self.ast = adapt_ast(self.ast)

            # provide changes based on SQL statement to memory representation
            if self._check_if_modifying_statement():
                self._modify_representation()

    def _sql_statements_processing(self) -> None:
        """
        Iterates over SQL statements from input
        Process each SQL statements
        Processing have multiple stages:
            1) Parse statements and get tokens and abstract syntax tree
            2) If possible, include to each node in abstract syntax tree the corresponding location from the code
            3) If necessary, reorder the nodes of abstract syntax tree into appropriate order according to real
               database statement execution
            4) Lint statement, apply rules to statement, get linting reports
            5) Determines whether the command now being processed is suitable for changing the memory representation.
            6) If yes, apply memory representation changes if any

        :return: None
        """

        self.rules_visitor: RulesVisitor = RulesVisitor(rules_args_data=self.rules_args_data,
                                                        mem_rep=self.mem_rep)

        self.rules_visitor.lint_event(event_type="start_lint")

        # iterate over SQL statements
        for self.statement, position in self.args_data.statements:

            success = self._parse_statement()

            if not success:
                # Next statement
                lines = self.statement.split("\n")
                result = []
                for line in lines:
                    if "--" in line:
                        text, index = line.split("--")
                        result.append((text, int(index)))

                # TODO if verbose
                # ProgramReporter.show_warning_message(
                #     message=f"An error occurred while processing an SQL statement that starts at line {result[0][1]}.\n"
                #             "This statement will be skipped.\n"
                #             f"Statement: \n{self.statement}"
                # )

                ProgramReporter.show_warning_message(
                    message=f"An error occurred while processing an SQL statement that starts at line {result[0][1]}. \n"
                            "This statement will be skipped.\n"
                )
                continue

            # Library counts the rows from one
            # It is necessary to calculate the rows to match the input file
            # The approach is to find out the position of the start of the statement
            # and add it as a constant to location (line value)
            # Since we are adding the number of rows to the location, so we have to count from zero
            # Therefore we have to subtract the value from which we count
            library_initial_count_number = 1
            self._include_code_locations(position_const=position - library_initial_count_number)

            # TODO DELETE
            ast_ast = self.ast.walk(bfs=False)

            # for nodes in ast_ast:
            #     if nodes is not None:
            #         node = nodes[0]
            #         # if node.code_location is None:
            #         if not hasattr(node, "code_location"):
            #             print(node)
            #         else:
            #             print(str(node) + " " + str(node.code_location))

            self.ast = adapt_ast(self.ast)

            self.rule_reporter.statement = (self.statement, position)

            self._lint_statement()

            # provide changes based on SQL statement to memory representation
            if self._check_if_modifying_statement():
                self._modify_representation()

        self.rules_visitor.lint_event(event_type="end_lint")

    def _include_code_locations(self, position_const: int) -> None:
        """
        Try to include code locations to abstract syntax tree nodes

        There are two possible approaches to how to get this work.
        1) Rewrite some part of SQLGlot library
           This means some incompatibility with source repository of SQLGlot
           It is a reliable solution, but it needs to maintain changes and update process if thera are incoming
           changes from source repository

        2) Try to associate node with token
           Tokens from SQLGlot library already have code location inside
           The problem is that SQLGlot library does not include this information also to abstract syntax tree
           By text or TokenType in token there is a high possibility that find out match with node
           abstract syntax tree, if they are used in node.

        This function combines these two approaches. Some changes have been made to SQLGlot library, this function
        detects if code location is already set.
        During testing, it appears that 2) approach can cover most cases, and the only problem is nodes that are created
        from two or more tokens like CREATE TABLE, NOT NULL, PRIMARY KEY where every word is representing a single
        token.

        This means the program can use a change-free library of SQLGlot, but code location data will be missing
        in nodes where are used more than one token during node creation.

        :return: None
        """

        ast_gen = self.ast.walk(bfs=False)

        # for nodes in ast_gen:
        #     if nodes is not None:
        #         nodes[0].code_location = None

        # Transform to dict structure
        # for nodes in ast_gen:
        #     if nodes is not None:
        #         if nodes[0].code_location is not None:
        #             tlist = []
        #             for token in nodes[0].code_location:
        #                 tlist.append({"line": token.line + position_const,
        #                               "col": token.col,
        #                               "text": token.text})
        #             nodes[0].code_location = tlist

        ast_gen = list(self.ast.walk(bfs=False))

        seen_tokens = []
        for nodes in ast_gen:
            if nodes is not None:
                node = nodes[0]
                node_name = node.name
                node_key = node.key

                to_del = []

                found = False
                for token_idx, token in enumerate(self.tokens):
                    if token.text.lower() == node_name.lower() or \
                            token.text.lower() == node_key.lower():

                        location_text = token.text

                        if hasattr(node, "args") and "kind" in node.args and isinstance(node.args["kind"], str):
                            if len(self.tokens)-1 > token_idx:
                                next_token = self.tokens[token_idx+1]
                                if node.args["kind"].lower() == next_token.text.lower():
                                    location_text = f"{location_text} {next_token.text}"


                        # if node.code_location is None or len(node.code_location) < 2:
                        node.code_location = [{"line": token.line + position_const,
                                              "col": token.col,
                                              "text": location_text}]
                        found = True
                        break
                    elif node_key.lower() == "datatype":

                        try:
                            t = token.token_type.value.upper()
                            ttype = exp.DataType.Type[t]
                            if node.this == ttype:
                                node.code_location = [{"line": token.line + position_const,
                                                      "col": token.col,
                                                      "text": token.text}]

                            found = True
                            break

                        except (Exception,):
                            pass

                    to_del.append(token)

                if found:
                    seen_tokens = to_del + seen_tokens
                    for token_to_del in to_del:
                        self.tokens.remove(token_to_del)

                else:
                    for stoken in seen_tokens:
                        if stoken.text.lower() == node_name.lower() or \
                                stoken.text.lower() == node_key.lower():
                            node.code_location = [{"line": stoken.line + position_const,
                                                  "col": stoken.col,
                                                  "text": stoken.text}]
                            break

                        elif node_key.lower() == "datatype":
                            try:
                                t = stoken.token_type.value.upper()
                                ttype = exp.DataType.Type[t]
                                if node.this == ttype:
                                    node.code_location = [{"line": stoken.line + position_const,
                                                           "col": stoken.col,
                                                           "text": stoken.text}]
                                break

                            except (Exception,):
                                pass

    def _lint_statement(self) -> None:
        """
        Encapsulate logic of linting process
        Creates the generator from abstract syntax tree
        Creates the queue where node is saved if it is belonged to another context part

        :return: None
        """

        ast_generator: Generator = self._get_generator_based_on_statement()
        visited_nodes = Queue()

        self.rules_visitor.expect_set = self._create_restriction_set_from_statement()

        self.rules_visitor.lint_event(event_type="start_command_lint")

        stop_parse = False
        while 1 and stop_parse is not True:

            # get node
            node, nodes, stop_parse = get_next_node(visited_nodes=visited_nodes,
                                                    ast_generator=ast_generator)

            if node is not None:
                node.accept(self.rules_visitor)

        self.rules_visitor.traversing_ast_done()
        self.rules_visitor.lint_event(event_type="end_command_lint")

        self.rule_reporter.add_reports(
            reports=self.rules_visitor.reports
        )

        self.rules_visitor.clear_lint_variables()

    def _create_restriction_set_from_statement(self) -> set:
        """
        Creates restriction set from statement data.
        Restriction set is then used to select only the appropriate rules.

        :return: Restriction set for an actual statement
        """

        expect_set = set()
        if hasattr(self.ast, "key") and \
                "kind" in self.ast.args and \
                self.ast.args["kind"] is not None:

            statement: str = self.ast.key.lower() + "_" + self.ast.args["kind"].lower()
            expect_set.add(statement)
            expect_set.add(self.ast.key.lower())
            expect_set.add(self.ast.args["kind"].lower())

        elif hasattr(self.ast, "key"):
            statement: str = self.ast.key.lower()
            expect_set.add(statement)

        return expect_set

    def _modify_representation(self) -> None:
        """
        Call functions that are responsible for modifying the memory representation.
        The function is determined by the current node.

        :return: None
        """

        if hasattr(self.ast, "key") and "kind" in self.ast.args and self.ast.args["kind"] is not None:

            statement: str = self.ast.key.lower() + "_" + self.ast.args["kind"].lower()

            if statement in self._modify_representation_functions:
                function = self._modify_representation_functions[statement]
                function(ast=self.ast, mem_rep=self.mem_rep)

            else:
                print(self.ast.key.upper() + " " + self.ast.args["kind"].upper() + " is not supported")

        elif hasattr(self.ast, "key") and self.ast.key == "altertable":
            function = self._modify_representation_functions["alter_table"]
            function(self.ast, self.mem_rep)

        else:
            ProgramReporter.show_warning_message(
                message="Unknown command."
            )

    def _get_generator_based_on_statement(self) -> Generator:
        """
        Reorder SELECT's abstract syntax tree to correct (database) order
        :return: Abstract syntax tree generator
        """
        return self.ast.walk(bfs=False)

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
    def _create_generator_from_list(list_instance: list) -> Generator:
        """
        Create generator from list items
        :param list_instance: List of items
        :return: Generator
        """

        for item in list_instance:
            yield item

    @staticmethod
    def _modify_representation_statements_path() -> str:
        """
        Create a path where memory representation change functions are located by default
        :return: Path
        """

        return os.path.join(get_program_root_path(),
                            "in_memory_representation",
                            "actions",
                            "modify_representation")

    def _get_modify_representation_statements(self) -> None:
        """
        Iterate over memory representation change functions and register it to the program.
        :return: None
        """

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

    def register_modify_representation_statement(self, modify_representation_function) -> None:
        """
        Encapsulates the registration of each memory representation change function.
        If successful, then function is registered for future use
        :param modify_representation_function: Memory representation change function
        :return: None
        """

        if modify_representation_function.__name__ in self._modify_representation_functions:
            new_func_name = modify_representation_function.__name__
            new_file_name = os.path.basename(inspect.getfile(modify_representation_function))

            existing_func = self._modify_representation_functions[new_func_name]
            existing_func_file_name = os.path.basename(inspect.getfile(existing_func))
            ProgramReporter.show_warning_message(
                message="Conflict detected during registering functions for representation modifying, "
                        "registration failed. \n" +
                        f"Function {new_func_name} which is stored in file {new_file_name} \n"
                        f" has same the name as already registered function in file {existing_func_file_name} \n" +
                        "This is not allowed, function names must be unique, please change the name one of them. "
            )
            return

        function_args_info = inspect.getfullargspec(modify_representation_function)

        if "ast" not in function_args_info.annotations or \
                "mem_rep" not in function_args_info.annotations:

            new_func_name = modify_representation_function.__name__

            ProgramReporter.show_warning_message(
                message="During registration of function for representation modifying was found that\n"
                        f"the function {new_func_name} has incorrect (inconsistent with the rest of program)\n"
                        "function arguments. This leads to unsuccessfully registration of this function.\n"
                        "The function needs to have arguments \"ast\" and \"mem_rep\".\n"
                        f"Please change function declaration to {new_func_name}(ast, mem_rep)\n"
                        f"or more specifically {new_func_name}(ast: Expression, mem_rep: Database)\n"
                        "where:\n"
                        "\t\"ast\" stands for abstract syntax tree of statement\n"
                        "\t\"mem_rep\" stands for reference to the in memory database representation"
            )
            return

        self._modify_representation_functions[modify_representation_function.__name__] = modify_representation_function

    def _make_serialization(self) -> None:
        """
        Makes serialization of state of memory representation and create persistent save to the disk
        :return: None
        """

        if self._parse_error_occurred:

            err_user_answer = False
            while 1:

                if err_user_answer:
                    user_answer = input("\nPlease answer only [yes/no] or in short way [y/n]\n")
                else:
                    ProgramReporter.show_warning_message(
                        message="An error occurred while parsing SQL statements.\n"
                                "One or more statements failed to parse. \n"
                                "Thus, these statements were not part of the linting \n"
                                "or memory representation changes, and the resulting \n"
                                "memory representation may be in an unexpected state. \n"
                                "Do you still want to continue saving the memory representation?"
                    )
                    user_answer = input()

                if user_answer.lower() == "n" or user_answer.lower() == "no":
                    Terminator.exit(enums.ExitWith.Success)

                elif user_answer.lower() == "y" or user_answer.lower() == "yes":
                    break

                else:
                    err_user_answer = True

        # Provide serialization memory representation and store to a serialization path
        path = self.args_data.serialization_path / self.args_data.serialization_file

        try:
            with open(path, 'wb') as f:
                pickle.dump(self.mem_rep, f)

        except FileNotFoundError:
            ProgramReporter.show_warning_message(
                message=f"Serialization failed, file not found!\nPath: {path}"
            )
        except pickle.PicklingError:
            ProgramReporter.show_warning_message(
                message=f"Serialization failed, can not unpickle file!\nPath: {path}"
            )

        except (Exception,):
            ProgramReporter.show_warning_message(
                message=f"Serialization failed!\nPath: {path}"
            )

    def _show_reports(self):
        self.rule_reporter.print_reports()
