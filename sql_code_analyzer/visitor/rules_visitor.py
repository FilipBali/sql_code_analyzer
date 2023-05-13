from __future__ import annotations

import enum
import importlib.util
from queue import LifoQueue


from sql_code_analyzer.checker.rules.base import BaseRule
from sql_code_analyzer.in_memory_representation.struct.database import Database
from sql_code_analyzer.output.enums import ExitWith
from sql_code_analyzer.output.reporter.program_reporter import ProgramReporter
from sql_code_analyzer.tools.path import get_path_object
from sql_code_analyzer.visitor.visitor import Visitor

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from typing import List, Set, Dict


class RuleType(enum.Enum):
    """
    Enumerator of rule types.
    Provides an option to call rules when a node is entered or leaved.
    The rule is mostly the root node of some subtree of abstract syntax tree.
    So this provides also provides functionality to call rules when
    subtree is visited or leaved.

    The enumerator value is always combined by node class name.
    By this design, it is possible to call only rules that are
    expecting this kind of node

    _visit rule is called when the node entered/visited.
    _leave rule called when the node leaved.

    Examples of using:
    The node is called: ColumnDef
    ColumnDef provides subtree to definition of column.
    To call rule when ColumnDef is visited, it is necessary to
    create a method called columndef_visit.

    For rule leaving ColumDef-tree the method is columndef_leave.
    """

    Visit = "_visit"
    Leave = "_leave"


