from datetime import datetime
from os import listdir
from os.path import join
import shortuuid

from django.contrib import messages
from django.core import serializers
from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import Paginator
from django.db.models import Q
from django.db import transaction
from django.http import Http404, HttpResponse, HttpResponseServerError, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.utils import timezone

from pharmaline.settings import MEDIA_ROOT, MEDIA_URL

from .forms import OrderForm, QuantityForm, ProductForm
from .models import Medication, Cart, CartItem, Order, OrderItem, OrderStatus

from account.models import Customer, Pharmacy, PharmaAdmin


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


@transaction.atomic
def cart(request):
    shopping_cart = get_cart(request)
    cart_items = shopping_cart.cartitem_set.all()

    if request.method == 'POST':
        med = Medication.objects.get(id=request.POST['med_id'])
        cart_item = cart_items.get(drug=med)
        try:
            alter_error = alter_cart_item_quantity(request.POST['operation'], cart_item)
            if alter_error:
                return alter_error
            return JsonResponse({
                'cart_count': get_cart_count(shopping_cart), 'total': get_cart_totals(shopping_cart),
                'cart_item': serializers.serialize('json', [cart_item])
            })
        except KeyError:  # (thrown from `request.POST['operation']`) then the POST request is a 'remove med' request
            med.stock = cart_item.quantity
            med.save()
            cart_items.filter(drug=med).delete()
        return redirect('store:cart')

    # TODO: calculate proper subtotals and totals (delivery fee, vat, etc...)
    totals = get_cart_totals(shopping_cart)
    response = render(request, 'store/cart.html',
                      context={'cart_count': get_cart_count(shopping_cart), 'cart_items': cart_items,
                               'order_count': get_order_count(request),
                               'subtotal': totals['subtotal'], 'total': totals['total']})
    return set_user_session_cookie(request, response)


@transaction.atomic
def alter_cart_item_quantity(operation, cart_item):
    if operation == '+':
        if cart_item.drug.stock == 0:
            return HttpResponseServerError(f'There pharmacy only has {cart_item.quantity}.')
        cart_item.quantity += 1
        cart_item.drug.stock -= 1
    elif operation == '-':
        cart_item.quantity -= 1
        cart_item.drug.stock += 1
    else:
        return HttpResponseServerError('Invalid operation requested.')
    cart_item.save()
    cart_item.drug.save()
    if cart_item.quantity == 0:
        cart_item.delete()
    return None


@transaction.atomic
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
    med.stock -= quantity
    med.save()


def about(request):
    cart_count = get_cart_count(get_cart(request))
    response = render(request, 'store/about.html', context={
        'cart_count': cart_count,
        'order_count': get_order_count(request)
    })
    return set_user_session_cookie(request, response)


def store(request, page_num):
    cart_count = get_cart_count(get_cart(request))
    all_medication = Medication.objects.filter(pharmacy__disabled=False, active=True)
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
    if len(query) < 3:
        search_result = []
    else:
        search_result = Medication.objects.filter(
            Q(name__icontains=query) | Q(vendor__icontains=query), pharmacy__disabled=False, active=True)
    response = render(request, 'store/search_results.html',
                      context={'search_result': search_result,
                               'query': query,
                               'cart_count': get_cart_count(get_cart(request)),
                               'order_count': get_order_count(request)})
    return set_user_session_cookie(request, response)


def get_similar_medication(med: Medication):
    similar_meds = []
    # In the case where a pharmacy has mistakenly registered the same medication more than
    # once, the medication will cause the pharmacy to appear as a separate location on the
    # 'Other Locations' table. To avoid that, those drugs that have the same pharmacy as their
    # origin will be removed from the `similar_med` list.
    for similar_med in Medication.objects.filter(active=True, name__iexact=med.name, pharmacy__disabled=False):
        if similar_med.pharmacy.id != med.pharmacy.id:
            similar_meds.append(similar_med)
    return similar_meds


def detail(request, med_id):
    quantity_form = QuantityForm()
    med = Medication.objects.get(id=med_id)
    shopping_cart = get_cart(request)
    similar_med = get_similar_medication(med)

    if not med.active:
        raise Http404('Page not found')

    if request.method == 'POST':
        quantity_form = QuantityForm(request.POST)
        quantity_form.med_stock_count = med.stock

        if quantity_form.is_valid():
            add_med_to_cart(shopping_cart, med, quantity_form.cleaned_data['quantity'])
            # Adding a new medication doesn't necessarily mean you want to checkout.
            # Therefore, the response will take the user to the 'store' page
            return redirect('store:store', page_num=1)

    response = render(request, 'store/med_details.html',
                      context={'form': quantity_form,
                               'med': med,
                               'similar_med': similar_med,
                               'cart_count': get_cart_count(shopping_cart),
                               'order_count': get_order_count(request)})
    return set_user_session_cookie(request, response)


