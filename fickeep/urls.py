from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path, re_path
from django.views.static import serve

from common import views

urlpatterns = [
    path('', views.EntryPointView.as_view()),

    path('fickeeper/notifications/', include('notifier.urls',
                                             namespace='notifier')),
    path('fickeeper/analyzer/', include('analyzer.urls',
                                        namespace='analyzer')),
    path('pages/', include('pages.urls', namespace='pages')),

    re_path(r'^fickeeper/media-type/',
            include('media_types.urls', namespace='media_type')),

    re_path(r'^fickeeper/fanfics/(?P<fanfic_id>['r'0-9]+)/',
            include('chapters.urls', namespace='chapters_fanfics')),

    re_path(r'^fickeeper/fandoms/',
            include('fandoms.urls', namespace='fandoms')),

    path('fickeeper/lists/', include('lists.urls', namespace='lists')),

    path('fickeeper/fanfics/', include('fanfics.urls', namespace='fanfics')),

    path('fickeeper/reviews/', include('reviews.urls', namespace='reviews')),

    path('fickeeper/users/', include('users.urls')),

    path('fickeeper/', include('common.urls', namespace='common')),

    path('admin/', admin.site.urls),

    re_path(r'^media/(?P<path>.*)$', serve,
            {'document_root': settings.MEDIA_ROOT}),
    re_path(r'^static/(?P<path>.*)$', serve,
            {'document_root': settings.STATIC_ROOT}),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
