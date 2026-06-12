from django.urls import path
from . import views
app_name = 'ai_engine'
urlpatterns = [
    path('', views.ai_dashboard, name='dashboard'),
    path('refresh/', views.refresh_analysis, name='refresh'),
    path('product/<int:pk>/', views.product_analysis, name='product_analysis'),
]
