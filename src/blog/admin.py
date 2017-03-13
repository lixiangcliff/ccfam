from django.contrib import admin

from .forms import AlbumForm, PhotoForm, ContactForm
from .models import Album, Photo, MyMessage, Attachment


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

class ContactModelAdmin(admin.ModelAdmin):
    list_display = ["author_name", "author_email", "content"]

    form = ContactForm
    class Meta:
        model = MyMessage


class AttachmentModelAdmin(admin.ModelAdmin):
    list_display = ["message", ]

    class Meta:
        model = Attachment

admin.site.register(Album, AlbumModelAdmin)
admin.site.register(Photo, PhotoModelAdmin)
admin.site.register(MyMessage, ContactModelAdmin)
admin.site.register(Attachment, AttachmentModelAdmin)

