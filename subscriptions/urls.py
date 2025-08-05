from django.urls import path
from . import views

app_name = 'subscriptions'

urlpatterns = [
    path('', views.plans, name='plans'),  # Shows list of plans
]
