"""
URL configuration for dudu_tracker project.
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path, re_path
from django.views.static import serve

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include(('web.urls', 'web'), namespace='web')),
    path('authenticate/', include(('authentication.urls', 'authentication'), namespace='authentication')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
else:
    static_prefix = settings.STATIC_URL.lstrip('/')
    media_prefix = settings.MEDIA_URL.lstrip('/')

    urlpatterns += [
        re_path(
            rf'^{static_prefix}(?P<path>.*)$',
            serve,
            {'document_root': settings.STATIC_ROOT, 'show_indexes': False},
        ),
        re_path(
            rf'^{media_prefix}(?P<path>.*)$',
            serve,
            {'document_root': settings.MEDIA_ROOT, 'show_indexes': False},
        ),
    ]