from django.shortcuts import render
from django.shortcuts import get_object_or_404

from .models import Medication, Cart, CartItem, Pharmacy
from django.utils.timezone import timezone


from datetime import datetime
import re

import shortuuid


def get_cart_count(cart):
    cart_items = CartItem.objects.filter(cart=cart)
    cart_count = sum([cart_item.quantity for cart_item in cart_items])
    return cart_count


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
    cart_count = get_cart_count(get_cart(request))
    response = render(request, 'store/index.html', context={'cart_count': cart_count})
    return set_user_session_cookie(request, response)


def cart(request):
    cart = get_cart(request)
    # TODO: add or remove the requested medication from the cart
    cart_items = CartItem.objects.filter(cart=cart)

    if request.method == 'POST':
        if 'remove_med' in request.POST:
            med = Medication.objects.get(id=request.POST['remove_med'])
            cart_items.filter(drug=med).delete()
        else:
            add_med_to_cart(request, cart_items)
            # Adding a new medication doesn't necessarily mean you want to checkout.
            # Therefore, the response will take the user to the 'store' page
            return store(request)

    # TODO: calculate proper subtotals and totals (dlivery fee, vat, etc...)
    cart_count = get_cart_count(cart)
    total = sum([cart_item.total_price for cart_item in cart_items])
    response = render(request, 'store/cart.html',
                      context={'cart_count': cart_count, 'cart_items': cart_items, 'subtotal': total, 'total': total})
    return set_user_session_cookie(request, response)


def add_med_to_cart(request, cart_items):
    med = Medication.objects.get(id=request.POST['med_id'])
    med_quantity = re.sub('[^\\d]', '', request.POST['quantity'])
    if re.match('^0+$', med_quantity) or (med_quantity == ''):
        med_quantity = 1
    med_quantity = int(med_quantity)
    # If the medication is already in the cart increase its quantity by `med_quantity`
    if cart_items.filter(drug=med).first():
        cart_item = cart_items.get(drug=med)
        cart_item.quantity += med_quantity
        cart_item.total_price += (
                med.price * cart_item.quantity)
        cart_item.save()
    else:  # The medication added to the cart must be inserted to the cart_item table
        new_item = CartItem(cart=get_cart(request), drug=med, quantity=med_quantity)
        new_item.total_price = med.price * new_item.quantity
        new_item.save()


def about(request):
    cart_count = get_cart_count(get_cart(request))
    response = render(request, 'store/about.html', context={'cart_count': cart_count})
    return set_user_session_cookie(request, response)


def store(request):
    cart_count = get_cart_count(get_cart(request))
    try:
        meds = Medication.objects.all()[:12]
    except Medication.DoesNotExist:
        meds = None
    response = render(request, 'store/store.html', {'meds': meds, 'cart_count': cart_count})
    return set_user_session_cookie(request, response)


def details(request, med_id):
    cart_count = get_cart_count(get_cart(request))
    response = render(request, 'store/details.html',
                      context={'med': get_object_or_404(Medication, pk=med_id),
                               'cart_count': cart_count})
    return set_user_session_cookie(request, response)


def checkout(request):
    cart_count = get_cart_count(get_cart(request))
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


def products(request, pk):
    pharmacy = Pharmacy.objects.get(id=pk)
    pharmacy_products = pharmacy.medication_set.all()

    context = {
        'products': pharmacy_products,
    }
    return render(request, 'store/products.html', context=context)
