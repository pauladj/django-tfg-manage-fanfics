from django.urls import path
from django.urls import re_path

from . import views

app_name = 'common'
urlpatterns = [
    re_path(r'^search/?$', views.SearchView.as_view(), name='search'),

    path('', views.DashboardView.as_view(), name='home'),
    re_path(r'^dashboard/?$', views.DashboardView.as_view(), name='dashboard'),

]
