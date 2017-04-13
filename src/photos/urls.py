from django.conf.urls import url

from .views import (
    photo_create,
    photo_detail,
    photo_update,
    photo_delete
)

urlpatterns = [
    url(r'^create/$', photo_create, name='create'),
    url(r'^(?P<id>[0-9]+)/$', photo_detail, name='detail'),
    url(r'^(?P<id>[0-9]+)/edit$', photo_update, name='update'),
    url(r'^(?P<id>[0-9]+)/delete', photo_delete, name='delete'),

]