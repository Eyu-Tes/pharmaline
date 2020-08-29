from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.http import Http404
from django.shortcuts import render, redirect, get_object_or_404

from .forms import RegistrationForm, LoginForm, CustomerProfileForm, PharmacyProfileForm, UpdateUserForm


from .models import Customer, Pharmacy


# Create your views here.
def index(request):
    return render(request, 'account/index.html')


def register_view(request, user_label):
    if not request.user.is_authenticated:
        form = RegistrationForm()
        if user_label == 'customer':
            profile_form = CustomerProfileForm()
        elif user_label == 'pharmacy':
            profile_form = PharmacyProfileForm()
        else:
            profile_form = None

        if request.method == 'POST':
            form = RegistrationForm(request.POST)
            if user_label == 'customer':
                profile_form = CustomerProfileForm(request.POST)
            elif user_label == 'pharmacy':
                profile_form = PharmacyProfileForm(request.POST)

            if form.is_valid() and profile_form.is_valid():
                user = form.save()
                profile = profile_form.save(commit=False)
                profile.user = user
                profile.save()
                messages.success(request, f"Account created for {form.cleaned_data.get('username')}!")
                return redirect('account:login', user_label=user_label)

        if user_label == 'customer':
            form_header = 'Create Customer Account'
        elif user_label == 'pharmacy':
            form_header = 'Create Pharmacy Account'
        else:
            raise Http404('Page not found')

        if profile_form:
            context = {'form': form, 'profile_form': profile_form,
                       'form_header': form_header, 'submit_msg': 'Sign Up'}

        return render(request, 'account/user_register.html', context=context)
    else:
        messages.warning(request, 'You\'re already logged in. Please logout first.')
        return redirect('store:home')


def login_view(request, user_label):
    if not request.user.is_authenticated:
        form = LoginForm()

        if request.method == 'POST':
            form = LoginForm(request.POST)
            if form.is_valid():
                username = form.cleaned_data.get('username')
                password = form.cleaned_data.get('password')

                user = authenticate(request, username=username, password=password)
                if user:
                    login(request, user)
                    messages.success(request, 'Login successful!')
                    return redirect('store:home')
                else:
                    messages.error(request, 'Username or password is incorrect')

        context = {
            'form': form, 'submit_msg': 'Sign In'
        }

        if user_label == 'customer':
            context['form_header'] = 'Customer Login'
        elif user_label == 'pharmacy':
            context['form_header'] = 'Pharmacy Login'
        else:
            raise Http404("Page not found")

        return render(request, 'account/user_login.html', context=context)
    else:
        messages.warning(request, 'You\'re already logged in. Please logout first.')
        return redirect('store:home')


def logout_view(request):
    # if isinstance(request.user, User):
    if request.user.is_authenticated:
        logged_out_user = request.user
        messages.success(request, f'{logged_out_user} logged out.')
        logout(request)
    else:
        messages.warning(request, 'No logged in user found.')
    return redirect('store:home')


def update_form(form, profile_form):
    user = form.save()
    profile = profile_form.save(commit=False)
    profile.user = user
    profile.save()


def proflie_view(request, user_label, pk):
    if request.user.is_authenticated:
        user_obj = get_object_or_404(User, id=pk)
        form = UpdateUserForm(instance=user_obj)
        if user_label == 'customer':
            customer_obj = Customer.objects.get(user=user_obj)
            profile_form = CustomerProfileForm(instance=customer_obj)
        elif user_label == 'pharmacy':
            pharmacy_obj = Pharmacy.objects.get(user=user_obj)
            profile_form = PharmacyProfileForm(instance=pharmacy_obj)
        else:
            profile_form = None

        if request.method == 'POST':
            form = UpdateUserForm(request.POST, instance=user_obj)
            if user_label == 'customer':
                profile_form = CustomerProfileForm(request.POST, instance=customer_obj)
            elif user_label == 'pharmacy':
                profile_form = PharmacyProfileForm(request.POST, instance=pharmacy_obj)

            if form.is_valid() and profile_form.is_valid():
                if form.has_changed() or profile_form.has_changed():
                    update_form(form, profile_form)
                    messages.success(request, f"Account updated for {form.cleaned_data.get('username')}!")
                return redirect('store:home')

        if user_label == 'customer':
            form_header = 'Customer Profile'
        elif user_label == 'pharmacy':
            form_header = 'Pharmacy Profile'
        else:
            raise Http404('Page not found')

        if profile_form:
            context = {'form': form, 'profile_form': profile_form,
                       'form_header': form_header, 'submit_msg': 'Update'}

        return render(request, 'account/user_profile.html', context=context)
    else:
        messages.warning(request, 'No logged in user found.')
        return redirect('store:home')
