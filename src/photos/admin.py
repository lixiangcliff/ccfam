from django.contrib import admin
from .forms import PhotoForm
from .models import Photo


class PhotoModelAdmin(admin.ModelAdmin):
    list_display = ["id", "title", "album", "image_name", "width", "height", "size", "image_path", "author", "editor",
                    "orientation", "updated_time", "created_time", "taken_time", "address", "device_make",
                    "device_model", "latitude", "longitude"]
    list_filter = ["author", "editor", "updated_time", "created_time"]
    search_fields = ["title", "author", "editor", "description"]

    form = PhotoForm

    class Meta:
        model = Photo


admin.site.register(Photo, PhotoModelAdmin)
