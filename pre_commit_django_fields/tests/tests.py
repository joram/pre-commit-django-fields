import dataclasses
import json

import pytest

from pre_commit_django_fields.utils.find_fields import find_fields
from pre_commit_django_fields.utils.find_errors import find_errors
from pre_commit_django_fields.data_classes import Field, FieldConfiguration, Configuration, MissingField


@pytest.mark.parametrize("filename, golden_file", [
    ("example_models_1.py", "example_models_1.golden.json"),
    ("example_models_2.py", "example_models_2.golden.json"),
    ("example_models_3.py", "example_models_3.golden.json"),
    ("example_models_4.py", "example_models_4.golden.json"),
])
def test_find_fields(filename: str, golden_file: str):
    fields = find_fields([filename])
    fields = [dataclasses.asdict(field) for field in fields]
    with open(f"{golden_file}", "r") as f:
        golden_fields = json.load(f)
    assert fields == golden_fields

    print(fields)


def test_find_errors__wrong_field__returns_MissingField_error():
    config = Configuration(
        fields=[
            FieldConfiguration(
                name="id",
                required_classes=["UUIDField"],
            ),
        ],
        ignore_models=["User"],
    )

    errors = find_errors(["example_models_4.py"], config)

    assert errors == [MissingField(
        name='id',
        class_name='ExampleModel',
        filename='example_models_4.py',
        lineno=0),
    ]
    assert errors[0].message == "example_models_4.py:0: ExampleModel.id is not explicitly defined"


def test_find_errors__wrong_field__returns_Field_error():
    config = Configuration(
        fields=[
            FieldConfiguration(
                name="id",
                required_classes=["UUIDField"],
            ),
        ],
        ignore_models=["User"],
    )

    errors = find_errors(["example_models_5.py"], config)

    assert errors == [Field(
        name='id',
        field_type='TextField',
        class_name='ExampleModel',
        filename='example_models_5.py',
        expected_field_classes=['UUIDField'],
        lineno=5),
    ]
    assert errors[0].message == "example_models_5.py:5: ExampleModel.id is a TextField. Should be one of ['UUIDField']"

