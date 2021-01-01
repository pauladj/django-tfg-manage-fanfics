from django.conf.urls import url
from django.contrib.auth import views as dj_views
from django.contrib.auth.decorators import login_required
from django.urls import path
from django.urls import re_path

from common.decorators import anonymous_required
from . import views

urlpatterns = [
    path('signup/', anonymous_required()(views.SignUp.as_view()),
         name='signup'),
    path('signup/done', anonymous_required()(views.SignUpDone.as_view()),
         name='signup_done'),

    # ajax
    url(r'signup/check$', views.check_username, name='check_username'),
    url(r'follow$', views.follow_user, name='toggle_follow_user'),

    path('login/', anonymous_required()(
        dj_views.LoginView.as_view()), name='login'),
    path('logout/',
         login_required(redirect_field_name=None, login_url='login')(
             dj_views.LogoutView.as_view()), name='logout'),

    path('password_change/', dj_views.PasswordChangeView.as_view(),
         name='password_change'),
    path('password_change/done/', dj_views.PasswordChangeDoneView.as_view(),
         name='password_change_done'),

    path('password_reset/', anonymous_required()(
        dj_views.PasswordResetView.as_view()),
         name='password_reset'),
    path('password_reset/done/', anonymous_required()(
        dj_views.PasswordResetDoneView.as_view()),
         name='password_reset_done'),
    path('reset/<uidb64>/<token>/',
         anonymous_required()(dj_views.PasswordResetConfirmView.as_view()),
         name='password_reset_confirm'),
    path('reset/done/', anonymous_required()(
        dj_views.PasswordResetCompleteView.as_view()),
         name='password_reset_complete'),

    re_path(r'^(?P<user_id>[0-9]+)/?$',
        views.Profile.as_view(), name='profile'),
    re_path(r'^(?P<user_id>[0-9]+)/backup/?$',
        views.GetBackupUserData.as_view(), name='user_backup'),
    re_path(r'^(?P<user_id>[0-9]+)/edit/profile/?$',
        views.EditProfileUser.as_view(), name='edit_profile_user'),
    re_path(r'^(?P<user_id>[0-9]+)/edit/general/?$',
        views.EditGeneralSettingsUser.as_view(), name='edit_general_user'),

    # See fanfics of a user
    re_path(r'^(?P<user_id>[0-9]+)/fanfics/?$', views.FanficsOfUser.as_view(),
            name='user_fanfics'),

]
