from django.utils.text import slugify
from .time import slugify_time


def create_slug(instance):
    slug = slugify(instance.title)
    qs = instance.__class__.objects.filter(slug=slug)
    exists = qs.exists()
    # if it is a duplicated title, add timestamp at the end of slug
    if exists:
        slug = '%s-%s' % (slug, slugify_time())
    return slug

# def create_slug(instance, new_slug=None):
#     slug = slugify(instance.title)
#     if new_slug is not None:
#         slug = new_slug
#     qs = Album.objects.filter(slug=slug).order_by('-id')
#     exists = qs.exists()
#     if exists:
#         new_slug = '%s-%s' % (slug, qs.first().id)
#         return create_slug(instance, new_slug=new_slug)
#     return slug