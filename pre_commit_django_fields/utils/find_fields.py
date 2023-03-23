import ast
from typing import List

from pre_commit_django_fields.analyzer import Analyzer
from pre_commit_django_fields.data_classes import Field


def find_fields(filenames: str) -> List[Field]:
    analyzer = Analyzer()
    fields = []
    for filename in filenames:
        analyzer.import_django_model_base_class = False
        if not filename.endswith(".py"):
            continue
        with open(filename, "r") as f:
            ast_tree = ast.parse(f.read(), filename)
            analyzer.set_filename(filename)
            analyzer.visit(ast_tree)
            fields += analyzer.fields
    return fields
