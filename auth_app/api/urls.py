from django.urls import path

from auth_app.api.views import (
    AccountActivationView,
    LoginView,
    LogoutView,
    PasswordConfirmView,
    PasswordResetView,
    RegistrationView,
    TokenRefreshView,
)

urlpatterns = [
    path('register/', RegistrationView.as_view(), name='registration'),
    path(
        'activate/<uidb64>/<token>/',
        AccountActivationView.as_view(),
        name='account-activation',
    ),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token-refresh'),
    path('password_reset/', PasswordResetView.as_view(), name='password-reset',),
    path(
        'password_confirm/<uidb64>/<token>/',
        PasswordConfirmView.as_view(),
        name='password-confirm',
    ),
]