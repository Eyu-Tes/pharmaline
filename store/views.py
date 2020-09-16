from datetime import datetime
from os import listdir
from os.path import join

import shortuuid
from django.core import serializers
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import Http404, HttpResponse, HttpResponseServerError, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone

from pharmaline.settings import MEDIA_ROOT, MEDIA_URL
from .forms import OrderForm, QuantityForm
from .models import Medication, Cart, CartItem, Pharmacy, Order, OrderItem, OrderStatus


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
    response = render(request, 'store/index.html',
                      context={'cart_count': cart_count,
                               'order_count': get_order_count(request)})
    return set_user_session_cookie(request, response)


def cart(request):
    shopping_cart = get_cart(request)
    cart_items = shopping_cart.cartitem_set.all()

    if request.method == 'POST':
        med = Medication.objects.get(id=request.POST['med_id'])
        try:
            operation = request.POST['operation']
            cart_item = cart_items.get(drug=med)
            if operation == '+':
                cart_item.quantity += 1
            elif operation == '-':
                cart_item.quantity -= 1
            else:
                return HttpResponseServerError('Invalid operation requested.')
            cart_item.save()
            if cart_item.quantity == 0:
                cart_item.delete()
            return JsonResponse({
                'cart_count': get_cart_count(shopping_cart), 'total': get_cart_totals(shopping_cart),
                'cart_item': serializers.serialize('json', [cart_item])
            })
        except KeyError:  # Then the POST request came from the form on the cart page
            cart_items.filter(drug=med).delete()
        return redirect('store:cart')

    # TODO: calculate proper subtotals and totals (delivery fee, vat, etc...)
    totals = get_cart_totals(shopping_cart)
    response = render(request, 'store/cart.html',
                      context={'cart_count': get_cart_count(shopping_cart), 'cart_items': cart_items,
                               'order_count': get_order_count(request),
                               'subtotal': totals['subtotal'], 'total': totals['total']})
    return set_user_session_cookie(request, response)


def add_med_to_cart(shopping_cart: Cart, med: Medication, quantity):
    med = Medication.objects.get(id=med.id)
    # If the medication is already in the cart increase its quantity by `med_quantity`
    if shopping_cart.cartitem_set.filter(drug=med).first():
        cart_item = shopping_cart.cartitem_set.get(drug=med)
        cart_item.quantity += quantity
        cart_item.total_price += (med.price * cart_item.quantity)
        cart_item.save()
    else:  # The medication added to the cart must be inserted to the cart_item table
        new_item = CartItem(cart=shopping_cart, drug=med, quantity=quantity)
        new_item.total_price = med.price * new_item.quantity
        new_item.save()


def about(request):
    cart_count = get_cart_count(get_cart(request))
    response = render(request, 'store/about.html', context={
        'cart_count': cart_count,
        'order_count': get_order_count(request)
    })
    return set_user_session_cookie(request, response)


def store(request, page_num):
    cart_count = get_cart_count(get_cart(request))
    all_medication = Medication.objects.filter(stock__gte=1)
    pages = Paginator(all_medication, 12)
    page = pages.get_page(page_num)
    response = render(request, 'store/store.html', {
        'meds': page,
        'cart_count': cart_count,
        'order_count': get_order_count(request)
    })
    return set_user_session_cookie(request, response)


def search(request):
    query = request.GET.get('query', '')
    search_result = Medication.objects.filter(
        Q(name__icontains=query) | Q(description__icontains=query) |
        Q(instructions__icontains=query) | Q(vendor__icontains=query) |
        Q(pharmacy__pharmacy_name__icontains=query))
    response = render(request, 'store/search_results.html',
                      context={'search_result': search_result,
                               'cart_count': get_cart_count(get_cart(request)),
                               'order_count': get_order_count(request)})
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


def detail(request, med_id):
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
                return redirect('store:store', page_num=1)
            else:
                form.add_error('quantity', '')

    response = render(request, 'store/med_details.html',
                      context={'form': form,
                               'med': med,
                               'similar_med': similar_med,
                               'cart_count': get_cart_count(shopping_cart),
                               'order_count': get_order_count(request)})
    return set_user_session_cookie(request, response)


def checkout(request):
    if not request.user.is_authenticated:
        return redirect('store:cart')

    shopping_cart = get_cart(request)
    order_form = OrderForm()

    if request.method == 'POST':
        order_form = OrderForm(request.POST, request.FILES)
        if order_form.is_valid():
            # Check if any existing order name matches the submitted order name
            order = Order.objects.filter(order_name=order_form.cleaned_data['order_name'])
            if len(order) == 0:  # The order is unique
                save_order(order_form.cleaned_data, request.FILES.getlist('prescriptions'),
                           shopping_cart, request.user.customer)
                response = redirect('store:thankyou')
                response.delete_cookie('user_session')
                return response

    totals = get_cart_totals(shopping_cart)
    cart_items = shopping_cart.cartitem_set.all()
    return render(request, 'store/checkout.html', {
        'form': order_form, 'cart_count': get_cart_count(shopping_cart),
        'order_count': get_order_count(request), 'cart_items': cart_items,
        'prescription_required': cart_items.filter(drug__requires_prescription=True).exists(),
        'subtotal': totals['subtotal'], 'total': totals['total']})


