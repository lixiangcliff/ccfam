from django.conf import settings
from django.db import models

# Create your models here.
from django.db.models.signals import pre_save
from django.urls import reverse
from django.utils.text import slugify
from .util import time


class AlbumManager(models.Manager):
    def active(self, *args, **kwargs):
        return super(AlbumManager, self).filter(draft=False)


def upload_location(instance, filename):
    AlbumModel = instance.__class__
    new_id = AlbumModel.objects.order_by('id').last().id + 1
    return '%s/%s' % (new_id, filename)


class Album(models.Model):
    title = models.CharField(max_length=120)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, default=1)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to=upload_location, null=True, blank=True, width_field='width_field',
                              height_field='height_field')
    width_field = models.IntegerField(default=0)
    height_field = models.IntegerField(default=0)
    slug = models.SlugField(unique=True)
    draft = models.BooleanField(default=True)
    created_time = models.DateTimeField(auto_now=False, auto_now_add=True)
    updated_time = models.DateTimeField(auto_now=True, auto_now_add=False)

    objects = AlbumManager()

    def __str__(self):  # python3
        return self.title

    def get_absolute_url(self):
        return reverse("album:detail", kwargs={"slug": self.slug})

    def get_absolute_url_edit(self):
        return reverse("album:update", kwargs={"slug": self.slug})

    class Meta:
        ordering = ["-created_time", "-updated_time"]


# def create_slug(instance, new_slug=None):
#     slug = slugify(instance.title)
#     if new_slug is not None:
#         slug = new_slug
#     qs = Album.objects.filter(slug=slug).order_by('-id')
#     exists = qs.exists()
#     if exists:
#         new_slug = '%s-%s' % (slug, qs.first().id)
#         return create_slug(instance, new_slug=new_slug)
#     return slug

def create_slug(instance):
    slug = slugify(instance.title)
    qs = Album.objects.filter(slug=slug)
    exists = qs.exists()
    # if it is a duplicated title, add timestamp at the end of slug
    if exists:
        slug = '%s-%s' % (slug, time.slugify_time())
    return slug


def pre_save_album_receiver(sender, instance, *args, **kwargs):
    if not instance.slug:
        instance.slug = create_slug(instance)


pre_save.connect(pre_save_album_receiver, sender=Album)
