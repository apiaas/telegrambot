from django.db import models


class Config(models.Model):
    default = models.BooleanField(default=False)
    name = models.CharField(max_length=500)
    token = models.CharField(max_length=100)

    def __str__(self):
        return self.name
