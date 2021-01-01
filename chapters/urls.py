from django.urls import re_path

from chapters import views

app_name = 'chapters'
urlpatterns = [
    # delete all the private notes for one user
    re_path(r'chapters/notes/?$',
            views.ChaptersNotesView.as_view(), name='chapters_notes'),

    # create/update private note for one user and chapter
    re_path(r'chapters/(?P<chapter_id>['r'0-9]+)/notes/?$',
            views.ChaptersNotesView.as_view(), name='chapters_note'),

    # mark as read last chapter of a fanfic
    re_path(r'chapters/read/?$',
            views.ChaptersMarkAsReadLastView.as_view(), name='chapter_read'),

    # toggle mark as read
    re_path(r'chapters/(?P<chapter_id>['r'0-9]+)/?$',
            views.ChaptersMarkAsReadView.as_view(), name='chapter_mark'),

    # delete all for one user, mark all as read
    re_path(r'chapters/?$',
            views.ChaptersView.as_view(), name='chapters'),

]
