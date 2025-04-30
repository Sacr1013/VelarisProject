# velaris/urls.py
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('flights.urls')),  # Incluye las URLs de flights
    path('accounts/', include('accounts.urls')),  # Incluye las URLs de accounts
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)