from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.views.generic import RedirectView

urlpatterns = [
    path('', RedirectView.as_view(url='/dashboard/', permanent=False)),
    path('django-admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    path('inventory/', include('inventory.urls')),
    path('sales/', include('sales.urls')),
    path('dashboard/', include('dashboard.urls')),
    path('ai/', include('ai_engine.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
