from django.contrib import messages
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db.models import Q
from django.http import Http404, HttpResponsePermanentRedirect
from django.shortcuts import get_object_or_404, redirect, render

from src.blog.util.slug import create_naive_slug
from .forms import AlbumForm, PhotoForm
from .models import Album, Photo, create_slug


def album_create(request):
    if not (request.user.is_staff or request.user.is_superuser):
        raise Http404
    form = AlbumForm(request.POST or None, request.FILES or None)
    import datetime
    print ("##start##")
    print (datetime.datetime.now())
    if form.is_valid():
        instance = form.save(commit=True)
        instance.editor = request.user
        # populate exif info to photos
        post_process_photos(instance)
        # update album cover photo
        create_cover_photo(instance)

        instance.save()
        messages.success(request, "Album Successfully Created!")

        print ("##end##")
        print (datetime.datetime.now())
        return HttpResponsePermanentRedirect(instance.get_absolute_url())
    elif form.errors:
        messages.error(request, "Album NOT Successfully Created!")
    context = {
        "form": form
    }
    return render(request, "album_form.html", context)


def album_detail(request, author_username, slug):
    # instance = get_object_or_404(Album, slug=slug)
    instance_set = Album.objects.filter(author__username__exact=author_username, slug__exact=slug)
    if not instance_set or len(instance_set) != 1:
        raise Http404
    instance = instance_set.first()
    if instance.draft:
        if not (request.user.is_staff or request.user.is_superuser):
            raise Http404
    photos = instance.photo_set.all()

    item_count = 9
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

    context = {
        "title": instance.title,
        "instance": instance,
        "photos": queryset,
        "photos_group": grouped(queryset, 3),
        "page_request_var": page_request_var,
    }

    return render(request, "album_detail.html", context)


def album_list(request):
    if Album is None:
        raise Http404
    queryset_list = Album.objects.active()  # .order_by('-timestamp')
    user_can_edit = False
    if request.user.is_staff or request.user.is_superuser:
        queryset_list = Album.objects.all()
        user_can_edit = True

    query = request.GET.get('q')
    if query:
        queryset_list = queryset_list.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query) |
            Q(author__first_name__icontains=query) |
            Q(author__last_name__icontains=query)
        ).distinct()

    item_count = 9
    paginator = Paginator(queryset_list, item_count)  # Show item_count per page
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
        "object_list": queryset,
        "object_list_group": grouped(queryset, 3),
        "title": "All Albums",
        "page_request_var": page_request_var,
        "user_can_edit": user_can_edit
    }
    return render(request, "album_list.html", context)


def album_update(request, author_username, slug=None):
    if not (request.user.is_staff or request.user.is_superuser):
        raise Http404
    # instance = get_object_or_404(Album, slug=slug)
    instance_set = Album.objects.filter(author__username__exact=author_username, slug__exact=slug)
    instance = instance_set.first()
    if instance:
        title = instance.title
    form = AlbumForm(request.POST or None, request.FILES or None, instance=instance)
    if form.is_valid():
        instance = form.save(commit=False)
        # 1.covert to naive slug if cur slug has ts but slug without ts(naive_slug) has been deleted (fu2 zheng4!)
        naive_slug = create_naive_slug(title)
        naive_instance_set = Album.objects.filter(author__username__exact=author_username, slug__exact=naive_slug)
        naive_slug_album_deleted = not naive_instance_set
        # 2.change slug if title updated
        if naive_slug_album_deleted or instance.title != title:
            instance.slug = create_slug(instance)
        instance.editor = request.user
        create_cover_photo(instance)
        instance.save()
        messages.success(request, "Album Successfully Updated!")
        # populate exif info to photos
        post_process_photos(instance)
        return HttpResponsePermanentRedirect(instance.get_absolute_url())
    elif form.errors:
        messages.error(request, "Album NOT Successfully Updated!")
    update = True
    context = {
        "title": instance.title,
        "instance": instance,
        "form": form,
        "update": update
    }
    return render(request, "album_form.html", context)


def album_delete(request, author_username, slug=None):
    if not request.user.is_staff or not request.user.is_superuser:
        raise Http404
    # instance = get_object_or_404(Album, slug=slug)
    instance_set = Album.objects.filter(author__username__exact=author_username, slug__exact=slug)
    instance = instance_set.first()
    # delete all photos under album
    photo_set = Photo.objects.filter(album=instance)
    for photo in photo_set:
        photo.delete()
    instance.delete()
    messages.success(request, "Album Successfully Deleted!")
    return redirect("album:list")


def photo_detail(request, id):
    instance = get_object_or_404(Photo, id=id)
    if instance.album.draft:
        if not (request.user.is_staff or request.user.is_superuser):
            raise Http404
    context = {
        "title": instance.title,
        "instance": instance,
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
    instance = get_object_or_404(Photo, id=id)
    if instance:
        title = instance.title
    form = PhotoForm(request.POST or None, request.FILES or None, instance=instance)
    if form.is_valid():
        instance = form.save(commit=True)
        instance.save()
        messages.success(request, "Photo Successfully Updated!")
        return HttpResponsePermanentRedirect(instance.get_absolute_url())
    elif form.errors:
        messages.error(request, "Photo NOT Successfully Updated!")
    update = True
    context = {
        "title": instance.title,
        "instance": instance,
        "form": form,
        "update": update
    }
    return render(request, "photo_form.html", context)


def photo_delete(request, id=id):
    if not request.user.is_staff or not request.user.is_superuser:
        raise Http404
    instance = get_object_or_404(Photo, id=id)
    album = instance.album
    photo_url = instance.image.url
    instance.delete()
    # if current photo is cover photo of album, need to update cover photo after deletion
    if album.cover_photo_url == photo_url:
        create_cover_photo(album)
    messages.success(request, "Photo Successfully Deleted!")
    return redirect("album:list")


# this needs to be moved to util module
def grouped(l, n):
    for i in range(0, len(l), n):
        yield l[i:i + n]


def post_process_photos(album):
    photos = album.photo_set.all()
    if photos:
        for photo in photos:
            photo.post_process()


# use the first image of the album when creating
def create_cover_photo(album):
    album.cover_photo_url = ''
    if album.photo_set and album.photo_set.order_by('title').first() is not None:
        cover_photo_url = album.photo_set.order_by('title').first().image.url
        album.cover_photo_url = cover_photo_url
        album.save()
