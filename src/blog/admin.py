from django.contrib import admin

from .forms import AlbumForm, PhotoForm, Album2Form
from .models import Album, Photo, Album2, Attachment


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

class Album2ModelAdmin(admin.ModelAdmin):
    list_display = ["title", "author_email", "content"]

    form = Album2Form
    class Meta:
        model = Album2


class AttachmentModelAdmin(admin.ModelAdmin):
    list_display = ["album", "file_name", "file_location"]

    class Meta:
        model = Attachment

admin.site.register(Album, AlbumModelAdmin)
admin.site.register(Photo, PhotoModelAdmin)
admin.site.register(Album2, Album2ModelAdmin)
admin.site.register(Attachment, AttachmentModelAdmin)

