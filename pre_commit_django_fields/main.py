#!/usr/bin/env python3
import argparse
import json
import os
from typing import Optional, Sequence

import colorama
from colorama import Fore, Style

from pre_commit_django_fields.data_classes import FieldConfiguration, Configuration
from pre_commit_django_fields.utils.find_errors import find_errors

CONFIG_FILENAME = ".pre-commit-config-django-fields.json"
DEFAULT_CONFIG = Configuration(
    fields=[FieldConfiguration(
        name="id",
        required_classes=["UUIDField"],
        parent_classes=[
            "django.db.models.Model",
            "core.utils.abstract_models.base_abstract_models.BaseModel",
        ],
    )],
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
            _config.fields = [FieldConfiguration(**field) for field in _config.fields]
    else:
        _config = DEFAULT_CONFIG
    return _config


def main(argv: Optional[Sequence[str]] = None):
    parser = argparse.ArgumentParser()
    parser.add_argument("filenames", nargs="*", help="Filenames to process")
    args = parser.parse_args(argv)
    config = get_configuration()

    errors = find_errors(
        filenames=args.filenames,
        config=config,
    )

    colorama.init(autoreset=True)
    for error in errors:
        print(Style.BRIGHT + Fore.RED + "ERROR: " + Fore.RESET + Style.RESET_ALL + error.message)

    if len(errors) > 0:
        exit(1)

