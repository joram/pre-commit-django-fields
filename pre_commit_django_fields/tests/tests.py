import dataclasses
import json

import pytest

from pre_commit_django_fields.main import find_fields


@pytest.mark.parametrize("filename, golden_file", [
    ("example_models_1.py", "example_models_1.golden.json"),
    ("example_models_2.py", "example_models_2.golden.json"),
    ("example_models_3.py", "example_models_3.golden.json"),
])
def test_all(filename: str, golden_file: str):
    fields = find_fields([filename])
    fields = [dataclasses.asdict(field) for field in fields]
    with open(f"{golden_file}", "r") as f:
        golden_fields = json.load(f)
    assert fields == golden_fields

    print(fields)


