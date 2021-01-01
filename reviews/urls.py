from django.urls import re_path

from reviews import views

app_name = 'reviews'
urlpatterns = [

    # see edit page, update
    re_path(r'^(?P<review_id>['
            r'0-9]+)/edit/?$',
            views.ReviewView.as_view(), name='review'),

    # see, delete a  review
    re_path(r'^(?P<review_id>[0-9]+)/?$',
            views.ReviewsView.as_view(), name='reviews'),

    # create a review
    re_path(r'^$',
            views.ReviewsView.as_view(), name='reviews'),

]
