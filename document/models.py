from django.db import models
from django.conf import settings
from brain.models import Client


class Document(models.Model):
    processed_text = models.TextField(default='')
    file_id = models.CharField(max_length=100, default='')
    author = models.ForeignKey(Client, default=-1)


