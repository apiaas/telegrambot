from django.db import models


class Client(models.Model):
    telegram_id = models.IntegerField(null=True, blank=True, unique=True)
    first_name = models.CharField(blank=True, max_length=500)
    last_name = models.CharField(blank=True, max_length=500)

    @property
    def name(self):
        return '{} {}'.format(self.first_name, self.last_name)

    def __str__(self):
        return self.name
