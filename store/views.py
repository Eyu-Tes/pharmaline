from django.shortcuts import render, redirect

from .models import Medication, Cart, CartItem, Pharmacy, Order, OrderItem
from .forms import OrderForm, QuantityForm

from django.utils import timezone

from datetime import datetime

import shortuuid


def get_cart_count(shopping_cart):
    cart_items = CartItem.objects.filter(cart=shopping_cart)
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


def get_cart_totals(shopping_cart: Cart):
    cart_items = CartItem.objects.filter(cart=shopping_cart)
    sub_total = sum([cart_item.total_price for cart_item in cart_items])
    total = sub_total
    return {'subtotal': sub_total, 'total': total}


def index(request):
    cart_count = get_cart_count(get_cart(request))
    response = render(request, 'store/index.html', context={'cart_count': cart_count})
    return set_user_session_cookie(request, response)


def cart(request):
    shopping_cart = get_cart(request)
    cart_items = CartItem.objects.filter(cart=shopping_cart)

    if request.method == 'POST':
        med = Medication.objects.get(id=request.POST['med_id'])
        cart_items.filter(drug=med).delete()
        return redirect('store:cart')

    # TODO: calculate proper subtotals and totals (delivery fee, vat, etc...)
    totals = get_cart_totals(shopping_cart)
    response = render(request, 'store/cart.html',
                      context={'cart_count': get_cart_count(shopping_cart), 'cart_items': cart_items,
                               'subtotal': totals['subtotal'], 'total': totals['total']})
    return set_user_session_cookie(request, response)


def add_med_to_cart(shopping_cart: Cart, med: Medication, quantity):
    med = Medication.objects.get(id=med.id)
    # If the medication is already in the cart increase its quantity by `med_quantity`
    if shopping_cart.cartitem_set.filter(drug=med).first():
        cart_item = shopping_cart.cartitem_set.get(drug=med)
        cart_item.quantity += quantity
        cart_item.total_price += (
                med.price * cart_item.quantity)
        cart_item.save()
    else:  # The medication added to the cart must be inserted to the cart_item table
        new_item = CartItem(cart=shopping_cart, drug=med, quantity=quantity)
        new_item.total_price = med.price * new_item.quantity
        new_item.save()


def about(request):
    cart_count = get_cart_count(get_cart(request))
    response = render(request, 'store/about.html', context={'cart_count': cart_count})
    return set_user_session_cookie(request, response)


def store(request):
    cart_count = get_cart_count(get_cart(request))
    try:
        # todo: pagination
        meds = Medication.objects.all()[:12]
    except Medication.DoesNotExist:
        meds = None
    response = render(request, 'store/store.html', {'meds': meds, 'cart_count': cart_count})
    return set_user_session_cookie(request, response)


def get_similar_medication(med: Medication):
    similar_meds = []
    # In the case where a pharmacy has mistakenly registered the same medication more than
    # once, the medication will cause the pharmacy to appear as a separate location on the
    # 'Other Locations' table. To avoid that, those drugs that have the same pharmacy as their
    # origin will be removed from the `similar_med` list.
    for similar_med in Medication.objects.filter(name__icontains=med.name):
        if similar_med.pharmacy.id != med.pharmacy.id:
            similar_meds.append(similar_med)
    return similar_meds


def details(request, med_id):
    form = QuantityForm()
    shopping_cart = get_cart(request)
    med = Medication.objects.get(id=med_id)
    similar_med = get_similar_medication(med)

    if request.method == 'POST':
        form = QuantityForm(request.POST)

        if form.is_valid():
            quantity = form.cleaned_data['quantity']

            if quantity <= med.stock:
                add_med_to_cart(shopping_cart, med, quantity)
                # Adding a new medication doesn't necessarily mean you want to checkout.
                # Therefore, the response will take the user to the 'store' page
                return redirect('store:store')
            else:
                form.add_error('quantity', '')

    response = render(request, 'store/details.html',
                      context={'form': form,
                               'med': med,
                               'similar_med': similar_med,
                               'cart_count': get_cart_count(shopping_cart)})
    return set_user_session_cookie(request, response)


def checkout(request):
    shopping_cart = get_cart(request)
    order_form = OrderForm()

    if request.method == 'POST':
        order_form = OrderForm(request.POST)
        if request.user.is_authenticated:
            if order_form.is_valid():
                # Check if any existing order name matches the submitted order name
                ord_nam = Order.objects.filter(order_name=order_form.cleaned_data['order_name'])
                if len(ord_nam) == 0:  # The order is unique
                    return save_order_redirect_to_thankyou(order_form.cleaned_data, shopping_cart)

    totals = get_cart_totals(shopping_cart)
    return render(request, 'store/checkout.html', {
        'form': order_form,
        'cart_count': get_cart_count(shopping_cart),
        'cart_items': CartItem.objects.filter(cart=shopping_cart),
        'subtotal': totals['subtotal'],
        'total': totals['total']
    })


def save_order_redirect_to_thankyou(clean_data, shopping_cart: Cart):
    order = Order(cart=shopping_cart, date_time=datetime.now(tz=timezone.utc))
    order = set_order_details(order, clean_data)
    order.save()

    for cart_item in shopping_cart.cartitem_set.all():
        order.orderitem_set.create(cart_item=cart_item, pharmacy=cart_item.drug.pharmacy)

    response = redirect('store:thankyou')
    response.delete_cookie('user_session')
    return response


def set_order_details(order: Order, clean_data):
    order.first_name = clean_data['first_name']
    order.last_name = clean_data['last_name']
    order.order_name = clean_data['order_name']
    order.address = clean_data['location_description_1']
    order.address_opt = clean_data['location_description_2']
    order.region = clean_data['region']
    order.woreda = clean_data['woreda']
    order.email = clean_data['email']
    order.phone = clean_data['phone']
    order.note = clean_data['order_note']
    return order


def thankyou(request):
    return render(request, 'store/thankyou.html')


def get_cart(request):
    user_session = get_user_session_cookie(request)
    try:
        # Try to get a cart registered associated with `user_session`
        shopping_cart = Cart.objects.get(user_session=user_session)
        if len(shopping_cart.cartitem_set.all()) == 0:
            # Even after getting an existing cart, there is a chance it might be empty. That creates
            # a problem when the user exits the browser without adding any items to it leaving an empty
            # cart in the database (coupled with the fact that the session associated with the cart is
            # deleted when the browser exits). In order to clear orphaned carts, check if the cart is empty.
            # If it is, delete the existing cart and create a new one. If its not, return it. This is a
            # terrible solution to the problem! We will get back to it ASAP.
            shopping_cart.delete()
            raise IndexError
    except (Cart.DoesNotExist, IndexError):
        # If the attempt to get an existing cart with the given `user_session` failed, then
        # the user must be adding items to the cart for the first time so create a new one.
        shopping_cart = Cart(date=datetime.now(tz=timezone.utc), user_session=user_session)
        shopping_cart.save()
    return shopping_cart


def products(request, pk):
    pharmacy = Pharmacy.objects.get(id=pk)
    pharmacy_products = pharmacy.medication_set.all()

    context = {
        'products': pharmacy_products,
    }
    return render(request, 'store/products.html', context=context)


def orders(request, pk):
    order_items = OrderItem.objects.filter(pharmacy_id=pk)

    return render(request, 'store/orders.html',
                  context={'orders': order_items,
                           'order_count': len(order_items)})
