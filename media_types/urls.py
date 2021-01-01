from django.urls import re_path

from media_types import views

app_name = 'fandoms'
urlpatterns = [
    # get fandoms of one media type
    re_path(r'^(?P<media_type>[\w\-]+)/fandoms/?$',
            views.FandomsView.as_view(), name='fandoms'),

]
