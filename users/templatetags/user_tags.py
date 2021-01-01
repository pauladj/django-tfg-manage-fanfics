from django import template

register = template.Library()


@register.simple_tag
def user_follows(user1, user2):
    return user1.follows(user2)
