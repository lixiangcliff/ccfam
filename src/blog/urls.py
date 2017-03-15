from django.conf.urls import url

from . import views

urlpatterns = [
    #url(r'^home/$', views.home, name='home'),
    url(r'^$', views.album_list, name='list'),
    url(r'^create/$', views.album_create, name='create'),
    url(r'^(?P<slug>[\w-]+)/$', views.album_detail, name='detail'),
    url(r'^(?P<slug>[\w-]+)/edit/$', views.album_update, name='update'),
    url(r'^(?P<slug>[\w-]+)/delete/$', views.album_delete, name='delete'),
    url(r'^photo/(?P<id>[0-9]+)/$', views.photo_detail, name='photo_detail'),

]