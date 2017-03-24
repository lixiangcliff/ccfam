import os

from django.conf import settings
from django.db import models
from django.urls import reverse

from .util.geo import get_location_by_coordinate
from .util.photo import get_exif_data_by_image_path, get_lat_lon
from .util.slug import create_slug
from .util.time import get_datetime_by_string


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
    # recursive definition?
    # cover_photo = models.ForeignKey(Photo, verbose_name=_('cover_photo'), null=True, blank=True)
    cover_photo = models.URLField(blank=True)
    description = models.TextField(blank=True)
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
        return reverse("album:detail", kwargs={"slug": self.slug, "author_username": self.author.username})

    def get_absolute_url_edit(self):
        return reverse("album:update", kwargs={"slug": self.slug, "author_username": self.author.username})

    class Meta:
        ordering = ["-created_time", "-updated_time"]


def upload_location_photo(instance, filename):
    author = instance.album.author
    title = instance.album.slug
    filename = filename.replace(' ', '_')
    filename = filename.replace(',', '')
    return 'photos/%s/%s/%s' % (author, title, filename)


class Photo(models.Model):
    # required
    title = models.CharField(max_length=128)  # author + file_name
    author = models.ForeignKey(settings.AUTH_USER_MODEL, default=1)
    editor = models.ForeignKey(settings.AUTH_USER_MODEL, default=1, related_name="+")

    album = models.ForeignKey(Album, verbose_name='album')
    image_name = models.CharField(max_length=128)  # photo original file name
    image_path = models.CharField(max_length=256)
    # order matters! file_name and file_location must locate in front of file
    # otherwise there will be csrf_token issue
    image = models.ImageField('Photo', upload_to=upload_location_photo, null=True, blank=True)
    created_time = models.DateTimeField(auto_now=False, auto_now_add=True)
    updated_time = models.DateTimeField(auto_now=True, auto_now_add=False)
    # optional
    width = models.IntegerField(default=0, null=True, blank=True)
    height = models.IntegerField(default=0, null=True, blank=True)
    size = models.BigIntegerField(default=0, null=True, blank=True)
    description = models.TextField(blank=True)
    device_make = models.CharField(max_length=128, null=True, blank=True)
    device_model = models.CharField(max_length=128, null=True, blank=True)
    orientation = models.CharField(max_length=2, null=True, blank=True)
    taken_time = models.DateTimeField(auto_now=False, auto_now_add=False, null=True, blank=True)
    latitude = models.DecimalField(max_digits=8, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    address = models.CharField(max_length=256, null=True, blank=True)

    def save(self, *args, **kwargs):
        # create title
        image_basename = os.path.basename(self.image.name)
        self.title = '[' + self.author.username + ']: ' + image_basename
        self.image_name = image_basename
        self.image_path = upload_location_photo(self, image_basename)
        super(Photo, self).save(*args, **kwargs)

    def post_process(self):
        # populate exif infos
        exif_data = get_exif_data_by_image_path(settings.MEDIA_ROOT + "/" + self.image_path)
        self.width = self.get_width(exif_data)
        self.height = self.get_height(exif_data)
        self.device_make = self.get_device_make(exif_data)
        self.device_model = self.get_device_model(exif_data)
        self.orientation = self.get_orientation(exif_data)
        self.taken_time = self.get_taken_time(exif_data)
        self.latitude = self.get_latitude(exif_data)
        self.longitude = self.get_longitude(exif_data)
        self.address = self.get_address(exif_data)
        # update other field
        self.author = self.album.author
        self.editor = self.album.editor

        # rotate image if needed
        self.rotate_and_compress_image()
        self.size = self.image.size

        super(Photo, self).save(
            update_fields=["author", "editor", "width", "height", "size", "orientation", "device_make", "device_model",
                           "taken_time", "latitude", "longitude", "address"])

    def __str__(self):  # python3
        return self.title

    # http://stackoverflow.com/questions/22045882/modify-or-delete-exif-tag-orientation-in-python
    # http://piexif.readthedocs.io/en/latest/sample.html?highlight=orientation
    def rotate_and_compress_image(self):
        filename = self.image
        from PIL import Image
        import piexif

        img = Image.open(filename)
        if "exif" in img.info:
            exif_dict = piexif.load(img.info["exif"])

            if piexif.ImageIFD.Orientation in exif_dict["0th"]:
                orientation = exif_dict["0th"].pop(piexif.ImageIFD.Orientation)
                exif_bytes = piexif.dump(exif_dict)

                if orientation == 2:
                    img = img.transpose(Image.FLIP_LEFT_RIGHT)
                elif orientation == 3:
                    img = img.rotate(180, expand=True)
                elif orientation == 4:
                    img = img.rotate(180, expand=True).transpose(Image.FLIP_LEFT_RIGHT)
                elif orientation == 5:
                    img = img.rotate(-90, expand=True).transpose(Image.FLIP_LEFT_RIGHT)
                elif orientation == 6:
                    img = img.rotate(-90, expand=True)
                elif orientation == 7:
                    img = img.rotate(90, expand=True).transpose(Image.FLIP_LEFT_RIGHT)
                elif orientation == 8:
                    img = img.rotate(90, expand=True)

                img.save(self.image.file.name, overwrite=True, optimize=True, quality=settings.IMAGE_QUALITY, exif=exif_bytes)

    def get_width(self, exif_data):
        return exif_data.get('ExifImageWidth', None)

    def get_height(self, exif_data):
        return exif_data.get('ExifImageHeight', None)

    def get_device_make(self, exif_data):
        return exif_data.get('Make', None)

    def get_device_model(self, exif_data):
        return exif_data.get('Model', None)

    def get_orientation(self, exif_data):
        return exif_data.get('Orientation', None)

    def get_taken_time(self, exif_data):
        return get_datetime_by_string(exif_data.get('DateTime', None))

    def get_latitude(self, exif_data):
        return get_lat_lon(exif_data)[0]

    def get_longitude(self, exif_data):
        return get_lat_lon(exif_data)[1]

    def get_address(self, exif_data):
        if get_lat_lon(exif_data)[0] is None:
            return ""
        else:
            return get_location_by_coordinate(get_lat_lon(exif_data)[0], get_lat_lon(exif_data)[1])

    def get_photo_title(self):
        pass

    def get_absolute_url(self):
        return reverse("album:photo_detail", kwargs={"id": self.id})

    # def get_absolute_url_edit(self):
    #     return reverse("album:update", kwargs={"slug": self.slug})

    class Meta:
        ordering = ["image_name", "created_time", "updated_time"]
