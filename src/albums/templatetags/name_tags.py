# http://stackoverflow.com/questions/9924750/how-to-compare-datetime-in-django-template

# NO GOOD

from django import template

register = template.Library()


@register.filter(name='full_name_or_username')
def full_name_or_username(value):
    """
    return user's full_name if it has, otherwise return its username
    """
    if value.get_full_name():
        return value.get_full_name()
    else:
        return value.get_username()


full_name_or_username.is_safe = False
