import os

from django.conf import settings
from django.db import models
from django.urls import reverse

from albums.models import Album
from src.util.time import get_datetime_by_string
from util.geo import get_location_by_coordinate
from util.photo import get_exif_data, get_lat_lon, rotate_and_compress_image, is_jpeg, get_image
# from src.ccfam import settings as ccfam_settings

def upload_location_photo(instance, filename):
    author = instance.album.author
    album_title = instance.album.slug
    filename = filename.replace(' ', '_')
    filename = filename.replace(',', '')
    return 'photos/%s/%s/%s' % (author, album_title, filename)


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
        pil_image = get_image(self.image_path) # Pillow Image object
        image_is_jpeg = is_jpeg(pil_image)
        # if jpeg
        # populate exif infos
        if image_is_jpeg:
            exif_data = get_exif_data(pil_image)
            # self.width must be put in post_process()
            # cuz we use this to check whether a photo has been processed in views.post_process_photos()
            self.width = self.get_width(exif_data)
            self.height = self.get_height(exif_data)
            self.device_make = self.get_device_make(exif_data)
            self.device_model = self.get_device_model(exif_data)
            self.orientation = self.get_orientation(exif_data)
            self.taken_time = self.get_taken_time(exif_data)
            lan_and_lon = get_lat_lon(exif_data)
            self.latitude = lan_and_lon[0]
            self.longitude = lan_and_lon[1]
            self.address = self.get_address(exif_data)

            # rotate image if needed
            print('self.image.file.name', self.image.file.name)
            print('self.image_path', self.image_path)
            rotate_and_compress_image(pil_image, self)
            self.size = self.image.size
        else: # not jpeg
            pass

        # update other field
        self.author = self.album.author
        self.editor = self.album.editor

        super(Photo, self).save(
            update_fields=["author", "editor", "width", "height", "size", "orientation", "device_make", "device_model",
                           "taken_time", "latitude", "longitude", "address"])

    def __str__(self):  # python3
        return self.title

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
        if not self.latitude:
            return ""
        else:
            return get_location_by_coordinate(get_lat_lon(exif_data)[0], get_lat_lon(exif_data)[1])

    def get_photo_title(self):
        pass

    def get_absolute_url(self):
        return reverse("photo:detail", kwargs={"id": self.id})

    def get_absolute_url_edit(self):
        return reverse("photo:update", kwargs={"id": self.id})

    def get_absolute_url_delete(self):
        return reverse("photo:delete", kwargs={"id": self.id})

    class Meta:
        ordering = ["title", "created_time", "updated_time"]
