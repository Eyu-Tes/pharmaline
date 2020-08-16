from django.shortcuts import render
from django.shortcuts import get_object_or_404

from .models import Medication, Cart, CartItem
from django.utils.timezone import timezone

from datetime import datetime

import shortuuid


def get_cart_count(request):
    cart = get_cart(request)
    return len(CartItem.objects.filter(cart=cart))


def set_user_session_cookie(request, response):
    response.set_cookie('user_session', get_user_session_cookie(request))
    return response


def get_user_session_cookie(request):
    try:
        user_session = request.COOKIES['user_session']
    except KeyError:
        user_session = shortuuid.random(length=30)

    return user_session


def index(request):
    cart_count = get_cart_count(request)
    response = render(request, 'store/index.html', context={'cart_count': cart_count})
    response = set_user_session_cookie(request, response)
    return response


def cart(request):
    cart = get_cart(request)
    # TODO: add or remove the requested medication from the cart
    cart_items = CartItem.objects.filter(cart=cart)

    if request.method == 'POST':
        new_med = Medication.objects.get(id=request.POST['med_id'])
        # If the medication is already in the cart increase its quantity by 1
        if CartItem.objects.filter(cart=cart, drug=new_med).first():
            cart_item = cart_items.get(drug=new_med)
            cart_item.quantity += 1
            cart_item.total_price += new_med.price  # `new_med` is the same as `cart_item.drug`
            cart_item.save()
        else:  # The medication added to the cart must be inserted to the cart_item table
            new_item = CartItem(drug=new_med, cart=cart, quantity=1)
            new_item.total_price = new_med.price * new_item.quantity
            new_item.save()

    cart_count = len(cart_items)
    total = sum([cart_item.total_price for cart_item in cart_items])
    # TODO: calculate proper subtotals and totals
    response = render(request, 'store/cart.html',
                      context={'cart_count': cart_count, 'cart_items': cart_items, 'subtotal': total, 'total': total})
    response = set_user_session_cookie(request, response)
    return response


def about(request):
    cart_count = get_cart_count(request)
    response = render(request, 'store/about.html', context={'cart_count': cart_count})
    response = set_user_session_cookie(request, response)
    return response


def store(request):
    cart_count = get_cart_count(request)
    try:
        meds = Medication.objects.all()[:12]
    except Medication.DoesNotExist:
        meds = None
    response = render(request, 'store/store.html', {'meds': meds, 'cart_count': cart_count})
    response = set_user_session_cookie(request, response)
    return response


def details(request, med_id):
    cart_count = get_cart_count(request)
    response = render(request, 'store/details.html',
                      context={'med': get_object_or_404(Medication, pk=med_id),
                               'cart_count': cart_count})
    response = set_user_session_cookie(request, response)
    return response


def checkout(request):
    cart_count = get_cart_count(request)
    response = render(request, 'store/checkout.html', {'cart_count': cart_count})
    return response


def thankyou(request):
    response = render(request, 'store/thankyou.html')
    return response


def get_cart(request):
    user_session = get_user_session_cookie(request)
    try:
        # Try to get a cart registered associated with `user_session`
        cart = Cart.objects.get(user_session=user_session)
    except Cart.DoesNotExist:
        # If the attempt to get an existing cart with the given `user_session` doesn't exist
        # then the user must be adding items to the cart for the first time so create a new one
        cart = Cart(date=datetime.now(tz=timezone.utc), user_session=user_session)
        cart.save()

    return cart
