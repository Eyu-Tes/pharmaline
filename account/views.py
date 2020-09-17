from smtplib import SMTPException
import socket

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.views import PasswordResetConfirmView, PasswordResetCompleteView, PasswordChangeView
from django.contrib.sites.shortcuts import get_current_site
from django.core.exceptions import ObjectDoesNotExist
from django.core.mail import send_mail
from django.db.models.query_utils import Q
from django.http import Http404, HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.template import loader
from django.urls import reverse_lazy
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.views.generic import FormView, TemplateView

from .forms import (RegistrationForm, LoginForm, UpdateUserForm,
                    CustomerProfileForm, PharmacyProfileForm, PharmaAdminProfileForm,
                    ConfirmUserPasswordResetForm, RequestUserPasswordResetForm, UserPasswordChangeForm)
from .models import Customer, Pharmacy, PharmaAdmin

from store.views import get_order_count, get_cart, get_cart_count


# Create your views here.
def register_view(request, user_label):
    form = RegistrationForm()
    if user_label == 'customer':
        profile_form = CustomerProfileForm()
    elif user_label == 'pharmacy':
        # make sure that only pharma-admins can create pharmacy account
        try:
            get_object_or_404(PharmaAdmin, user=request.user)
        except TypeError:
            raise Http404('Page not found')
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
            if user_label == 'pharmacy':
                return redirect('store:user_list', user_label='pharmacy')
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
                    try:
                        if user_label == 'customer' and Customer.objects.get(user=user):
                            redirect_to = 'store:home'
                        elif user_label == 'pharmacy' and Pharmacy.objects.get(user=user):
                            redirect_to = 'store:home'
                        elif user_label == 'pharma_admin' and PharmaAdmin.objects.get(user=user):
                            redirect_to = 'store:pharma_admin_home'
                    except ObjectDoesNotExist:
                        messages.error(request, 'Username or password is incorrect.')
                    else:
                        login(request, user)
                        messages.success(request, 'Login successful!')
                        return redirect(redirect_to)
                else:
                    messages.error(request, 'Username or password is incorrect')

        context = {
            'form': form, 'submit_msg': 'Sign In'
        }

        if user_label == 'customer':
            context['form_header'] = 'Customer Login'
        elif user_label == 'pharmacy':
            context['form_header'] = 'Pharmacy Login'
        elif user_label == 'pharma_admin':
            context['form_header'] = 'Administrator Login'
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


def update_user(form, profile_form):
    user = form.save()
    profile = profile_form.save(commit=False)
    profile.user = user
    profile.save()


# make sure that only account owners can view their profile page
def proflie_view(request, user_label, fk):
    if request.user.is_authenticated:
        user_obj = get_object_or_404(User, id=fk)
        if user_obj != request.user:
            raise Http404('Page not found')
        form = UpdateUserForm(instance=user_obj, initial={'id': fk})
        if user_label == 'customer':
            customer_obj = get_object_or_404(Customer, user=user_obj)
            profile_form = CustomerProfileForm(instance=customer_obj)
        elif user_label == 'pharmacy':
            pharmacy_obj = get_object_or_404(Pharmacy, user=user_obj)
            profile_form = PharmacyProfileForm(instance=pharmacy_obj)
        elif user_label == 'pharma_admin':
            pharma_admin_obj = get_object_or_404(PharmaAdmin, user=user_obj)
            profile_form = PharmaAdminProfileForm(instance=pharma_admin_obj)
        else:
            profile_form = None

        if request.method == 'POST':
            form = UpdateUserForm(request.POST, instance=user_obj, initial={'id': fk})
            if user_label == 'customer':
                profile_form = CustomerProfileForm(request.POST, instance=customer_obj)
            elif user_label == 'pharmacy':
                profile_form = PharmacyProfileForm(request.POST, instance=pharmacy_obj)
            elif user_label == 'pharma_admin':
                profile_form = PharmaAdminProfileForm(request.POST, instance=pharma_admin_obj)

            if form.is_valid() and profile_form.is_valid():
                if form.has_changed() or profile_form.has_changed():
                    update_user(form, profile_form)
                    messages.success(request, f"Account updated for {form.cleaned_data.get('username')}!")

                if user_label == 'pharma_admin':
                    return redirect('store:pharma_admin_home')
                return redirect('store:home')

        if user_label == 'customer':
            form_header = 'Customer Profile'
        elif user_label == 'pharmacy':
            form_header = 'Pharmacy Profile'
        elif user_label == 'pharma_admin':
            form_header = 'Administrator Profile'
        else:
            raise Http404('Page not found')

        if profile_form:
            context = {'form': form, 'profile_form': profile_form,
                       'form_header': form_header, 'submit_msg': 'Update',
                       'order_count': get_order_count(request),
                       'cart_count': get_cart_count(get_cart(request))}

        return render(request, 'account/user_profile.html', context=context)
    else:
        messages.warning(request, 'No logged in user found.')
        return redirect('store:home')


