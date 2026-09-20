from django import template

register = template.Library()

@register.filter
def food_image(name, category=None):
    """
    Image filter removed per design requirement: zero food photos.
    """
    return ''