class RulesVisitor(Visitor):
    """
    Provides functionality/logic of RulesVisitor visitor.
    It is specialized to call the rules for visited node.
    It is supporting restrict and permanent features.

    Restrict feature can be used when we want to restrict
    the rule to only some nodes. Restriction is defined by
    appointing the node names.

    Permanent feature is providing an option to have an
    indestructible rule object. When the rule is called
    between nodes, the rule object is always a new instance.
    If a permanent feature is set to true, the object is
    saved and called also with another node. This can
    be useful if we want to transfer data about linting
    from one node to another one.

    """
    # def __init__(self, rules_args_data, expect_set):
    def __init__(self, rules_args_data, mem_rep):
        """
        Initial method for RulesVisitor instance

        :param rules_args_data: Provides data about available rules and additional data about them.

        :param expect_set: The set of expecting rules. The restrict feature. The expect_set comes from
        a statement that will be visited.
        """

        # Parameters
        self.rules_args_data = rules_args_data

        # Memory representation
        self.mem_rep = mem_rep

        # Lint variables
        self._expect_set = set()
        self.node = None
        self.node_to_lint = None
        self.visit_leave_queue = LifoQueue()
        self.reports = []

        # Rules
        self.rules = []
        self.persistent_rules = []
        self.normal_rules = []
        self.temporary_rules = []
        self.restrict_rules = {}
        self.get_rules()

    def clear_lint_variables(self):
        self._expect_set = set()
        self.node = None
        self.node_to_lint = None
        self.visit_leave_queue = LifoQueue()
        self.reports = []
        self._reset_normal_rules()

    def _reset_normal_rules(self):
        for i, rule_object in enumerate(self.normal_rules):
            self.normal_rules[i] = rule_object.__class__()


    @property
    def expect_set(self) -> Set:
        """
        The set of expecting rules.
        This is part of the rule restriction feature.
        The expect_set comes from a statement that will be visited.
        :return: The set of expecting rules.
        """
        return self._expect_set

    @expect_set.setter
    def expect_set(self, value):
        self._expect_set = value

    @property
    def restrict_rules(self) -> Dict:
        return self._restrict_rules

    @restrict_rules.setter
    def restrict_rules(self, value):
        self._restrict_rules = value

    @property
    def rules_args_data(self):
        return self._rules_args_data

    @rules_args_data.setter
    def rules_args_data(self, value):
        self._rules_args_data = value

    @property
    def node(self):
        return self._node

    @node.setter
    def node(self, value):
        self._node = value

    @property
    def node_to_lint(self):
        return self._node_to_lint

    @node_to_lint.setter
    def node_to_lint(self, value):
        self._node_to_lint = value

    @property
    def rules(self) -> List:
        return self._rules

    @rules.setter
    def rules(self, value):
        self._rules = value

    @property
    def persistent_rules(self) -> List:
        return self._persistent_rules

    @persistent_rules.setter
    def persistent_rules(self, value):
        self._persistent_rules = value

    @property
    def normal_rules(self) -> List:
        return self._normal_rules

    @normal_rules.setter
    def normal_rules(self, value):
        self._normal_rules = value

    @property
    def temporary_rules(self) -> List:
        return self._temporary_rules

    @temporary_rules.setter
    def temporary_rules(self, value):
        self._temporary_rules = value

    @property
    def visit_leave_queue(self) -> LifoQueue:
        return self._visit_leave_queue

    @visit_leave_queue.setter
    def visit_leave_queue(self, value):
        self._visit_leave_queue = value

    @property
    def reports(self) -> List:
        return self._reports

    @reports.setter
    def reports(self, value):
        self._reports = value

    @staticmethod
    def _get_node_type(node) -> str:
        """
        Getting the node type as lowered class name.
        Class name is also the node name.

        :param node: The node of abstract syntax tree.
        :return: The name of node type.
        """

        return node.__class__.__name__.lower()

    def traversing_ast_done(self) -> None:
        """
        It is used when traversing of abstract syntax tree is done.
        Over time as the RuleVisitor visits nodes, there are saved
        _leave functions of these nodes.
        When traversing of the abstract syntax tree is done, there
        are always some _leave functions that need to be called.
        This function does this work.

        :return: None
        """

        """
        Pop all and call visit_leave
        If node is None, then already
        iterated through all nodes,
        so we just check remaining nodes
        in queue which are waiting for
        _leave function call
        """
        while not self.visit_leave_queue.empty():
            self.node_to_lint = self.visit_leave_queue.get()
            self.lint_node(RuleType.Leave)

    def lint_event(self, event_type: str) -> None:

        if event_type == "start_lint" or event_type == "end_lint":
            method_name = event_type

            for rule in self.persistent_rules:
                if hasattr(rule, method_name) and \
                        callable(getattr(rule, method_name)):
                    # Get the method
                    rule_method = getattr(rule, method_name)

                    # Call/Apply rule
                    self.call_rule(rule_method=rule_method)

        elif event_type == "start_command_lint" or event_type == "end_command_lint":

            method_name = event_type

            rules_result = [obj for obj, restrictions in self.restrict_rules.items()
                            if not restrictions or restrictions.intersection(self.expect_set)]

            for rule in rules_result:
                # Search for persistent rule if persistent

                rule_instance = None
                if hasattr(rule, "persistent") and rule.persistent is True:
                    for item in self.persistent_rules:
                        if type(item) is rule:
                            rule_instance = item
                            break

                else:
                    for item in self.normal_rules:
                        if type(item) is rule:
                            rule_instance = item
                            break

                if rule_instance is None:
                    continue

                if hasattr(rule_instance, method_name) and \
                   callable(getattr(rule_instance, method_name)):
                    # Get the method
                    rule_method = getattr(rule_instance, method_name)

                    # Call/Apply rule
                    self.call_rule(rule_method=rule_method)

    def visit(self, node) -> None:
        """
        Provides the main logic of RuleVisitor.
        As the abstract syntax tree is traversed,
        the visit function calls the rules over
        particular nodes and provides node linting.

        :param node: Node which will be visited
        :return: None
        """

        # Save node
        self.node = node

        if self.visit_leave_queue.empty():
            self.visit_leave_queue.put(node)

            self.node_to_lint = self.node
            self.lint_node(visit_or_leave=RuleType.Visit)

        else:
            prev_node = self.visit_leave_queue.get()
            if node.depth > prev_node.depth:

                # prev_node == 2
                #      node == 3
                #
                # Going from node 2 to node 3
                # As we are going to more depth
                # there is no need to call _leave function
                # because we are not leaving subtree
                # bud instead entering new one
                #             ---
                #            | 1 |
                #             ---
                #            /   \
                #          ---    ---
                #         | 2 |  | 4 |
                #          ---    ---
                #         /
                #       ---
                #      | 3 |
                #       ---

                self.visit_leave_queue.put(prev_node)

                self.visit_leave_queue.put(node)
                self.node_to_lint = self.node
                self.lint_node(visit_or_leave=RuleType.Visit)

            elif node.depth == prev_node.depth:
                # call visit_leave on prev_node

                # prev_node == 2
                #      node == 4
                #
                # Going from node 2 to node 4
                # As we are going to visit sibling node
                # we must call _leave function to all
                # nodes in node 2 sub-tree
                #             ---
                #            | 1 |
                #             ---
                #            /   \
                #          ---    ---
                #         | 2 |  | 4 |
                #          ---    ---

                self.node_to_lint = prev_node
                self.lint_node(visit_or_leave=RuleType.Leave)

                self.visit_leave_queue.put(node)
                self.node_to_lint = node
                self.lint_node(visit_or_leave=RuleType.Visit)

            elif node.depth < prev_node.depth:
                # pop queue and call visit_leave until prev_node.depth is not equal

                # prev_node == 3
                #      node == 4
                # Going from node 3 to node 4
                # As we are going to visit upper node
                # we must call _leave function to all
                # nodes in node 2 subtree
                # We can use that node 2 and node 4
                # are in the same depth,
                # so we call _leave function for all
                # nodes which have depth <= node 4
                #
                #             ---
                #            | 1 |
                #             ---
                #            /   \
                #          ---    ---
                #         | 2 |  | 4 |
                #          ---    ---
                #         /
                #       ---
                #      | 3 |
                #       ---

                self.visit_leave_queue.put(prev_node)
                while not self.visit_leave_queue.empty():
                    self.node_to_lint = self.visit_leave_queue.get()
                    self.lint_node(RuleType.Leave)

                    if self.node_to_lint.depth == node.depth:
                        break

                self.visit_leave_queue.put(node)
                self.node_to_lint = node
                self.lint_node(RuleType.Visit)

            else:
                ProgramReporter.show_error_message(
                    message="Unexpected error during evaluating rules.",
                    exit_code=ExitWith.InternalError
                )

    def lint_node(self, visit_or_leave) -> None:
        """
        This function encapsulates the application of rules
        to a node.

        :param visit_or_leave: Specify a rule type.
        :return: None
        """

        # Apply rules based on a node type
        self.apply_rules(visit_or_leave=visit_or_leave)

    def apply_rules(self, visit_or_leave: RuleType) -> None:
        """
        Provides logic of application of particular
        rules to node.

        :param visit_or_leave: Specify a rule type.
        :return: None
        """

        # Get rules that satisfy restrictions or have no restrictions
        rules_result = [obj for obj, restrictions in self.restrict_rules.items()
                        if not restrictions or restrictions.intersection(self.expect_set)]

        # Iterating over rules which comply with restriction
        for rule in rules_result:

            rule_instance = None

            # Search for persistent rule if persistent
            if hasattr(rule, "persistent") and rule.persistent is True:
                for item in self.persistent_rules:
                    if type(item) is rule:
                        rule_instance = item
                        break

            # Create temporary rule if temporary
            elif hasattr(rule, "temporary") and rule.temporary is True:
                rule_instance = rule()

            # Search for normal rule if temporary
            else:
                for item in self.normal_rules:
                    if type(item) is rule:
                        rule_instance = item
                        break

            # If instance of rule is still None(instance not found), then error, program integrity violated
            if rule_instance is None:
                ProgramReporter.show_warning_message(
                    message=f"The program could not find the rule object of class {rule.__name__},\n"
                            "this can occur when program integrity is violated."
                )
                continue

            # Check if the rule class has _visit or _leave method for this node
            if hasattr(rule_instance, self._get_node_type(node=self.node_to_lint) + visit_or_leave.value) and \
               callable(getattr(rule_instance, self._get_node_type(node=self.node_to_lint) + visit_or_leave.value)):

                rule_instance.node = self.node_to_lint
                rule_instance.mem_rep = self.mem_rep

                # Get the method
                rule_method = getattr(rule_instance, self._get_node_type(node=self.node_to_lint) + visit_or_leave.value)

                # Call/Apply rule
                self.call_rule(rule_method=rule_method)

    def get_rules(self) -> None:
        """
        Extracts a list of rule files from the data obtained by processing program arguments.

        :return: None
        """

        # Go through all rule files
        for path in self.rules_args_data.paths:
            path_object = get_path_object(path)

            try:

                # Load file as module
                # Necessary to access the content
                spec = importlib.util.spec_from_file_location(path, path)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)

                # Check if the file has register method
                if "register" in dir(module):

                    try:
                        # Get method
                        register_method = getattr(module, "register")

                        # Apply registration to this visitor
                        register_method(self)

                    except TypeError as e:
                        ProgramReporter.show_warning_message(
                            message=f"Unable to register rule in {path_object.name},"
                                    "probably missing parameter for checker.\n"
                                    f"Python interpreter report: {e}"
                        )

                    except Exception as e:
                        ProgramReporter.show_warning_message(
                            message=f"Unable to register rule in {path_object.name}.\n"
                                    f"Python interpreter report: {e}"
                        )

            except (Exception, ) as e:
                ProgramReporter.show_warning_message(
                    message=f"Unable to load a module with rule in {path_object.name}.\n"
                            f"Python interpreter report: {e}"
                )

    def register_rule(self, rule) -> None:
        """
        Registers particular rules for their further use for node checking.

        :param rule: The rule class
        :return: Nome
        """

        if hasattr(rule, "persistent") and rule.persistent is True and \
                hasattr(rule, "temporary") and rule.temporary is True:
            ProgramReporter.show_warning_message(
                message="Bad configuration rule, functions persistent and temporary are mutually exclusive.\n"
                        f"Rule {rule.__name__} will not be accepted for checking."
            )
            return

        # Register rule
        self.rules.append(rule)

        if hasattr(rule, "persistent") and rule.persistent is True:
            self.persistent_rules.append(rule())

        elif hasattr(rule, "temporary") and rule.temporary is True:
            self.temporary_rules.append(rule())

        else:
            self.normal_rules.append(rule())

        if hasattr(rule, "restrict"):
            self.restrict_rules[rule] = rule.restrict

        else:
            self.restrict_rules[rule] = {}

    def call_rule(self, rule_method) -> None:
        """
        Call the rule on the node and save the reports.

        :param rule_method: Particular rule method
        :return: None
        """

        reports: BaseRule = rule_method()
        self.save_reports(reports=reports)

    def save_reports(self, reports) -> None:
        """
        The logic of storing reports from the rule.

        :param reports: BaseRule object
        :return: None
        """

        if reports is None:
            return

        reports = reports.get_reports()
        for report in reports:
            self.reports.append(report)