def checkout(request):
    if not request.user.is_authenticated:
        return redirect('store:cart')

    shopping_cart = get_cart(request)
    cart_items = shopping_cart.cartitem_set.all()
    prescription_required = cart_items.filter(drug__requires_prescription=True).exists()
    # pre-populate the form
    customer = request.user.customer
    order_form = OrderForm(initial={
        'first_name': customer.first_name, 'last_name': customer.last_name,
        'email': customer.user.email, 'phone': customer.phone
    })

    if request.method == 'POST':
        order_form = OrderForm(request.POST, request.FILES)
        order_form.order_requires_prescription = prescription_required
        if order_form.is_valid():
            save_order(order_form.cleaned_data, request.FILES.getlist('prescriptions'),
                       shopping_cart, request.user.customer)
            response = redirect('store:thankyou')
            response.delete_cookie('user_session')
            return response

    totals = get_cart_totals(shopping_cart)
    return render(request, 'store/checkout.html', {
        'form': order_form, 'cart_count': get_cart_count(shopping_cart),
        'order_count': get_order_count(request), 'cart_items': cart_items,
        'prescription_required': prescription_required,
        'subtotal': totals['subtotal'], 'total': totals['total']})


@transaction.atomic
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
    order.address = clean_data['location_description_1']
    order.address_opt = clean_data['location_description_2']
    order.region = clean_data['region']
    order.woreda = clean_data['woreda']
    order.email = clean_data['email']
    order.phone = clean_data['phone']
    order.note = clean_data['order_note']
    return order


def thankyou(request):
    return render(request, 'store/thankyou.html', context={
        'order_count': get_order_count(request),
        'cart_count': get_cart_count(get_cart(request))
    })


@transaction.atomic
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


def products(request):
    context = {}
    if not request.GET:
        # make sure that only admins can view all products
        try:
            if request.user.pharmaadmin:
                products = Medication.objects.all()
                context['products'] = products
                return render(request, 'store/products.html', context=context)
        except (AttributeError, ObjectDoesNotExist):
            # AttributeError - is thrown for anonymous users
            # ObjectDoesNotExist - is thrown for non pharmaadmin users
            raise Http404
    elif request.GET.get('user') == 'pharmacy':
        # make sure that only owner pharmacies can view their products
        pharmacy_id = request.GET.get('id')
        pharmacy = get_object_or_404(Pharmacy, id=pharmacy_id)
        if request.user == pharmacy.user:
            pharmacy_products = pharmacy.medication_set.all()
            context.update({
                'pharmacy_name': pharmacy,
                'products': pharmacy_products,
            })
        else:
            raise Http404('Page not found')
    else:
        raise Http404('Page not found')
    context['order_count'] = get_order_count(request)

    return render(request, 'store/pharmacy_products.html', context=context)


def orders(request, status):
    try:  # try getting a pharmacy user
        pharmacy = request.user.pharmacy
        order_items = OrderItem.objects.filter(pharmacy=pharmacy)
    # TODO: find a better way to identify user kind (also see: `get_order_count(...)`)
    except Exception:  # if this block is hit the user is a customer
        customer = request.user.customer
        order_items = OrderItem.objects.filter(order__customer=customer)
    all_order_counts = {
        OrderStatus.PENDING.value:
            len(order_items.filter(status__exact=OrderStatus.PENDING.value)),
        OrderStatus.DISPATCHED.value:
            len(order_items.filter(status__exact=OrderStatus.DISPATCHED.value)),
        OrderStatus.COMPLETE.value:
            len(order_items.filter(status__exact=OrderStatus.COMPLETE.value)),
        OrderStatus.REJECTED.value:
            len(order_items.filter(status__exact=OrderStatus.REJECTED.value)),
        OrderStatus.CANCELED.value:
            len(order_items.filter(status__exact=OrderStatus.CANCELED.value))
    }

    return render(request, 'store/orders.html',
                  context={'orders': order_items.filter(status__exact=status),
                           'status': status,
                           'order_count': get_order_count(request),
                           'all_order_counts': all_order_counts,
                           'cart_count': get_cart_count(get_cart(request))})


@transaction.atomic
def set_order_status(order_item, new_status, rejection_reason=''):
    if order_item.status == new_status:
        return
    else:
        order_item.status = new_status
        if new_status == OrderStatus.REJECTED.value:
            order_item.rejection_reason = rejection_reason
        order_item.save()
        cart_item = order_item.cart_item
        # If an order is put in the CANCELLED or REJECTED state the stock amount must be restored
        if (new_status == OrderStatus.REJECTED.value) or (new_status == OrderStatus.CANCELED.value):
            cart_item.drug.stock += cart_item.quantity
            cart_item.drug.save()


