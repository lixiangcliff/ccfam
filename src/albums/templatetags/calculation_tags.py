# http://stackoverflow.com/questions/5848967/django-how-to-do-caculation-inside-the-template-html-page

from django import template

register = template.Library()


@register.filter(name='subtract')
def subtract(value, arg):
    """
    Subtracts the value; argument is the subtractor.
    Returns empty string on any error.
    """
    try:
        value = int(value)
        arg = int(arg)
        if arg:
            return value - arg
    except:
        pass
    return ''


@register.filter(name='multiply')
def multiply(value, arg):
    """
    Multiplies the value; argument is the multiplier.
    Returns empty string on any error.
    """
    try:
        value = int(value)
        arg = int(arg)
        if arg:
            return value * arg
    except:
        pass
    return ''


@register.filter(name='divide')
def divide(value, arg):
    """
    Divides the value; argument is the divisor.
    Returns empty string on any error.
    """
    try:
        value = int(value)
        arg = int(arg)
        if arg:
            return value / arg
    except:
        pass
    return ''


@register.filter(name='ceil_divide')
def ceil_divide(value, arg):
    """
        Divides the value by ceiling; argument is the divisor.
        Returns empty string on any error.
        """
    try:
        value = int(value)
        arg = int(arg)
        if arg:
            return -(-value // arg)
    except:
        pass
    return ''