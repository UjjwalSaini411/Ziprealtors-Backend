# backend_project/urls.py
from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse
from django.conf import settings
from django.conf.urls.static import static

def health(request):
    return JsonResponse({"status": "ok", "message": "API is running"})

urlpatterns = [
    path('', health),  # root endpoint
    path('admin/', admin.site.urls),
    path('api/', include('listings.urls')),
    path('api/', include('enquiries.urls')),
    path('api/', include('blogs.urls')),
    path('eoi/', include('eoi.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
