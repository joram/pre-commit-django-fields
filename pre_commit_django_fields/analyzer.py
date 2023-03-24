import ast
from typing import List

from pre_commit_django_fields.data_classes import Field


class Analyzer(ast.NodeVisitor):
    def __init__(self):
        self.current_filename = None
        self.import_django_model_base_class = False
        self.verify_model_inherits_from_django_model = True
        self.fields: List[Field] = []

    def visit_ImportFrom(self, node: ast.ImportFrom):

        if node.module == "django.db.models":
            for name in node.names:
                if name.name == "Model" and name.asname is None:
                    self.import_django_model_base_class = True

        if node.module == "django.db":
            for name in node.names:
                if name.name == "models" and name.asname is None:
                    self.import_django_model_base_class = True

        self.generic_visit(node)

    def visit_ClassDef(self, node: ast.ClassDef):
        for n in node.body:
            if self.verify_model_inherits_from_django_model and not self.import_django_model_base_class:
                continue
            if not isinstance(n, ast.AnnAssign) and not isinstance(n, ast.Assign):
                continue

            skip = False
            for ignorable_type in [ast.List, ast.Tuple, ast.Dict, ast.Constant, ast.Name, ast.Attribute, ast.BinOp]:
                if isinstance(n.value, ignorable_type):
                    skip = True
                    break
            if skip or n.value is None:
                continue

            class_name = n.value.func.attr if hasattr(n.value.func, "attr") else n.value.func.id
            line_number = n.lineno
            try:
                if isinstance(n, ast.AnnAssign):
                    self.fields.append(Field(
                        name=n.target.id,
                        field_type=class_name,
                        class_name=node.name,
                        lineno=line_number,
                        filename=self.current_filename,
                    ))
                else:
                    for target in n.targets:
                        self.fields.append(Field(
                            name=target.id,
                            field_type=class_name,
                            class_name=node.name,
                            lineno=line_number,
                            filename=self.current_filename,
                        ))
            except AttributeError:
                pass

        self.generic_visit(node)

    def set_filename(self, filename):
        self.current_filename = filename
