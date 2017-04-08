from django.conf.urls import url

from .views import (
    album_list,
    album_create,
    album_detail,
    album_detail_preview,
    album_update,
    album_delete,
    set_cover_photo,
)

urlpatterns = [
    # url(r'^home/$', views.home, name='home'),
    url(r'^$', album_list, name='list'),
    url(r'^create/$', album_create, name='create'),
    url(r'^(?P<author_username>[\w.@+-]+)/(?P<slug>[\w-]+)/$', album_detail, name='detail'),
    url(r'^(?P<author_username>[\w.@+-]+)/(?P<slug>[\w-]+)/preview/$', album_detail_preview, name='preview'),
    url(r'^(?P<author_username>[\w.@+-]+)/(?P<slug>[\w-]+)/edit/$', album_update, name='update'),
    url(r'^(?P<author_username>[\w.@+-]+)/(?P<slug>[\w-]+)/delete/$', album_delete, name='delete'),
    url(r'^(?P<author_username>[\w.@+-]+)/(?P<slug>[\w-]+)/set_cover_photo/(?P<id>[0-9]+)/$', set_cover_photo,
        name='set_cover_photo'),

]
