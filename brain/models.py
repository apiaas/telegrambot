from django.db import models
from jsonfield import JSONField
import collections


class Client(models.Model):
    telegram_id = models.IntegerField(null=True, blank=True, unique=True)
    token = models.CharField(blank=True, max_length=500)
    first_name = models.CharField(blank=True, max_length=500)
    last_name = models.CharField(blank=True, max_length=500)
    password = models.CharField(blank=True, max_length=500)
    data = JSONField(
        blank=True, load_kwargs={'object_pairs_hook': collections.OrderedDict}
    )

    @property
    def name(self):
        return '{} {}'.format(self.first_name, self.last_name)

    def __str__(self):
        return self.name
