from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
import stripe
from .models import SubscriptionPlan, UserSubscription


def plans(request):
    plans = SubscriptionPlan.objects.filter(is_active=True)
    return render(request, 'subscriptions/plans.html', {'plans': plans})