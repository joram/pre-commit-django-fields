from django.db.models import UUIDField, CharField, TextField, DateTimeField


class Model:
    pass


class ExampleModel(Model):
    id = UUIDField(primary_key=True)
    name = CharField(max_length=255)
    description = TextField()
    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)
