#!/usr/bin/env python3
import argparse
import ast
import json
import os
from dataclasses import dataclass
from typing import List, Optional, Sequence


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
    verify_model_inherits_from_django_model: bool = True


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
            _config = Configuration(**json.load(f))
    else:
        _config = DEFAULT_CONFIG
    return _config


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
            class_name = n.value.func.attr if hasattr(n.value.func, "attr") else n.value.func.id
            line_number = n.lineno
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

        self.generic_visit(node)

    def set_filename(self, filename):
        self.current_filename = filename


def find_fields(filenames: str, verify_model_inherits_from_django_model:bool=True) -> List[Field]:
    analyzer = Analyzer()
    analyzer.verify_model_inherits_from_django_model = verify_model_inherits_from_django_model
    fields = []
    for filename in filenames:
        if not filename.endswith(".py"):
            continue
        with open(filename, "r") as f:
            ast_tree = ast.parse(f.read(), filename)
            analyzer.set_filename(filename)
            analyzer.visit(ast_tree)
            fields += analyzer.fields
    return fields


def find_errors(filenames: str, config: Configuration) -> List[Field]:
    fields = find_fields(
        filenames=filenames,
        verify_model_inherits_from_django_model=config.verify_model_inherits_from_django_model,
    )
    errors = []
    for field in fields:
        if field.class_name in config.ignore_models:
            continue
        for field_config in config.fields:
            if field.name == field_config["name"]:
                if field.field_type not in field_config["required_classes"]:
                    errors.append(field)
    return errors


def main(argv: Optional[Sequence[str]] = None):
    parser = argparse.ArgumentParser()
    parser.add_argument("filenames", nargs="*", help="Filenames to process")
    args = parser.parse_args(argv)
    config = get_configuration()

    errors = find_errors(args.filenames, config)

    for error in errors:
        print(f"ERROR: {error.filename}:{error.lineno} - {error.class_name}.{error.name} is not a {error.field_type}")

    if len(errors) > 0:
        exit(1)

