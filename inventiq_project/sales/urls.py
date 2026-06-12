from django.urls import path
from . import views

app_name = 'sales'
urlpatterns = [
    path('', views.sale_list, name='sale_list'),
    path('pos/', views.pos_view, name='pos'),
    path('process/', views.process_sale, name='process_sale'),
    path('<int:pk>/', views.sale_detail, name='sale_detail'),
    path('<int:pk>/receipt/', views.sale_receipt, name='sale_receipt'),
]
