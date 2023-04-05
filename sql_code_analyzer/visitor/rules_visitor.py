import enum
import importlib.util
import ntpath
from queue import LifoQueue

from sql_code_analyzer.checker.rules.base import BaseRule
from sql_code_analyzer.output.enums import MessageType, ExitWith
from sql_code_analyzer.output.reporter.base import ProgramReporter, RuleReport
from sql_code_analyzer.visitor.visitor import Visitor


class RuleType(enum.Enum):
    Visit = "_visit"
    Leave = "_leave"


class RulesVisitor(Visitor):

    def __init__(self, rules_args_data, expect_set):
        self.expect_set = expect_set
        self._restrict_rules = {}
        self.rules_args_data = rules_args_data
        self.node = None
        self.node_to_lint = None
        self._rules = []
        self._persistent_rules = []
        self.visit_leave_queue = LifoQueue()
        self.get_rules()
        self._reports = []


    @staticmethod
    def _get_node_type(node):
        return node.__class__.__name__[:-1].lower()

    def traversing_ast_done(self):
        # pop all and call visit_leave
        # If node is None, then already
        # iterated through all nodes,
        # so we just check remaining nodes
        # in queue which are waiting for
        # _leave function call

        while not self.visit_leave_queue.empty():
            self.node_to_lint = self.visit_leave_queue.get()
            self.lint_node(RuleType.Leave)

    def visit(self, node):
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
                # because we are not leaving sub-tree
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
                # nodes in node 2 sub-tree
                # We can use that node 2 and node 4
                # are in same depth,
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
                ProgramReporter.show_error_message("Unexpected error during evaluating rules.", ExitWith.InternalError)

    def lint_node(self, visit_or_leave):
        # Apply rules based on node type
        self.apply_rules(visit_or_leave=visit_or_leave)

    def apply_rules(self, visit_or_leave: RuleType):

        # Get rules that satisfy restrictions or have no restrictions
        rules_result = [obj for obj, restrictions in self._restrict_rules.items()
                        if not restrictions or restrictions.intersection(self.expect_set)]

        # Iterating over rules which comply with restriction
        for rule in rules_result:

            rule_instance = None
            for item in self._persistent_rules:
                if type(item) is rule:
                    rule_instance = item
                    break

            if rule_instance is None:
                rule_instance = rule()

            # Check if the rule class has _visit method for this node
            if hasattr(rule_instance, self._get_node_type(node=self.node_to_lint) + visit_or_leave.value) and \
               callable(getattr(rule_instance, self._get_node_type(node=self.node_to_lint) + visit_or_leave.value)):

                # Get the method
                rule_method = getattr(rule_instance, self._get_node_type(node=self.node_to_lint) + visit_or_leave.value)

                # Call/Apply rule

                self.call_rule(rule_method=rule_method)
                ...

    @staticmethod
    def path_leaf(path):
        head, tail = ntpath.split(path)
        return tail or ntpath.basename(head)

    def get_rules(self):
        # Go through all rule files
        for path in self.rules_args_data.paths:

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

    def register_rule(self, rule):
        # Register rule
        self._rules.append(rule)

        if hasattr(rule, "persistent"):
            if rule.persistent:
                self._persistent_rules.append(rule())

        if hasattr(rule, "restrict"):
            self._restrict_rules[rule] = rule.restrict
        else:
            self._restrict_rules[rule] = {}

        ...

    def call_rule(self, rule_method):
        reports: BaseRule = rule_method(self.node_to_lint)
        self.save_reports(reports=reports)

    def save_reports(self, reports):
        reports = reports.get_reports()
        for report in reports:
            self._reports.append(report)
