from django.urls import path
from django.urls import re_path

from . import views

app_name = 'fanfics'
urlpatterns = [
    # Add external fanfic
    path('external/', views.AddExternalFanfic.as_view(),
         name='external_add'),
    path('external/done/', views.AddExternalFanficDone.as_view(),
         name='external_done'),

    # get possible characters for a fanfic
    re_path(r'^(?P<fanfic_id>[0-9]+)/characters/?$',
            views.FanficCharactersView.as_view(), name='fanfic_characters'),

    # Submit fanfic error
    re_path(r'^(?P<fanfic_id>[0-9]+)/errors?$',
            views.FanficErrorsView.as_view(), name='fanfic_errors'),

    # Existing Fanfic
    re_path(r'^(?P<fanfic_id>[0-9]+)/?$',
            views.FanficView.as_view(), name='fanfic'),

]
