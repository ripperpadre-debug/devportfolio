from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from core import views as core_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls')),
]

handler404 = core_views.page_not_found
handler500 = core_views.server_error
handler403 = core_views.permission_denied
handler400 = core_views.bad_request

media_root = getattr(settings, 'MEDIA_ROOT', None)
if media_root:
    urlpatterns += static(settings.MEDIA_URL, document_root=media_root)
