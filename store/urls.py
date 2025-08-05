from django.urls import path
from . import views

app_name = 'store'

urlpatterns = [
    # Product listing & detail
    path('', views.products, name='products'),  # All products
]