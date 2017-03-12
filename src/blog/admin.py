from django.contrib import admin

from .forms import AlbumForm, PhotoForm
from .models import Album, Photo


class AlbumModelAdmin(admin.ModelAdmin):
    list_display = ["title", "author", "slug", "updated_time", "created_time"]
    list_filter = ["author", "updated_time", "created_time"]
    search_fields = ["title", "author", "description"]

    form = AlbumForm
    class Meta:
        model = Album


class PhotoModelAdmin(admin.ModelAdmin):
    list_display = ["title", "file_name", "author", "editor", "slug", "updated_time", "created_time"]
    list_filter = ["author", "editor", "updated_time", "created_time"]
    search_fields = ["title", "author", "editor", "description"]

    form = PhotoForm
    class Meta:
        model = Photo

admin.site.register(Album, AlbumModelAdmin)
admin.site.register(Photo, PhotoModelAdmin)

