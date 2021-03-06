"""ccfam URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.static import static
from django.contrib import admin
# from albums import views
from ccfam import views as ccfam_views

# may need to change per:
# https://github.com/codingforentrepreneurs/Guides/blob/master/all/common_url_regex.md
urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^$', ccfam_views.home, name='home'),
    url(r'^home/$', ccfam_views.home, name='home'),
    url(r'^about/$', ccfam_views.about, name='about'),
    url(r'^contact/$', ccfam_views.contact, name='contact'),
    url(r'^albums/', include('albums.urls', namespace='album')),
    url(r'^photos/', include('photos.urls', namespace='photo')),
    url(r'^accounts/', include('registration.backends.default.urls')),

]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
