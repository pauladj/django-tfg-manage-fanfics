from django.urls import path
from common.decorators import anonymous_required

from . import views

app_name = 'pages'
urlpatterns = [
    path('home/', anonymous_required()(views.HomePageView.as_view()),
         name='home'),
]
