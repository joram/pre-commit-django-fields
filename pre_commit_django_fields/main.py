import argparse
import json
import os
from typing import List

from django import setup
from django.apps import apps

setup()

CONFIG_FILENAME = ".pre-commit-config-django-fields.json"
DEFAULT_CONFIG = {
    "fields": [
        {
            "name": "id",
            "required_classes": ["UUIDField"]
        },
    ],
    "ignore_models": [],
}


_config = None
def config():
    global _config
    if _config is not None:
        return _config

    if os.path.exists(CONFIG_FILENAME):
        with open(CONFIG_FILENAME) as f:
            _config = json.load(f)
    else:
        _config = DEFAULT_CONFIG
    return _config


def required_field_classes():
    file_config = config()
    dict_config = {}
    for c in file_config["fields"]:
        dict_config[c["name"]] = c["required_classes"]
    return dict_config


def get_django_models():
    for app_name in apps.all_models.keys():
        app = apps.get_app_config(app_name)
        if "site-packages" in app.path:
            continue
        for model_class in app.get_models():
            yield model_class


def erronious_fields():
    model_classes = get_django_models()
    for model_class in model_classes:
        model_name = model_class.__name__
        if model_name in config()["ignore_models"]:
            continue

        for field in model_class._meta.fields:
            field_class_name = field.__class__.__name__
            field_name = field.name
            required_classes = required_field_classes().get(field_name)
            if required_classes is None:
                continue

            if field_class_name not in required_classes:
                yield model_class, field_class_name, required_classes


def main():
    found_erronious_fields = False
    for model_class, field_class_name, required_classes in erronious_fields():
        print(f"ERROR: id for {model_class} is {field_class_name}. Must be one of {required_classes}")
        found_erronious_fields = True

    if found_erronious_fields:
        exit(1)
