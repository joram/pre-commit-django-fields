from typing import List, Union

from pre_commit_django_fields.data_classes import Configuration, MissingField, Field
from pre_commit_django_fields.utils.find_fields import find_fields


def find_errors(filenames: str, config: Configuration) -> List[Union[MissingField, Field]]:
    errors = []
    fields = find_fields(filenames=filenames)

    # find fields that don't match the configuration
    for field in fields:
        if field.class_name in config.ignore_models:
            continue
        for field_config in config.fields:
            if field.name == field_config.name:
                if field.field_type not in field_config.required_classes:
                    field.expected_field_classes = field_config.required_classes
                    errors.append(field)

    # find fields that are missing
    found_class_names = set()
    for field in fields:
        found_class_names.add((field.class_name, field.filename))
    for class_name, filename in found_class_names:
        if class_name in config.ignore_models:
            continue
        for field_config in config.fields:
            if not field_config.required_explicit_definition:
                continue

            found_field = False
            for field in fields:
                if field.name == field_config.name:
                    found_field = True
                    break

            if not found_field:
                errors.append(MissingField(
                    name=field_config.name,
                    class_name=class_name,
                    lineno=0,
                    filename=filename,
                ))
    return errors
