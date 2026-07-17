"""Utility functions for the Videoflix authentication API."""

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode


def build_activation_url(user, token):
    """Build the backend account activation URL for a user."""

    uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
    return f'/api/activate/{uidb64}/{token}/'


def build_frontend_activation_url(user, token):
    """Build the absolute frontend account activation URL for a user."""

    uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
    return (
        f'{settings.FRONTEND_BASE_URL}'
        f'/pages/auth/activate.html?uid={uidb64}&token={token}'
    )


def build_activation_email_message(user, token):
    """Build the plain text activation email message."""

    frontend_url = build_frontend_activation_url(user, token)
    activation_url = build_activation_url(user, token)

    return (
        'Welcome to Videoflix.\n\n'
        'Please activate your account using this link:\n'
        f'{frontend_url}\n\n'
        'Backend activation endpoint:\n'
        f'{activation_url}\n\n'
        'If you did not create this account, you can ignore this email.'
    )


def build_activation_email_html(user, token):
    """Render the HTML activation email message."""

    return render_to_string(
        'auth_app/emails/activation_email.html',
        {
            'user': user,
            'activation_url': build_frontend_activation_url(user, token),
        },
    )


def send_activation_email(user, token):
    """Send an account activation email to a newly registered user."""

    message = build_activation_email_message(user, token)
    html_message = build_activation_email_html(user, token)

    email = EmailMultiAlternatives(
        subject='Activate your Videoflix account',
        body=message,
        from_email=None,
        to=[user.email],
    )

    email.attach_alternative(html_message, 'text/html')
    email.send()


def build_password_confirm_url(user, token):
    """Build the backend password confirmation URL for a user."""

    uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
    return f'/api/password_confirm/{uidb64}/{token}/'


def build_frontend_password_confirm_url(user, token):
    """Build the absolute frontend password confirmation URL for a user."""

    uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
    return (
        f'{settings.FRONTEND_BASE_URL}'
        f'/pages/auth/confirm_password.html?uid={uidb64}&token={token}'
    )


def build_password_reset_email_message(user, token):
    """Build the plain text password reset email message."""

    frontend_url = build_frontend_password_confirm_url(user, token)
    confirm_url = build_password_confirm_url(user, token)

    return (
        'You requested a password reset for your Videoflix account.\n\n'
        'Please set a new password using this link:\n'
        f'{frontend_url}\n\n'
        'Backend password confirmation endpoint:\n'
        f'{confirm_url}\n\n'
        'If you did not request this password reset, you can ignore this email.'
    )


def build_password_reset_email_html(user, token):
    """Render the HTML password reset email message."""

    return render_to_string(
        'auth_app/emails/password_reset_email.html',
        {
            'user': user,
            'password_confirm_url': build_frontend_password_confirm_url(
                user,
                token,
            ),
        },
    )


def send_password_reset_email(user, token):
    """Send a password reset email to a user."""

    message = build_password_reset_email_message(user, token)
    html_message = build_password_reset_email_html(user, token)

    email = EmailMultiAlternatives(
        subject='Reset your Videoflix password',
        body=message,
        from_email=None,
        to=[user.email],
    )

    email.attach_alternative(html_message, 'text/html')
    email.send()


def get_user_from_uidb64(uidb64):
    """Return a user for a base64 encoded user id."""

    user_model = get_user_model()

    try:
        user_id = force_str(urlsafe_base64_decode(uidb64))
        return user_model.objects.get(pk=user_id)
    except (TypeError, ValueError, OverflowError, user_model.DoesNotExist):
        return None


def set_auth_cookies(response, access_token, refresh_token):
    """Set HttpOnly JWT authentication cookies on a response."""

    response.set_cookie(
        key='access_token',
        value=str(access_token),
        httponly=True,
        samesite='Lax',
        max_age=int(
            settings.SIMPLE_JWT['ACCESS_TOKEN_LIFETIME'].total_seconds()
        ),
    )
    response.set_cookie(
        key='refresh_token',
        value=str(refresh_token),
        httponly=True,
        samesite='Lax',
        max_age=int(
            settings.SIMPLE_JWT['REFRESH_TOKEN_LIFETIME'].total_seconds()
        ),
    )


def delete_auth_cookies(response):
    """Delete JWT authentication cookies from a response."""

    response.delete_cookie('access_token', samesite='Lax')
    response.delete_cookie('refresh_token', samesite='Lax')