def save_order(clean_data, files, shopping_cart, customer):
    order = Order(customer=customer, cart=shopping_cart, date_time=datetime.now(tz=timezone.utc))
    order = set_order_details(order, clean_data)
    order.save()

    for cart_item in shopping_cart.cartitem_set.all():
        order_item = order.orderitem_set.create(cart_item=cart_item, pharmacy=cart_item.drug.pharmacy)
        set_order_status(order_item, OrderStatus.PENDING.value)

    for image in files:
        order.save_prescription_image(image)


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
    return render(request, 'store/thankyou.html', context={'order_count': get_order_count(request)})


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
    pharmacy = get_object_or_404(Pharmacy, id=pk)
    if request.user == pharmacy.user:
        pharmacy_products = pharmacy.medication_set.all()
        context = {
            'pharmacy_name': pharmacy,
            'products': pharmacy_products,
            'order_count': get_order_count(request)
        }
    else:
        raise Http404('Page not found')

    return render(request, 'store/products.html', context=context)


def orders(request):
    try:  # try getting a pharmacy user
        pharmacy = request.user.pharmacy
        order_items = OrderItem.objects.filter(pharmacy=pharmacy)
    # TODO: find a better way to identify user kind (also see: `get_order_count(...)`)
    except Exception:  # if this block is hit the user is a customer
        customer = request.user.customer
        order_items = OrderItem.objects.filter(order__customer=customer)
    # 'DISPATCHED' orders can't be cancelled. Hence, the missing filter for dispatched orders
    order_items = order_items.filter(
        Q(status__exact=OrderStatus.PENDING.value) | Q(status__exact=OrderStatus.DISPATCHED.value))
    return render(request, 'store/orders.html',
                  context={'orders': order_items,
                           'order_count': get_order_count(request),
                           'cart_count': get_cart_count(get_cart(request))})


def set_order_status(order_item, new_status):
    order_item.status = new_status
    order_item.save()
    cart_item = order_item.cart_item
    if new_status == OrderStatus.PENDING.value:
        cart_item.drug.stock -= cart_item.quantity
    # If an order is put in the CANCELLED or REJECTED state the stock amount must be restored
    elif (new_status == OrderStatus.REJECTED.value) or (new_status == OrderStatus.CANCELED.value):
        cart_item.drug.stock += cart_item.quantity
    else:  # The other states such as COMPLETED and DISPATCHED don't affect the stock amount
        pass
    cart_item.drug.save()


def order_details(request, pk):
    order_item = OrderItem.objects.get(id=pk)

    if request.method == 'POST':
        new_status = request.POST['new_status']
        if new_status in [status.value for status in list(OrderStatus)]:
            # A customer may try to cancel an order that is already dispatched. That should not be allowed.
            if not (new_status == OrderStatus.CANCELED.value and order_item.status == OrderStatus.DISPATCHED.value):
                set_order_status(order_item, new_status)
                order_item.save()
                return HttpResponse('Order cancelled successfully.')
            else:
                return HttpResponseServerError('This order is already dispatched.')
        else:
            # In case someone tampered with the values ('value' attribute) of
            # the buttons an error will be returned
            return HttpResponseServerError('The requested status change is non-existent.')

    if order_item.status == OrderStatus.CANCELED.value:
        order_states = None
    else:
        order_states = [status.value for status in list(OrderStatus)]
        order_states.remove(OrderStatus.CANCELED.value)
    # Collect the prescription images for the order
    try:
        order_prescriptions = listdir(join(MEDIA_ROOT, order_item.order.order_name))
        image_paths = []
        for image in order_prescriptions:
            image_paths.append(join(MEDIA_URL, order_item.order.order_name, image))
    except IOError:
        image_paths = None
    return render(request, 'store/order_details.html',
                  context={'order_count': get_order_count(request),
                           'order_states': order_states,
                           'order_item': order_item,
                           'image_paths': image_paths})


# TODO: provide a better solution for the bad (generic) except block below
def get_order_count(request):
    try:  # try getting a pharmacy user
        pharmacy = request.user.pharmacy
        return len(OrderItem.objects.filter(
            Q(pharmacy=pharmacy),
            Q(status__exact=OrderStatus.PENDING.value) | Q(status__exact=OrderStatus.DISPATCHED.value)))
    # TODO: find a better way to identify user kind
    except Exception:  # if this block is hit the user is either a customer or anonymous
        try:
            customer = request.user.customer
            return len(OrderItem.objects.filter(
                Q(order__customer=customer),
                Q(status__exact=OrderStatus.PENDING.value) | Q(status__exact=OrderStatus.DISPATCHED.value)))
        except Exception:
            return None
