from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render, redirect

from .forms import RegistrationForm, LoginForm, CustomerProfileForm, PharmacyProfileForm
# from .models import Customer, Pharmacy


# Create your views here.
def index(request):
    return render(request, 'account/index.html')


def customer_register_view(request):
    form = RegistrationForm()
    profile_form = CustomerProfileForm()
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        profile_form = CustomerProfileForm(request.POST)
        if form.is_valid() and profile_form.is_valid():
            user = form.save()
            profile = profile_form.save(commit=False)
            profile.user = user
            profile.save()
            messages.success(request, f"Account created for {form.cleaned_data.get('username')}!")
            return redirect('account:customer-login')

    context = {
        'form': form, 'profile_form': profile_form, 'form_type': 'register',
        'form_header': 'Create Customer Account', 'submit_msg': 'Sign Up'
    }
    return render(request, 'account/customer_register.html', context=context)


def pharmacy_register_view(request):
    form = RegistrationForm()
    profile_form = PharmacyProfileForm()
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        profile_form = PharmacyProfileForm(request.POST)
        if form.is_valid() and profile_form.is_valid():
            user = form.save()
            profile = profile_form.save(commit=False)
            profile.user = user
            profile.save()
            messages.success(request, f"Account created for {user}!")
            return redirect('account:pharmacy-login')

    context = {
        'form': form, 'profile_form': profile_form, 'form_type': 'register',
        'form_header': 'Create Pharmacy Account', 'submit_msg': 'Sign Up'
    }
    return render(request, 'account/pharmacy_register.html', context=context)


def customer_login_view(request):
    if not request.user.is_authenticated:
        form = LoginForm()
        if request.method == 'POST':
            form = LoginForm(request.POST)
            if form.is_valid():
                username = form.cleaned_data.get('username')
                password = form.cleaned_data.get('password')

                user = authenticate(request, username=username, password=password)
                if user is not None:
                    try:
                        customer = user.customer
                        # Customer.objects.get(user=user)
                    except ObjectDoesNotExist:
                        messages.error(request, "customer by this username doesn't exist")
                    else:
                        login(request, user)
                        messages.success(request, f'{user} has logged in!')
                        return redirect('store:home')
                else:
                    messages.error(request, 'username or password is incorrect')

        context = {
            'form': form, 'form_type': 'login',
            'form_header': 'Customer Login', 'submit_msg': 'Sign In'
        }
        return render(request, 'account/customer_login.html', context=context)
    else:
        messages.warning(request, 'you need to logout from your current account first.')
        return redirect('store:home')


def pharmacy_login_view(request):
    if not request.user.is_authenticated:
        form = LoginForm()
        if request.method == 'POST':
            form = LoginForm(request.POST)
            if form.is_valid():
                username = form.cleaned_data.get('username')
                password = form.cleaned_data.get('password')

                user = authenticate(request, username=username, password=password)
                if user is not None:
                    try:
                        pharmacy = user.pharmacy
                        # Pharmacy.objects.get(user=user)
                    except ObjectDoesNotExist:
                        messages.error(request, "pharmacy by this username doesn't exist")
                    else:
                        login(request, user)
                        messages.success(request, f'{pharmacy} has logged in!')
                        return redirect('store:home')
                else:
                    messages.error(request, 'username or password is incorrect')

        context = {
            'form': form, 'form_type': 'login',
            'form_header': 'Pharmacy Login', 'submit_msg': 'Sign In'
        }
        return render(request, 'account/pharmacy_login.html', context=context)
    else:
        messages.warning(request, 'you need to logout from your current account first.')
        return redirect('store:home')


def logout_view(request):
    # if isinstance(request.user, User):
    if request.user.is_authenticated:
        logged_out_user = request.user
        messages.success(request, f'{logged_out_user} has logged out.')
        logout(request)
    else:
        messages.warning(request, 'no account has logged in.')
    return redirect('store:home')
