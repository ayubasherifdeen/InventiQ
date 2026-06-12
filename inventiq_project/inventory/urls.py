from django.urls import path
from . import views

app_name = 'inventory'
urlpatterns = [
    path('', views.product_list, name='product_list'),
    path('create/', views.product_create, name='product_create'),
    path('<int:pk>/', views.product_detail, name='product_detail'),
    path('<int:pk>/edit/', views.product_edit, name='product_edit'),
    path('<int:pk>/delete/', views.product_delete, name='product_delete'),
    path('<int:pk>/stock/', views.stock_adjust, name='stock_adjust'),
    path('categories/', views.category_list, name='category_list'),
]
