from dataclasses import dataclass
from typing import Optional, List


@dataclass
class Field:
    name: str
    field_type: str
    class_name: str
    filename: str
    lineno: int
    expected_field_classes: Optional[List[str]] = None

    @property
    def message(self):
        return f"{self.filename}:{self.lineno}: {self.class_name}.{self.name} is a {self.field_type}. Should be one of {self.expected_field_classes}"


@dataclass
class FieldConfiguration:
    required_classes: List[str]
    parent_classes: Optional[List[str]] = None
    name: str = "id"
    required_explicit_definition: bool = False


@dataclass
class Configuration:
    fields: List[FieldConfiguration]
    ignore_models: List[str]


@dataclass
class MissingField:
    name: str
    class_name: str
    lineno: int
    filename: str

    @property
    def message(self):
        return f"{self.filename}:{self.lineno}: {self.class_name}.{self.name} is not explicitly defined"
