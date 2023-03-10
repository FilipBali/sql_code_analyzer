import glob
import os
import re


class CRules:

    path_to_rules_folder: str = ""

    # if both empty, take all rules
    include_folders: [str] = []
    exclude_folders: [str] = []

    def __init__(self,
                 path_to_rules_folder: str = None):

        if path_to_rules_folder is not None:
            self.path_to_rules_folder = path_to_rules_folder

        else:
            checker_root = os.path.dirname(os.path.dirname(__file__))
            self.path_to_rules_folder = os.path.join(checker_root, "rules")


        include = set(glob.glob(self.path_to_rules_folder + "\\**\\*.py", recursive=True))
        # exclude_folder = set(glob.glob(self.path_to_rules_folder + "\\**\\drop*", recursive=True))

        self.exclude_folders.append("drop")
        self.exclude_folders.append("create")
        for exclude_folder in self.exclude_folders:
            regex = re.compile(r".*/\\"+exclude_folder+"/\\.*")
            include = [i for i in include if not regex.match(i)]

        ...


