from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from django.utils import timezone
from django.contrib.auth import get_user_model

import stripe
from datetime import timedelta

from .models import SubscriptionPlan, UserSubscription

stripe.api_key = settings.STRIPE_SECRET_KEY


def plans(request):
    """
    Display all active subscription plans.
    """
    active_plans = SubscriptionPlan.objects.filter(is_active=True)
    return render(request, 'subscriptions/plans.html', {'plans': active_plans})


@login_required
def subscribe(request, plan_id):
    """
    Handle subscription checkout with Stripe.
    """
    try:
        plan = SubscriptionPlan.objects.get(id=plan_id, is_active=True)
    except SubscriptionPlan.DoesNotExist:
        messages.error(request, 'Selected subscription plan does not exist.')
        return redirect('subscriptions:plans')

    existing_subscription = UserSubscription.objects.filter(
        user=request.user,
        is_active=True
    ).first()

    if existing_subscription:
        messages.warning(request, f"You already have an active subscription: {existing_subscription.plan.name}")
        return redirect('profile')

    try:
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'usd',
                    'product_data': {'name': plan.name},
                    'unit_amount': int(plan.price * 100),
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url=request.build_absolute_uri(f'/subscriptions/success/?plan_id={plan.id}'),
            cancel_url=request.build_absolute_uri('/subscriptions/cancel/'),
            metadata={
                'plan_id': plan.id,
                'user_id': request.user.id,
            },
        )
        return redirect(checkout_session.url)


    except Exception as e:
        messages.error(request, 'An error occurred during checkout. Please try again.')
        return redirect('subscriptions:plans')


@login_required
def subscription_success(request):
    """
    Handle successful subscription payment.
    """
    plan_id = request.GET.get('plan_id')
    if not plan_id:
        return redirect('subscriptions:plans')

    try:
        plan = SubscriptionPlan.objects.get(id=plan_id)
        messages.success(request, f'You have successfully subscribed to {plan.name}!')
    except SubscriptionPlan.DoesNotExist:
        messages.warning(request, 'Subscription plan not found.')

    return redirect('profile')


@login_required
def subscription_cancel(request):
    """
    Handle canceled subscription attempt.
    """
    messages.info(request, 'Your subscription process was canceled.')
    return redirect('subscriptions:plans')


@csrf_exempt
def stripe_webhook(request):
    """
    Handle Stripe webhook for completed checkout sessions.
    """
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except (ValueError, stripe.error.SignatureVerificationError):
        return HttpResponse(status=400)

    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        fulfill_subscription(
            session.metadata['plan_id'],
            session.metadata['user_id'],
            session.payment_intent
        )

    return HttpResponse(status=200)


def fulfill_subscription(plan_id, user_id, payment_intent):
    """
    Create a new user subscription after successful Stripe payment.
    """
    User = get_user_model()

    try:
        plan = SubscriptionPlan.objects.get(id=plan_id)
        user = User.objects.get(id=user_id)
    except (SubscriptionPlan.DoesNotExist, User.DoesNotExist):
        return

    start_date = timezone.now()
    end_date = start_date + timedelta(days=plan.duration_days)

    UserSubscription.objects.create(
        user=user,
        plan=plan,
        start_date=start_date,
        end_date=end_date,
        is_active=True,
        stripe_subscription_id=payment_intent
    )
