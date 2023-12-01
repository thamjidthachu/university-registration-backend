from django.db import models
from registration.models.user_model import User


class Service(models.Model):
    SERVICE_NAME = (
        ("EQU", "Equation"),
    )
    name = models.CharField(max_length=6, choices=SERVICE_NAME, unique=True)
    active = models.BooleanField(default=False)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    action_date = models.DateTimeField()

    def __str__(self):
        return dict(self.SERVICE_NAME)[self.name]
