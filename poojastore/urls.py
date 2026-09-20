from django.contrib import admin
from django.urls import path, include
from django.conf import settings # Naya add kiya
from django.conf.urls.static import static # Naya add kiya

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('store.urls')),
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)