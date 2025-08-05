from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse

import stripe
import json
from decimal import Decimal

from .models import Product, ProductCategory, Order, OrderItem
from .forms import AddToCartForm
from .cart import Cart

stripe.api_key = settings.STRIPE_SECRET_KEY


def products(request, category_slug=None):
    """
    Display list of active products, optionally filtered by category.
    """
    category = None
    categories = ProductCategory.objects.all()
    product_list = Product.objects.filter(is_active=True)

    if category_slug:
        category = get_object_or_404(ProductCategory, slug=category_slug)
        product_list = product_list.filter(category=category)

    return render(request, 'store/products.html', {
        'category': category,
        'categories': categories,
        'products': product_list
    })


def product_detail(request, id, slug):
    """
    Display product detail page, including reviews and cart form.
    """
    product = get_object_or_404(Product, id=id, slug=slug, is_active=True)
    reviews = product.productreview_set.all()

    can_review = False
    if request.user.is_authenticated:
        can_review = OrderItem.objects.filter(
            order__user=request.user,
            order__is_paid=True,
            product=product
        ).exists()

    return render(request, 'store/product_detail.html', {
        'product': product,
        'reviews': reviews,
        'can_review': can_review,
        'form': AddToCartForm()
    })


@login_required
def add_to_cart(request, product_id):
    """
    Add a product to the user's cart.
    """
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    form = AddToCartForm(request.POST)

    if form.is_valid():
        quantity = form.cleaned_data['quantity']
        cart.add(product, quantity)
        messages.success(request, f'Added {product.name} to your cart.')

    return redirect('store:product_detail', id=product.id, slug=product.slug)


@login_required
def cart_view(request):
    """
    Display the user's cart.
    """
    cart = Cart(request)
    return render(request, 'store/cart.html', {'cart': cart})


@login_required
def remove_from_cart(request, product_id):
    """
    Remove a product from the cart.
    """
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    cart.remove(product)
    messages.info(request, f'Removed {product.name} from your cart.')
    return redirect('store:cart')


@login_required
def checkout(request):
    """
    Create Stripe checkout session and redirect to Stripe.
    """
    cart = Cart(request)

    if not cart:
        messages.warning(request, 'Your cart is empty.')
        return redirect('store:products')

    if request.method == 'POST':
        try:
            line_items = [{
                'price_data': {
                    'currency': 'usd',
                    'product_data': {'name': item['product'].name},
                    'unit_amount': int(item['price'] * 100),
                },
                'quantity': item['quantity'],
            } for item in cart]

            checkout_session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=line_items,
                mode='payment',
                success_url=request.build_absolute_uri('/store/order/success/'),
                cancel_url=request.build_absolute_uri('/store/order/cancel/'),
                metadata={
                    'user_id': request.user.id,
                    'cart': json.dumps(cart.cart)
                }
            )
            return redirect(checkout_session.url)

        except Exception:
            messages.error(request, 'There was an error processing your payment.')
            return redirect('store:cart')

    return render(request, 'store/checkout.html', {'cart': cart})


@login_required
def order_success(request):
    """
    Handle successful checkout.
    """
    Cart(request).clear()
    messages.success(request, 'Your order was successful!')
    return redirect('store:orders')


@login_required
def order_cancel(request):
    """
    Handle canceled checkout.
    """
    messages.info(request, 'Your order was canceled.')
    return redirect('store:cart')


@login_required
def orders(request):
    """
    Show all orders made by the current user.
    """
    user_orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'store/orders.html', {'orders': user_orders})


@login_required
def order_detail(request, order_id):
    """
    Show details of a specific order.
    """
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'store/order_detail.html', {'order': order})


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
        fulfill_order(
            session.metadata['user_id'],
            session.metadata['cart'],
            session.payment_intent
        )

    return HttpResponse(status=200)


def fulfill_order(user_id, cart_data, payment_intent):
    """
    Create an order and order items after successful Stripe checkout.
    """
    from django.contrib.auth import get_user_model
    User = get_user_model()

    try:
        user = User.objects.get(id=user_id)
        cart = json.loads(cart_data)

        total = sum(
            Decimal(item['price']) * item['quantity']
            for item in cart.values()
        )

        order = Order.objects.create(
            user=user,
            total=total,
            is_paid=True,
            stripe_payment_intent_id=payment_intent
        )

        for product_id, item in cart.items():
            product = Product.objects.get(id=product_id)
            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=item['quantity'],
                price=item['price']
            )
    except (User.DoesNotExist, Product.DoesNotExist, KeyError, json.JSONDecodeError):
        pass  # Optionally log error or handle as needed

