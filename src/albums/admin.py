from django.contrib import admin

from .forms import AlbumForm
from .models import Album


class AlbumModelAdmin(admin.ModelAdmin):
    list_display = ["title", "author", "editor", "cover_photo_url", "slug", "draft", "updated_time", "created_time"]
    list_filter = ["author", "editor", "updated_time", "created_time"]
    search_fields = ["title", "author", "description"]

    form = AlbumForm

    class Meta:
        model = Album


admin.site.register(Album, AlbumModelAdmin)
