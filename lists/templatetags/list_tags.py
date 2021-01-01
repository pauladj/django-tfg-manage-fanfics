from django import template

from common.models import FanficList, List

register = template.Library()


@register.simple_tag()
def initialize_list_dropdown(user_id):
    """ Get all the lists of a user """
    return List.objects.filter(user__id=user_id)


@register.inclusion_tag('add-fanfic-button.html', takes_context=True)
def add_fanfic_button(context, fanfic_id):
    """ Modal to add fanfic to list """
    user = context['user']
    user_lists = context['user_lists']
    return {'fanfic_id': fanfic_id, 'user': user, 'user_lists': user_lists}


@register.simple_tag()
def get_list_of_fanfic(fanfic_id, user_id):
    # Get the list of a fanfic
    fl = FanficList.objects.filter(fanfic__id=fanfic_id,
                                   list__user__id=user_id)
    if fl.exists():
        fl = fl.first().list
    else:
        fl = None

    return fl
