from django import forms
from multiupload.fields import MultiFileField

from .models import Album, Photo


class AlbumForm(forms.ModelForm):
    class Meta:
        model = Album
        fields = [
            'title',
            'author',
            'editor',
            'cover_photo',
            'description',
            'draft',
        ]

    images = MultiFileField(min_num=1, max_num=9999, max_file_size=1024 * 1024 * 20)

    def save(self, commit=True):
        instance = super(AlbumForm, self).save(commit)
        for each in self.cleaned_data['images']:
            Photo.objects.create(image=each, album=instance)
        return instance


class PhotoForm(forms.ModelForm):
    image = forms.ImageField(label='Image')

    class Meta:
        model = Photo
        fields = [
            'title',
            'author',
            'editor',
            'image_name',
            "image_path",
            'description',
        ]
