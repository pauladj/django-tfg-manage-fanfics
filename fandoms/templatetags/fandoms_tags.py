from django import template

from common.models import Type, FandomFanfic

register = template.Library()


@register.simple_tag
def number_of_fanfics_in_fandom(fandom_id):
    """ Get the number of fanfics for one fandom"""
    return FandomFanfic.objects.filter(fandom__id=fandom_id).count()
