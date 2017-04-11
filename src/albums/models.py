from django.conf import settings
from django.db import models
from django.urls import reverse

from util.slug import create_slug


class AlbumManager(models.Manager):
    # to show non-draft instance only
    def active(self, *args, **kwargs):
        return super(AlbumManager, self).filter(draft=False)


def upload_location(instance, filename):
    AlbumModel = instance.__class__
    new_id = AlbumModel.objects.order_by('id').last().id + 1
    return '%s/%s' % (new_id, filename)


class Album(models.Model):
    title = models.CharField(max_length=128)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, default=1)
    editor = models.ForeignKey(settings.AUTH_USER_MODEL, default=1, related_name="+")
    # cover_photo_url = models.CharField(max_length=256, null=True, blank=True)
    cover_photo = models.ForeignKey('photos.Photo', verbose_name='cover_photo', related_name='+', null=True, blank=True)
    description = models.TextField(blank=True)
    slug = models.SlugField(null=False, blank=False)
    draft = models.BooleanField(default=True)
    created_time = models.DateTimeField(auto_now=False, auto_now_add=True)
    updated_time = models.DateTimeField(auto_now=True, auto_now_add=False)

    objects = AlbumManager()

    def save(self, *args, **kwargs):
        if self.slug is None or self.slug == "":
            self.slug = create_slug(self)
        super(Album, self).save(*args, **kwargs)

    def __str__(self):  # python3
        return self.title

    def get_absolute_url(self):
        return reverse("album:detail", kwargs={"slug": self.slug, "author_username": self.author.username})

    def get_absolute_url_preview(self):
        return reverse("album:preview", kwargs={"slug": self.slug, "author_username": self.author.username})

    def get_absolute_url_preview(self):
        return reverse("album:preview", kwargs={"slug": self.slug, "author_username": self.author.username})

    def get_absolute_url_edit(self):
        return reverse("album:update", kwargs={"slug": self.slug, "author_username": self.author.username})

    class Meta:
        ordering = ["-created_time", "-updated_time"]


