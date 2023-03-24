from django.db.models import Model, CharField, TextField, DateTimeField


class ExampleModel(Model):
    name = CharField(max_length=255)
    description = TextField()
    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)
