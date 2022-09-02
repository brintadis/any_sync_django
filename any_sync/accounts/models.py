from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    yandex_token = models.CharField(
        max_length=500,
        null=True,
    )

    def __str__(self) -> str:
        return self.username
