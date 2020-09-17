from django.contrib.auth import views as auth_views
from django.urls import path

from .views import (index, login_view, register_view, logout_view, proflie_view, delete_view,
                    RequestUserPasswordResetView, ConfirmUserPasswordResetView,
                    CompleteUserPasswordResetView, UserPasswordChangeView,
                    admin_manage_users_view)

app_name = 'account'

urlpatterns = [
    path('login/<str:user_label>/', login_view, name='login'),
    path('register/<str:user_label>/', register_view, name='register'),
    path('logout/', logout_view, name='logout'),
    path('<str:user_label>/<int:fk>/', proflie_view, name='profile'),
    path('<int:pk>/delete/', delete_view, name='delete'),
    # admin manages user accounts
    path('<str:manage>/<str:user_label>/', admin_manage_users_view, name='admin_manage'),

    # sends the mail with password reset instruction
    path('password_reset/', RequestUserPasswordResetView.as_view(), name='password_reset'),
    # shows an email sent success message
    path('password_reset/done/',
         auth_views.PasswordResetDoneView.as_view(
             template_name='account/password/password_reset_done.html'),
         name='password_reset_done'),
    # returns from password reset email and prompts user for a new pwd
    # uidb64 = user's id encoded in base 64, token = checks if password is valid
    path('reset/<uidb64>/<token>/', ConfirmUserPasswordResetView.as_view(), name='password_reset_confirm'),
    # password successfully changed message
    ############################################
    # don't put the '/' at the end of the path: 'reset/done/<str:user_label>/'
    ############################################
    path('reset/done/<str:user_label>', CompleteUserPasswordResetView.as_view(), name='password_reset_complete'),

    # change password
    path('password_change/', UserPasswordChangeView.as_view(), name='password_change'),
    path('password_change/done/', auth_views.PasswordChangeDoneView.as_view(), name='password_change_done')
]
