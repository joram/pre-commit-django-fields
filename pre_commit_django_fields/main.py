#!/usr/bin/env python3
import ast
import json
import os
from dataclasses import dataclass
from pprint import pprint
from typing import List

@dataclass
class Field:
    name: str
    field_type: str
    class_name: str
    filename: str
    lineno: int


@dataclass
class Configuration:
    fields: List[dict]
    ignore_models: List[str]


CONFIG_FILENAME = ".pre-commit-config-django-fields.json"
DEFAULT_CONFIG = Configuration(
    fields=[{
        "name": "id",
        "required_classes": ["UUIDField1"]
    }],
    ignore_models=[],
)
_config = None


def get_configuration():
    global _config
    if _config is not None:
        return _config

    if os.path.exists(CONFIG_FILENAME):
        with open(CONFIG_FILENAME) as f:
            _config = json.load(f)
    else:
        _config = DEFAULT_CONFIG
    return _config


class Analyzer(ast.NodeVisitor):
    def __init__(self):
        self.current_filename = None
        self.import_django_model_base_class = False
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
        if self.import_django_model_base_class:
            for n in node.body:
                class_name = n.value.func.attr if hasattr(n.value.func, "attr") else n.value.func.id
                line_number = n.lineno
                for target in n.targets:
                    self.fields.append(Field(
                        name=target.id,
                        field_type=class_name,
                        class_name=node.name,
                        lineno=line_number,
                        filename=self.current_filename,
                    ))

        self.generic_visit(node)

    def set_filename(self, filename):
        self.current_filename = filename


def find_fields(filenames: str) -> List[Field]:
    analyzer = Analyzer()
    for filename in filenames:
        with open(filename, "r") as f:
            ast_tree = ast.parse(f.read(), filename)
            analyzer.set_filename(filename)
            analyzer.visit(ast_tree)
            return analyzer.fields


def find_errors(filenames: str, config: Configuration) -> List[Field]:
    fields = find_fields(filenames)
    errors = []
    for field in fields:
        if field.class_name in config.ignore_models:
            continue
        for field_config in config.fields:
            if field.name == field_config["name"]:
                if field.field_type not in field_config["required_classes"]:
                    errors.append(field)
    return errors


if __name__ == "__main__":
    config = get_configuration()
    errors = find_errors(["tests/example_models_1.py"], config)

    for error in errors:
        print(f"ERROR: {error.filename}:{error.lineno} - {error.class_name}.{error.name} is not a {error.field_type}")
    if len(errors) > 0:
        exit(1)

