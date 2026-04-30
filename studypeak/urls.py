from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls')),
    path('accounts/', include('accounts.urls')),
    path('chat/', include('chat.urls')),
    path('materials/', include('materials.urls')),
    path('assignments/', include('assignments.urls')),
    path('crm/', include('crm.urls')),
    path('dashboard/', include('dashboard.urls')),
    path('shop/', include('shop.urls')),
    path('ai/', include('ai.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)