def delete_view(request, pk):
    if request.user.is_authenticated:
        # make sure that only a user can delete it's account from this view
        if request.user.id == pk:
            user_obj = get_object_or_404(User, id=pk)
            if request.method == "POST":
                user_obj.delete()
                messages.success(request, 'Account Deleted')
                return redirect('store:home')
        else:
            raise Http404('Page not found')
        return render(request, 'account/user_profile.html')
    else:
        messages.warning(request, 'No logged in user found.')
        return redirect('store:home')


class RequestUserPasswordResetView(FormView):
    template_name = 'account/password/password_reset.html'
    success_url = reverse_lazy('account:password_reset_done')
    form_class = RequestUserPasswordResetForm

    def form_valid(self, form):
        form_email = form.cleaned_data["email"]
        user = User.objects.filter(Q(email=form_email)).first()
        if user:
            c = {
                'email': user.email,
                'domain': self.request.META['HTTP_HOST'],
                'site_name': get_current_site(self.request),
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'user': user,
                'token': default_token_generator.make_token(user),
                'protocol': self.request.scheme,
            }
            email_template_name = 'account/password/password_reset_email.html'
            subject = f"Password reset on {c['site_name']}"
            email = loader.render_to_string(email_template_name, c)
            try:
                send_mail(subject, email, settings.EMAIL_HOST_USER, [user.email], fail_silently=False)
            except SMTPException:
                messages.warning(self.request, 'Invalid e-mail address. Please check again.')
            except socket.gaierror:
                messages.warning(self.request, 'Email failed. Please check your connection.')
            else:
                return super().form_valid(form)

        return super().form_invalid(form)


class ConfirmUserPasswordResetView(PasswordResetConfirmView):
    form_class = ConfirmUserPasswordResetForm
    template_name = 'account/password/password_reset_confirm.html'

    def get_success_url(self):
        try:
            if self.user.customer:
                user_label = 'customer'
        except ObjectDoesNotExist:
            pass
        try:
            if self.user.pharmacy:
                user_label = 'pharmacy'
        except ObjectDoesNotExist:
            pass
        return reverse_lazy('account:password_reset_complete', kwargs={'user_label': user_label})


class CompleteUserPasswordResetView(PasswordResetCompleteView):
    template_name = 'account/password/password_reset_complete.html'

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        context['user_label'] = self.kwargs.get('user_label')
        return context


class UserPasswordChangeView(PasswordChangeView):
    form_class = UserPasswordChangeForm
    success_url = reverse_lazy('account:password_change_done')
    template_name = 'account/password/password_change.html'

    def get_success_url(self):
        try:
            if self.request.user.customer:
                user_label = 'customer'
        except ObjectDoesNotExist:
            pass
        try:
            if self.request.user.pharmacy:
                user_label = 'pharmacy'
        except ObjectDoesNotExist:
            pass
        messages.success(self.request, 'Your password was changed.')
        return reverse_lazy('account:profile',
                            kwargs={'user_label': user_label, 'fk': self.request.user.id})


def admin_manage_users_view(request, manage, user_label, pk):
    # make sure that only admin can access this functionality
    try:
        get_object_or_404(PharmaAdmin, user=request.user)
    except TypeError:
        raise Http404('Page not found')

    if user_label == 'pharmacy' and manage in ['delete', 'disable', 'enable']:
        pass
    elif user_label == 'customer' and manage in ['disable', 'enable']:
        pass
    else:
        raise Http404('Page not found')

    success_msg = ''
    try:
        target_user = None
        if user_label == 'pharmacy':
            target_user = Pharmacy.objects.filter(id=pk).first()
        elif user_label == 'customer':
            target_user = Customer.objects.filter(id=pk).first()

        user_obj = target_user.user

        if target_user:
            if manage == 'delete':
                user_obj.delete()
                success_msg = f'{user_obj} account deleted'
            elif manage == 'disable':
                target_user.disabled = True
                target_user.save()
                success_msg = f'{user_obj} account disabled'
            elif manage == 'enable':
                target_user.disabled = False
                target_user.save()
                success_msg = f'{user_obj} account enabled'
        else:
            raise ObjectDoesNotExist
    except ObjectDoesNotExist:
        messages.error(request, 'Account not found.')
    else:
        messages.success(request, success_msg)

    return redirect('store:user_list', user_label=user_label)
