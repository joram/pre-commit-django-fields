from django.db import models


class ExampleModel(models.Model):
    id = models.UUIDField(primary_key=True)
    name = models.CharField(max_length=255)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def hello(self):
        match "var":
            case "var":
                print("Hello World!")
