import glob
import os
import re

from sql_code_analyzer.output.reporter.program_reporter import ProgramReporter


class CRules:

    path_to_rules_folder: str = ""

    # paths with rules
    paths: list = []

    # if both empty, take all rules
    include_folders: [str] = []
    exclude_folders: [str] = []

    def __init__(self,
                 include_folders: list,
                 exclude_folders: list,
                 path_to_rules_folder: str = None):

        self.include_folders = include_folders
        self.exclude_folders = exclude_folders
        self.path_to_rules_folder = path_to_rules_folder

        if len(self.include_folders) > 0 and len(self.exclude_folders) > 0:
            ProgramReporter.show_error_message(
                message="Forbidden parameter combination. Both include and exclude folders are set."
            )

        if self.path_to_rules_folder is None:
            ProgramReporter.show_error_message(
                message="Internal problem. Path targeting to rules is empty."
            )

        # get all paths
        t_paths = list(glob.glob(self.path_to_rules_folder + "\\**\\*.py", recursive=True))

        # TODO \\ for Windows-based system, todo for Linux-based systems
        if len(self.exclude_folders) > 0:
            self.paths = t_paths
            for exclude_folder in self.exclude_folders:
                regex = re.compile(r".*\\"+exclude_folder+r"\\.*")
                self.paths = [i for i in self.paths if not regex.match(i)]

        elif len(self.include_folders) > 0:
            for include_folder in self.include_folders:
                regex = re.compile(r".*\\"+include_folder+r"\\.*")
                self.paths += [i for i in t_paths if regex.match(i)]

