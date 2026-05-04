from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='home'),

    path('products/<int:category_id>/', views.product, name='products'),
    path('products/', views.product, name='product_all'),
    path('product/<int:product_id>/', views.product_detail, name='product_detail'),

    path('filter-products/', views.filter_products, name='filter_products'),
    path('api/subcategories/', views.api_subcategories, name='api_subcategories'),
]