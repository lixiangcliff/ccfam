from django import template

register = template.Library()


@register.filter(name='display_to_preview')
def display_to_preview(value, position):
    """
    transpose photo's postion from display view to preview view
    """
    try:
        value = int(value)
        position = int(position)
        pos = (value - 1) * 9 + position + 1
        return pos
    except:
        pass
    return ''