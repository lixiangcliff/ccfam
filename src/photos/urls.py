from django.conf.urls import url

from .views import (
    photo_create,
    photo_detail,
    photo_update,
    photo_delete
)

urlpatterns = [
    url(r'^create/$', photo_create, name='photo_create'),
    url(r'^(?P<id>[0-9]+)/$', photo_detail, name='photo_detail'),
    url(r'^(?P<id>[0-9]+)/edit$', photo_update, name='photo_update'),
    url(r'^(?P<id>[0-9]+)/delete', photo_delete, name='photo_delete'),

]