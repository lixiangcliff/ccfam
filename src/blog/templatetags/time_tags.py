# http://stackoverflow.com/questions/9924750/how-to-compare-datetime-in-django-template
from datetime import timedelta

from django import template
from django.utils import timezone
from django.utils.timesince import timesince

register = template.Library()


@register.filter(name='timesince_threshold')
def timesince_threshold(value, days=7):
    """
    return timesince(<value>) if value is more than <days> old. Return value otherwise
    """
    now = timezone.now()
    if now - value < timedelta(days=days):
        return timesince(value) + ' ago'
    else:
        return value


timesince_threshold.is_safe = False
