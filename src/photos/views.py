from django.contrib import messages
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.http import Http404, HttpResponsePermanentRedirect
from django.shortcuts import get_object_or_404, redirect, render

from albums.views import create_cover_photo
from .forms import PhotoForm
from .models import Photo


def photo_detail(request, id):
    photo = get_object_or_404(Photo, id=id)
    if photo.album.draft:
        if not (request.user.is_staff or request.user.is_superuser):
            raise Http404
    album = photo.album
    user_can_edit = False
    if request.user.is_staff or request.user.is_superuser:
        user_can_edit = True
    photos = album.photo_set.all()


    item_count = 1
    paginator = Paginator(photos, item_count)  # Show item_count per page
    page_request_var = 'page'
    page = request.GET.get(page_request_var)
    try:
        queryset = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        queryset = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        queryset = paginator.page(paginator.num_pages)

    # context['object_list'] = grouped(Bar.objects.all(), 4)

    context = {
        "title": photo.title,
        "photo": photo,
        "photos": queryset,
        #"photos_group": grouped(queryset, 3),
        "page_request_var": page_request_var,
        "user_can_edit": user_can_edit,
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
    album = photo.album
    photo_url = photo.image.url
    photo.delete()
    # if current photo is cover photo of album, need to update cover photo after deletion
    if album.cover_photo == photo_url:
        create_cover_photo(album)
    messages.success(request, "Photo Successfully Deleted!")
    return redirect("album:list")

