from django.urls import path
from . import views

app_name = 'store'

urlpatterns = [
    path('', views.products, name='products'),
    path('<slug:category_slug>/', views.products, name='products_by_category'),
    path('<int:id>/<slug:slug>/', views.product_detail, name='product_detail'),
    path('add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('remove/<int:product_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('cart/', views.cart, name='cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('order/success/', views.order_success, name='order_success'),
    path('order/cancel/', views.order_cancel, name='order_cancel'),
    path('orders/', views.orders, name='orders'),
    path('orders/<int:order_id>/', views.order_detail, name='order_detail'),
    path('webhook/', views.stripe_webhook, name='stripe_webhook'),
]


