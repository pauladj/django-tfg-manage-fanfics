from django import template
from django.db.models import Max

from common.models import Fanfic, Character, FanficList, FandomFanfic, \
    Fandom, Chapter, Reading

register = template.Library()


@register.filter('input_type')
def input_type(input):
    return input.field.widget.__class__.__name__


@register.inclusion_tag('utils/pagination.html', takes_context=True)
def paginate(context, position=''):
    """ Get notification list """
    paginator = context['paginator']
    page_obj = context['page_obj']
    is_paginated = context['is_paginated']

    return {'pagination_obj': page_obj,
            'paginator': paginator, 'is_paginated': is_paginated,
            'position': position}


@register.inclusion_tag('utils/stars.html')
def generate_stars(score, size='normal'):
    """ Get the stars to show """
    return {'score': score, 'size': size}


@register.simple_tag
def get_reading_of_user(chapter, user):
    """ Get the stars to show """
    return chapter.get_reading_of_user(user)


@register.simple_tag()
def get_all_different_languages():
    """ Get all different languages """

    languages = Fanfic.objects.exclude(language__isnull=True).values(
        'language').distinct()
    return languages


@register.simple_tag()
def get_characters_of_fandom(fandom_id):
    """ Get the characters of a fandom """
    characters = Character.objects.filter(fandom=fandom_id)
    return characters


@register.simple_tag()
def compare_if_equal(str1, str2):
    """ Compare the two strings """
    if str1 is None or str2 is None:
        return False
    if str(str1) == str(str2):
        return True
    else:
        return False


@register.simple_tag()
def get_fandoms(user_id):
    """ Get fandoms of one user """
    fanfics = list(FanficList.objects.filter(
        list__user__id=user_id).values_list(
        'fanfic__id', flat=True))
    fandoms_id = FandomFanfic.objects.filter(
        fanfic__id__in=fanfics).values_list('fandom__id', flat=True).distinct()

    fandoms = Fandom.objects.filter(id__in=fandoms_id).order_by('name')
    return fandoms


@register.simple_tag()
def get_new_chapters_for_user(user_id):
    """ Get the last four updated fanfics with new chapters for a user """
    chapters = []
    fanfics_ids_of_user = FanficList.objects.filter(
        list__user__id=user_id).values_list('fanfic__id', flat=True)
    for fanfic_id in fanfics_ids_of_user:
        max_date = Chapter.objects.filter(
            fanfic__id=fanfic_id).aggregate(maxdate=Max('date'))['maxdate']
        chapter = Chapter.objects.filter(fanfic__id=fanfic_id, date=max_date)
        if chapter.exists():
            chapters.append(chapter.first())

    chapters.sort(key=lambda t: t.date, reverse=True)
    return chapters[:4]


@register.simple_tag()
def chapters_user_has_read(fanfic_id, user_id):
    """ How many chapters a user has read of a fanfic"""
    return Reading.objects.filter(user__id=user_id,
                                  chapter__fanfic__id=fanfic_id,
                                  read=True).count()


@register.simple_tag()
def get_user_recently_read_chapters(user_id):
    """ Get the last five read chapters for a user """
    return Reading.objects.filter(user=user_id, read=True).order_by(
        '-date')[:5]


@register.simple_tag()
def get_recently_added_fanfics(user_id):
    """ Get last four recently added fanfics """
    return FanficList.objects.filter(list__user__id=user_id).order_by(
        '-date')[:4]
