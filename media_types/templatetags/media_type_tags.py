from django import template

from common.models import Type

register = template.Library()


@register.simple_tag
def get_all_media_types():
    """ Get the media types for the menu"""
    return Type.objects.all()