@transaction.atomic
def order_details(request, pk):
    order_item = OrderItem.objects.get(id=pk)

    if request.method == 'POST':
        new_status = request.POST['new_status']
        if new_status in [status.value for status in list(OrderStatus)]:
            # A customer may try to cancel an order that is already dispatched. That should not be allowed.
            if not (new_status == OrderStatus.CANCELED.value and order_item.status == OrderStatus.DISPATCHED.value):
                set_order_status(order_item, new_status, request.POST['rejection_reason'])
                return HttpResponse(f'Order status changed to {new_status}.')
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
        order_prescriptions = listdir(join(MEDIA_ROOT, Order.PRESCRIPTIONS_DIR_NAME, str(order_item.order.pk)))
        image_paths = []
        for image in order_prescriptions:
            image_paths.append(join(MEDIA_URL, Order.PRESCRIPTIONS_DIR_NAME, str(order_item.order.pk), image))
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
            return 0


# make sure only admin can access this page
def pharma_admin_home(request):
    get_object_or_404(PharmaAdmin, user_id=request.user.id)
    pharmacy_count = Pharmacy.objects.count()
    customer_count = Customer.objects.count()
    product_count = Medication.objects.count()

    context = {
        'pharmacies': pharmacy_count,
        'customers': customer_count,
        'products': product_count
    }

    return render(request, 'store/admin/index.html', context=context)


# make sure only admin can view all pharmacies
def user_list(request, user_label):
    user_list = None
    try:
        if request.user.pharmaadmin:
            if user_label == 'pharmacy':
                user_list = Pharmacy.objects.all()
            elif user_label == 'customer':
                user_list = Customer.objects.all()
            else:
                raise Http404
    except AttributeError:
        raise Http404

    context = {
        'user_list': user_list,
        'user_label': user_label
    }

    return render(request, 'store/user_list.html', context=context)


def create_product(request, pk):
    pharmacy = get_object_or_404(Pharmacy, id=pk)
    try:
        # make sure that only owner pharmacy can access this view
        if request.user.pharmacy == pharmacy:
            if request.method == 'POST':
                # file data placed in request.FILES
                form = ProductForm(request.POST, request.FILES)
                if form.is_valid():
                    product = form.save(commit=False)
                    product.pharmacy = pharmacy
                    product.save()
                    messages.success(request, 'Product created.')
                    return redirect(reverse_lazy('store:products') + f'?user=pharmacy&id={pk}')
                else:
                    messages.error(request, 'Unable to create product.')
            else:
                form = ProductForm()
            context = {
                'form': form, 'form_header': 'Add New', 'submit_msg': 'Create',
                'order_count': get_order_count(request)
            }
            return render(request, 'store/manage_product.html', context=context)
    except ObjectDoesNotExist:
        raise Http404


def update_product(request, pk, prod_id):
    pharmacy = get_object_or_404(Pharmacy, id=pk)
    try:
        if request.user.pharmacy == pharmacy:
            product = get_object_or_404(Medication, id=prod_id)
            if request.method == 'POST':
                form = ProductForm(request.POST, request.FILES, instance=product)
                if form.is_valid():
                    if form.has_changed():
                        product = form.save(commit=False)
                        product.pharmacy = pharmacy
                        product.save()
                        messages.success(request, 'Product updated.')
                    return redirect(reverse_lazy('store:products') + f'?user=pharmacy&id={pk}')
                else:
                    messages.error(request, 'Unable to update product.')
            else:
                form = ProductForm(instance=product)
            context = {
                'form': form, 'form_header': 'Edit', 'submit_msg': 'Update',
                'order_count': get_order_count(request)
            }
            return render(request, 'store/manage_product.html', context=context)
    except ObjectDoesNotExist:
        raise Http404


def delete_product(request, pk, prod_id):
    pharmacy = get_object_or_404(Pharmacy, id=pk)
    try:
        if request.user.pharmacy == pharmacy:
            product = get_object_or_404(Medication, id=prod_id)
            if request.method == "POST":
                product.delete()
                messages.success(request, 'Product deleted.')
                return redirect(reverse_lazy('store:products') + f'?user=pharmacy&id={pk}')
            else:
                data = dict()
                context = {'object': product,
                           'object_type': 'product',
                           'action': reverse_lazy('store:product_delete', kwargs={'pk': pk, 'prod_id': prod_id})}
                data['confirm_delete_form'] = render_to_string('store/partial_delete_confirm.html',
                                                               context=context,
                                                               request=request)
                return JsonResponse(data)
    except ObjectDoesNotExist:
        raise Http404


def toggle_active_product(request):
    if request.method == 'POST':
        # make sure that only admin can access this functionality
        try:
            get_object_or_404(PharmaAdmin, user=request.user)
        except TypeError:
            raise Http404('Page not found')

        new_status = request.POST['new_status']

        try:
            product = Medication.objects.get(id=int(request.POST['med_id']))
        except Medication.DoesNotExist:
            raise Http404
        else:
            if new_status == 'active':
                product.active = True
            elif new_status == 'inactive':
                product.active = False
            else:
                return HttpResponseServerError('Invalid Status.')
            product.save()
        return HttpResponse(new_status)
    return redirect('store:pharma_admin_home')
