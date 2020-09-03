from django.contrib.auth import views as auth_views
from django.urls import path, reverse_lazy

from .views import (index, login_view, register_view, logout_view, proflie_view, delete_view,
                    UserPasswordResetConfirmView, UserPasswordResetCompleteView)
from .forms import ResetUserPasswordForm

app_name = 'account'

urlpatterns = [
    path('', index, name='home'),
    path('login/<str:user_label>', login_view, name='login'),
    path('register/<str:user_label>', register_view, name='register'),
    path('logout/', logout_view, name='logout'),
    path('<str:user_label>/<int:fk>/', proflie_view, name='profile'),
    path('<int:pk>/delete/', delete_view, name='delete'),


    # sends the mail with password reset instruction
    path('password_reset/',
         auth_views.PasswordResetView.as_view(
             form_class=ResetUserPasswordForm,
             success_url=reverse_lazy('account:password_reset_done'),
             template_name='account/password/password_reset.html',
             # password reset email content
             email_template_name='account/password/password_reset_email.html'),
         name='password_reset'),
    # shows an email sent success message
    path('password_reset/done/',
         auth_views.PasswordResetDoneView.as_view(
             template_name='account/password/password_reset_done.html'),
         name='password_reset_done'),
    # returns from password reset email and prompts user for a new pwd
    # uidb64 = user's id encoded in base 64, token = checks if password is valid
    path('reset/<uidb64>/<token>/', UserPasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    # password successfully changed message
    ############################################
    # don't put the '/' at the end of the path: 'reset/done/<str:user_label>/'
    ############################################
    path('reset/done/<str:user_label>', UserPasswordResetCompleteView.as_view(), name='password_reset_complete')
]
