from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect

from .forms import RegistrationForm, LoginForm, CustomerProfileForm
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
            return redirect('login')

    context = {
        'form': form, 'profile_form': profile_form, 'form_type': 'register',
        'form_header': 'Create Customer Account', 'submit_msg': 'Sign Up'
    }
    return render(request, 'account/customer_register.html', context=context)


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
            'form': form, 'form_type': 'login', 'submit_msg': 'Sign In'
        }

        if user_label == 'customer':
            context['form_header'] = 'Customer Login'
        else:
            context['form_header'] = 'Pharmacy Login'

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
