from django import template
from notifier.models import Notification

register = template.Library()


@register.inclusion_tag('notifier.html')
def add_real_time_notifications():
    """ Adds the necessary script for the socket so the notifications 
        are in real time
    """
    return


@register.inclusion_tag('user-notifications.html', takes_context=True)
def get_user_notifications(context):
    """ Get notification list """
    user = context['user']
    user_notifications = Notification.top_bar_notifications(
        user)
    return {'user_notifications': user_notifications, 'user': user}


@register.simple_tag
def get_user_unread_notification_count(current_user):
    """ Get unread notification count """
    badge_count = Notification.get_unseen_count(current_user)
    return badge_count


@register.inclusion_tag('user-feed.html', takes_context=True)
def feed_text(context):
    """ Get feed text to show """
    notifications = context['user_notifications']
    page_obj = context['page_obj']
    is_paginated = context['is_paginated']
    paginator = context['paginator']
    user = context['user']
    return {'user_notifications': notifications, 'page_obj': page_obj,
            'paginator': paginator, 'is_paginated': is_paginated, 'user': user}
