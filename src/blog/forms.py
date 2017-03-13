from django import forms

from .models import Album, Photo


class AlbumForm(forms.ModelForm):

    class Meta:
        model = Album
        fields = [
            'title',
            'author',
            'description',
            'image',
            'draft',
        ]


class PhotoForm(forms.ModelForm):
    image = forms.ImageField(label='Image')

    class Meta:
        model = Photo
        fields = [
            #'title',
            'author',
            'editor',
            'image',
            'description',
            #'device_make',
        ]


from multiupload.fields import MultiFileField

from .models import Album2, Attachment


class Album2Form(forms.ModelForm):
    class Meta:
        model = Album2
        fields = ["title", 'author_email', 'content']  # not attachments!

    files = MultiFileField(min_num=1, max_num=3, max_file_size=1024*1024*5)

    def save(self, commit=True):
        instance = super(Album2Form, self).save(commit)
        for each in self.cleaned_data['files']:
            Attachment.objects.create(file=each, album=instance)
        return instance
