from django.urls import path
from . import views


app_name = 'notifier'
urlpatterns = [
    path('', views.NotificationsView.as_view(), name='notifications'),
]