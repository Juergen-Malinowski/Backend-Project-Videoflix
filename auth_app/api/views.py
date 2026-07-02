from django.contrib.auth.tokens import default_token_generator

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from auth_app.api.serializers import RegistrationSerializer
from auth_app.api.utils import get_user_from_uidb64, send_activation_email


class RegistrationView(APIView):
    """Handle user registration requests."""

    authentication_classes = []
    permission_classes = []

    def post(self, request):
        """Create an inactive user and send an activation email."""

        serializer = RegistrationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        token = default_token_generator.make_token(user)
        send_activation_email(user, token)

        return Response(
            {
                'user': {
                    'id': user.id,
                    'email': user.email,
                },
                'token': token,
            },
            status=status.HTTP_201_CREATED,
        )


class AccountActivationView(APIView):
    """Handle account activation requests."""

    authentication_classes = []
    permission_classes = []

    def get(self, request, uidb64, token):
        """Activate a user account if uid and token are valid."""

        user = get_user_from_uidb64(uidb64)

        if user is None or not default_token_generator.check_token(user, token):
            return Response(
                {'message': 'Account activation failed.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user.is_active = True
        user.save(update_fields=['is_active'])

        return Response(
            {'message': 'Account successfully activated.'},
            status=status.HTTP_200_OK,
        )


class LoginView(APIView):
    pass


class LogoutView(APIView):
    pass


class TokenRefreshView(APIView):
    pass


class PasswordResetView(APIView):
    pass


class PasswordConfirmView(APIView):
    pass