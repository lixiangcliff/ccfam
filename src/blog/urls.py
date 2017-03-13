from django.conf.urls import url

from . import views

urlpatterns = [
    #url(r'^home/$', views.home, name='home'),
    url(r'^$', views.album_list, name='list'),
    url(r'^create/$', views.album_create, name='create'),
    url(r'^test/$', views.ContactView.as_view()),
    url(r'^(?P<slug>[\w-]+)/$', views.album_detail, name='detail'),
    url(r'^(?P<slug>[\w-]+)/edit/$', views.album_update, name='update'),
    url(r'^(?P<slug>[\w-]+)/delete/$', views.album_delete, name='delete'),

]