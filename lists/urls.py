from django.urls import re_path, path

from lists import views

app_name = 'lists'
urlpatterns = [
    # add fanfic to a list of user
    re_path(r'^(?P<list_id>[0-9]+)/?$',
            views.ListsView.as_view(), name='lists'),

    # Manage user's lists
    path('', views.ListsView.as_view(), name='manage_lists'),

]
