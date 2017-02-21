from django.conf import settings
from django.db import models


# Create your models here.


class Album(models.Model):
    title = models.CharField(max_length=120)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, default=1)
    description = models.TextField(blank=True)
    slug = models.SlugField(unique=True)
    draft = models.BooleanField(default=True)
    created_time = models.DateTimeField(auto_now=False, auto_now_add=True)
    updated_time = models.DateTimeField(auto_now=True, auto_now_add=False)

    def __str__(self):  # python3
        return self.title
