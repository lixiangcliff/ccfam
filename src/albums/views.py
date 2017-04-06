import datetime

from django.contrib import messages
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db.models import Q
from django.http import Http404, HttpResponsePermanentRedirect
from django.shortcuts import get_object_or_404, redirect, render

from src.albums.util.slug import create_naive_slug
from .forms import AlbumForm, PhotoForm, CoverPhotoForm
from .models import Album, Photo, create_slug


def album_create(request):
    if not (request.user.is_staff or request.user.is_superuser):
        raise Http404
    form = AlbumForm(request.POST or None, request.FILES or None)

    print ("##create start##")
    print (datetime.datetime.now())
    if form.is_valid():
        album = form.save(commit=True)
        album.editor = request.user
        # populate exif info to photos
        post_process_photos(album)
        # update album cover photo
        create_cover_photo(album)

        album.save()
        messages.success(request, "Album Successfully Created!")

        print ("##create end##")
        print (datetime.datetime.now())
        return HttpResponsePermanentRedirect(album.get_absolute_url())
    elif form.errors:
        messages.error(request, "Album NOT Successfully Created!")
    context = {
        "form": form
    }
    return render(request, "album_form.html", context)


def album_detail(request, author_username, slug):
    return album_detail_generic(request, author_username, slug, 9, "album_detail.html")


def album_detail_preview(request, author_username, slug):
    return album_detail_generic(request, author_username, slug, 1, "album_detail_preview.html")


def album_detail_generic(request, author_username, slug, item_count_per_page, render_page):
    album_set = Album.objects.filter(author__username__exact=author_username, slug__exact=slug)
    if not album_set or len(album_set) != 1:
        raise Http404
    user_can_edit = False
    if request.user.is_staff or request.user.is_superuser:
        user_can_edit = True
    album = album_set.first()
    if album.draft:
        if not (request.user.is_staff or request.user.is_superuser):
            raise Http404
    photos = album.photo_set.all()

    item_count_per_page = item_count_per_page
    paginator = Paginator(photos, item_count_per_page)
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
        "album": album,
        "photos": queryset,
        "photos_group": grouped(queryset, 3),
        "page_request_var": page_request_var,
        "user_can_edit": user_can_edit,
    }
    return render(request, render_page, context)

def album_list(request):
    if Album is None:
        raise Http404
    album_list = Album.objects.active()  # .order_by('-timestamp')
    user_can_edit = False
    if request.user.is_staff or request.user.is_superuser:
        album_list = Album.objects.all()
        user_can_edit = True

    query = request.GET.get('q')
    if query:
        album_list = album_list.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query) |
            Q(author__first_name__icontains=query) |
            Q(author__last_name__icontains=query)
        ).distinct()

    item_count = 9
    paginator = Paginator(album_list, item_count)  # Show item_count per page
    page_request_var = 'page'
    page = request.GET.get(page_request_var)
    try:
        albums = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        albums = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        albums = paginator.page(paginator.num_pages)

    # context['object_list'] = grouped(Bar.objects.all(), 4)

    context = {
        "albums": albums,
        #"object_list_group": grouped(albums, 3),
        "title": "All Albums",
        "page_request_var": page_request_var,
        "user_can_edit": user_can_edit
    }
    return render(request, "album_list.html", context)


def album_update(request, author_username, slug=None):
    if not (request.user.is_staff or request.user.is_superuser):
        raise Http404
    # album = get_object_or_404(Album, slug=slug)
    albums = Album.objects.filter(author__username__exact=author_username, slug__exact=slug)
    album = albums.first()
    if album:
        title = album.title
    form = AlbumForm(request.POST or None, request.FILES or None, instance=album)
    print ("##update start##")
    print (datetime.datetime.now())
    if form.is_valid():
        album = form.save(commit=False)
        # 1.covert to naive slug if cur slug has ts but slug without ts(naive_slug) has been deleted (fu2 zheng4!)
        naive_slug = create_naive_slug(title)
        naive_instance_set = Album.objects.filter(author__username__exact=author_username, slug__exact=naive_slug)
        naive_slug_album_deleted = not naive_instance_set
        # 2.change slug if title updated
        if naive_slug_album_deleted or album.title != title:
            album.slug = create_slug(album)
        album.editor = request.user
        if not album.cover_photo_url:
            create_cover_photo(album)
        album.save()
        messages.success(request, "Album Successfully Updated!")
        # populate exif info to photos
        post_process_photos(album)
        print ("##update end##")
        print (datetime.datetime.now())

        return HttpResponsePermanentRedirect(album.get_absolute_url())
    elif form.errors:
        messages.error(request, "Album NOT Successfully Updated!")
    update = True
    context = {
        "album": album,
        "form": form,
        "update": update
    }
    return render(request, "album_form.html", context)


def album_delete(request, author_username, slug=None):
    if not request.user.is_staff or not request.user.is_superuser:
        raise Http404
    # album = get_object_or_404(Album, slug=slug)
    albums = Album.objects.filter(author__username__exact=author_username, slug__exact=slug)
    album = albums.first()
    # delete all photos under album
    photo_set = Photo.objects.filter(album=album)
    for photo in photo_set:
        photo.delete()
    album.delete()
    messages.success(request, "Album Successfully Deleted!")
    return redirect("album:list")


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
    if album.cover_photo_url == photo_url:
        create_cover_photo(album)
    messages.success(request, "Photo Successfully Deleted!")
    return redirect("album:list")


def set_cover_photo(request, author_username, slug, id):
    album_set = Album.objects.filter(author__username__exact=author_username, slug__exact=slug)
    album = album_set.first()
    photo = get_object_or_404(Photo, id=id)
    album.cover_photo_url = photo.image.url
    album.save()
    messages.success(request, "Cover photo Successfully Updated!")
    return redirect(album.get_absolute_url())


# this needs to be moved to util module
def grouped(l, n):
    for i in range(0, len(l), n):
        yield l[i:i + n]


def post_process_photos(album):
    photos = album.photo_set.all()
    if photos:
        for photo in photos:
            if not photo.width or photo.width == 0: # means it has not been processed before
                photo.post_process()


# use the first image of the album when creating
def create_cover_photo(album):
    album.cover_photo_url = ''
    if album.photo_set and album.photo_set.order_by('title').first() is not None:
        cover_photo_url = album.photo_set.order_by('title').first().image.url
        album.cover_photo_url = cover_photo_url
        album.save()
