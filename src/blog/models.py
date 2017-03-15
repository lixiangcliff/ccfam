from django.conf import settings
from django.db import models
from django.urls import reverse

from .util.photo import get_exif_data
from .util.slug import create_slug


class AlbumManager(models.Manager):
    # to show non-draft instance only
    def active(self, *args, **kwargs):
        return super(AlbumManager, self).filter(draft=False)


def upload_location(instance, filename):
    AlbumModel = instance.__class__
    new_id = AlbumModel.objects.order_by('id').last().id + 1
    return '%s/%s' % (new_id, filename)


class Album(models.Model):
    title = models.CharField(max_length=120)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, default=1)
    editor = models.ForeignKey(settings.AUTH_USER_MODEL, default=1, related_name="+")
    # recursive definition?
    # cover_photo = models.ForeignKey(Photo, verbose_name=_('cover_photo'), blank=True)
    cover_photo = models.URLField(blank=True)
    description = models.TextField(blank=True)
    # image = models.ImageField(upload_to=upload_location, null=True, blank=True, width_field='width_field',
    #                           height_field='height_field')
    # width_field = models.IntegerField(default=0)
    # height_field = models.IntegerField(default=0)
    slug = models.SlugField(unique=True)
    draft = models.BooleanField(default=False)
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
        return reverse("album:detail", kwargs={"slug": self.slug})

    def get_absolute_url_edit(self):
        return reverse("album:update", kwargs={"slug": self.slug})

    class Meta:
        ordering = ["-created_time", "-updated_time"]


def upload_location_photo(instance, filename):
    author = instance.album.author
    title = instance.album.slug
    modi_filename = filename.replace(' ', '_')
    return 'photos/%s/%s/%s' % (author, title, modi_filename)


def get_device_make(image):
    return get_exif_data(image)['Make']


def get_photo_title():
    pass


class Photo(models.Model):
    # required
    title = models.CharField(max_length=120)  # author + file_name
    author = models.ForeignKey(settings.AUTH_USER_MODEL, default=1)
    editor = models.ForeignKey(settings.AUTH_USER_MODEL, default=1, related_name="+")

    album = models.ForeignKey(Album, verbose_name='album')
    image_name = models.CharField(max_length=128) # photo original file name
    image_location = models.CharField(max_length=256)
    # order matters! file_name and file_location must locate in front of file
    # otherwise there will be csrf_token issue
    image = models.ImageField('Photo', upload_to=upload_location_photo, width_field='width_field', height_field='height_field')

    width_field = models.IntegerField(default=0)
    height_field = models.IntegerField(default=0)

    # slug = models.SlugField(unique=True) # not useful
    created_time = models.DateTimeField(auto_now=False, auto_now_add=True)
    updated_time = models.DateTimeField(auto_now=True, auto_now_add=False)
    # optional
    description = models.TextField(blank=True)

    # device_make = models.CharField(default=get_device_make(upload_location_photo), max_length=120)
    # device_model = models.CharField(max_length=120, blank=True)
    # taken_time = models.DateTimeField(auto_now=False, auto_now_add=False, blank=True)
    # latitude = models.DecimalField(max_digits=8, decimal_places=6, blank=True, null=True)
    # longitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)

    def save(self, *args, **kwargs):
        # create title
        self.title = '[' + self.author.username + ']: ' + self.image.name
        self.image_name = self.image.name
        self.image_location = upload_location_photo(self, self.image.name)
        #self.image_location = self.image.url

        # create slug
        # if self.slug is None or self.slug == "":
        #     self.slug = create_slug(self)

        # exif_data = get_exif_data_by_image_path(self.image.url)
        # print (exif_data['Make'])
        super(Photo, self).save(*args, **kwargs)

    def __str__(self):  # python3
        return self.title

    # def get_device_make(self):
    #     return get_exif_data(self.image)['Make']
    #
    # def get_device_model(self):
    #     return get_exif_data(self.image)['Model']
    #
    # def get_taken_time(self):
    #     return get_exif_data(self.image)['DateTime']
    #
    # def get_latitude(self):
    #     return get_lat_lon(get_exif_data(self.image))[0]
    #
    # def get_longitude(self):
    #     return get_lat_lon(get_exif_data(self.image))[1]
    #
    # def get_photo_title(self):
    #     pass

    def get_absolute_url(self):
        return reverse("album:photo_detail", kwargs={"id": self.id})

    def get_absolute_url_edit(self):
        return reverse("album:update", kwargs={"slug": self.slug})

    class Meta:
        ordering = ["image_name", "created_time", "updated_time"]
