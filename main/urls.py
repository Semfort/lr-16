from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()

router.register(r'categories', views.CategoryViewSet, basename='category')
router.register(r'manufacturers', views.ManufacturerViewSet, basename='manufacturer')
router.register(r'products', views.ProductViewSet, basename='product')
router.register(r'carts', views.CartViewSet, basename='cart-api')
router.register(r'cart-items', views.CartItemViewSet, basename='cartitem-api')


urlpatterns = [
    path('', views.index, name='index'),
    path('catalog/', views.product_list, name='product_list'),
    path('catalog/<int:pk>/', views.product_detail, name='product_detail'),
    path('author/', views.author, name='author'),
    path('cart/', views.cart, name='cart_view'),
    path('cart/add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/update/<int:item_id>/', views.update_cart, name='update_cart'),
    path('cart/remove/<int:pk>/', views.remove_from_cart, name='remove_from_cart'),
    path('register/', views.register, name='register'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('checkout/', views.checkout_view, name='checkout'),
    path('api/v1/', include(router.urls)), 
    path('api/products/', views.api_products, name='api_products'),
    path('api/cart/add/', views.api_add_to_cart, name='api_add_to_cart'),
]