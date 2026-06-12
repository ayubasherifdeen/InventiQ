from django.urls import path
from . import views

app_name = 'dashboard'
urlpatterns = [
    path('', views.index, name='index'),
    path('export/sales/', views.export_csv, name='export_sales'),
    path('export/inventory/', views.export_inventory_csv, name='export_inventory'),
]
