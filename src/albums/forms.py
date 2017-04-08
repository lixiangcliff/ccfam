from django import forms
from .util.multiupload.multiupload import MultiFileField

from .models import Album
from photos.models import Photo


class AlbumForm(forms.ModelForm):
    class Meta:
        model = Album
        fields = [
            'title',
            'author',
            'description',
            'draft',
        ]

    images = MultiFileField(min_num=0, max_num=9999, max_file_size=1024 * 1024 * 20, required=False)

    def save(self, commit=True):
        instance = super(AlbumForm, self).save(commit)
        for each in self.cleaned_data['images']:
            Photo.objects.create(image=each, album=instance, author=instance.author, editor=instance.editor)
        return instance




class CoverPhotoForm(forms.ModelForm):

    class Meta:
        model = Album
        fields = [
            'cover_photo_url',
        ]
