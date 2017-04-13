from django.contrib import messages
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.http import Http404, HttpResponsePermanentRedirect
from django.shortcuts import get_object_or_404, redirect, render

from albums.models import Album
from albums.views import create_cover_photo
from .forms import PhotoForm
from .models import Photo


def photo_detail(request, id):
    photo = get_object_or_404(Photo, id=id)
    if photo.album.draft:
        if not (request.user.is_staff or request.user.is_superuser):
            raise Http404
    album = photo.album
    photos = Photo.objects.filter(album=album).values().order_by('title')
    prev_idx = -1
    next_idx = len(photos)
    idx = 0
    for p in photos:
        if p.get('id') == photo.id:
            prev_idx = idx - 1
            next_idx = idx + 1
            break
        idx += 1
    prev_photo = photos[prev_idx] if prev_idx > -1 else None
    next_photo = photos[next_idx] if next_idx < len(photos) else None

    context = {
        "title": photo.title,
        "photo": photo,
        "prev_photo": prev_photo,
        "next_photo": next_photo,
        "album": album
    }
    return render(request, "photo_detail.html", context)


def photo_create(request):
    if not (request.user.is_staff or request.user.is_superuser):
        raise Http404
    form = PhotoForm(request.POST or None, request.FILES or None)
    if form.is_valid():
        instance = form.save(commit=True)
        # instance.editor = request.user
        instance.save()
        messages.success(request, "Photo Successfully Uploaded!")
        # populate exif info to photo
        instance.post_process()
        return HttpResponsePermanentRedirect(instance.get_absolute_url())
    elif form.errors:
        messages.error(request, "Photo NOT Successfully Uploaded!")
    context = {
        "form": form
    }
    return render(request, "photo_form.html", context)


def photo_update(request, id=id):
    if not (request.user.is_staff or request.user.is_superuser):
        raise Http404
    photo = get_object_or_404(Photo, id=id)
    if photo:
        title = photo.title
    form = PhotoForm(request.POST or None, request.FILES or None, instance=photo)
    if form.is_valid():
        photo = form.save(commit=True)
        photo.save()
        messages.success(request, "Photo Successfully Updated!")
        return HttpResponsePermanentRedirect(photo.get_absolute_url())
    elif form.errors:
        messages.error(request, "Photo NOT Successfully Updated!")
    update = True
    context = {
        "photo": photo,
        "form": form,
        "update": update
    }
    return render(request, "photo_form.html", context)


def photo_delete(request, id=id):
    if not request.user.is_staff or not request.user.is_superuser:
        raise Http404
    photo = get_object_or_404(Photo, id=id)
    print('photo.id', photo.id)
    album = photo.album
    photos = Photo.objects.filter(album=album).values().order_by('title')

    prev_idx = -1
    next_idx = len(photos)
    idx = 0
    for p in photos:
        if str(p.get('id')) == str(photo.id):
            prev_idx = idx - 1
            next_idx = idx + 1
            break
        idx += 1
    prev_photo = photos[prev_idx] if prev_idx > -1 else None
    next_photo = photos[next_idx] if next_idx < len(photos) else None

    if prev_photo is None and next_photo is None:  # no photo left in current album
        photo.delete()
        messages.success(request, "Photo Successfully Deleted!")
        return redirect("album:list")

    if next_photo is None:  # deleted photo is the last one in album
        next_photo = prev_photo

    # if current photo is cover photo of album, need to update cover photo after deletion
    if album.cover_photo == photo:
        # this must happen after 'album.cover_photo == photo' checking,
        # otherwise if the deleted photo is cover_photo, album.cover_photo will be null
        photo.delete()
        create_cover_photo(album)
    else:
        photo.delete()
    messages.success(request, "Photo Successfully Deleted!")
    return redirect("photo:detail", id=next_photo.get('id'))


