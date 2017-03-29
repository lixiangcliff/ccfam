from django.conf.urls import url

from . import views

urlpatterns = [
    #url(r'^home/$', views.home, name='home'),
    url(r'^$', views.album_list, name='list'),
    # temp workaround below, need to move photo out of album
    url(r'^photo/create/$', views.photo_create, name='photo_create'),
    url(r'^photo/(?P<id>[0-9]+)/$', views.photo_detail, name='photo_detail'),
    url(r'^photo/(?P<id>[0-9]+)/edit$', views.photo_update, name='photo_update'),
    url(r'^photo/(?P<id>[0-9]+)/delete', views.photo_delete, name='photo_delete'),
    # temp workaround above, need to move photo out of album
    url(r'^create/$', views.album_create, name='create'),
    url(r'^(?P<author_username>[\w.@+-]+)/(?P<slug>[\w-]+)/display_to_preview/$', views.album_display_to_preview, name='display_to_preview'),
    url(r'^(?P<author_username>[\w.@+-]+)/(?P<slug>[\w-]+)/$', views.album_detail, name='detail'),
    url(r'^(?P<author_username>[\w.@+-]+)/(?P<slug>[\w-]+)/preview/$', views.album_detail_preview, name='preview'),
    url(r'^(?P<author_username>[\w.@+-]+)/(?P<slug>[\w-]+)/edit/$', views.album_update, name='update'),
    url(r'^(?P<author_username>[\w.@+-]+)/(?P<slug>[\w-]+)/delete/$', views.album_delete, name='delete'),
    url(r'^(?P<author_username>[\w.@+-]+)/(?P<slug>[\w-]+)/set_cover_photo/(?P<id>[0-9]+)/$', views.set_cover_photo, name='set_cover_photo'),

]