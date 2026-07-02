from django.contrib.auth.tokens import default_token_generator

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from auth_app.api.serializers import RegistrationSerializer
from auth_app.api.utils import send_activation_email


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
    pass


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