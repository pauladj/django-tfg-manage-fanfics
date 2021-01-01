from django.urls import re_path

from fandoms import views

app_name = 'fandoms'
urlpatterns = [
    # get fanfics of one fandom
    re_path(r'^(?P<fandom_id>['r'0-9]+)/fanfics/?$',
            views.FanficsOfFandomView.as_view(), name='fanfics'),

]
