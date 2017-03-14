from django.contrib import messages
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db.models import Q
from django.http import Http404, HttpResponsePermanentRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.text import slugify

from .forms import AlbumForm
from .models import Album, create_slug


def album_create(request):
    if not (request.user.is_staff or request.user.is_superuser):
        raise Http404
    form = AlbumForm(request.POST or None, request.FILES or None)
    if form.is_valid():
        instance = form.save(commit=True)
        #instance.editor = request.user
        instance.save()
        messages.success(request, "Album Successfully Created!")
        return HttpResponsePermanentRedirect(instance.get_absolute_url())
    elif form.errors:
        messages.error(request, "Album NOT Successfully Created!")
    context = {
        "form": form
    }
    return render(request, "album_form.html", context)


def album_detail(request, slug):
    instance = get_object_or_404(Album, slug=slug)
    if instance.draft:
        if not (request.user.is_staff or request.user.is_superuser):
            raise Http404
    context = {
        "title": instance.title,
        "instance": instance
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
    paginator = Paginator(queryset_list, 9)  # Show 25 contacts per page
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


def album_update(request, slug=None):
    if not (request.user.is_staff or request.user.is_superuser):
        raise Http404
    instance = get_object_or_404(Album, slug=slug)
    if instance:
        title = instance.title
    form = AlbumForm(request.POST or None, request.FILES or None, instance=instance)
    if form.is_valid():
        instance = form.save(commit=False)
        # change slug if title updated
        if instance.title != title:
            instance.slug = create_slug(instance)
        instance.save()
        messages.success(request, "Album Successfully Updated!")
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


def album_delete(request, slug=None):
    if not request.user.is_staff or not request.user.is_superuser:
        raise Http404
    instance = get_object_or_404(Album, slug=slug)
    instance.delete()
    messages.success(request, "Album Successfully Deleted!")
    return redirect("album:list")


def grouped(l, n):
    for i in range(0, len(l), n):
        yield l[i:i + n]
