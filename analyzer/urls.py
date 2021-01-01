from django.urls import path

from . import views

app_name = 'analyzer'
urlpatterns = [
    path('', views.AnalyticsView.as_view(), name='analytics'),

]
