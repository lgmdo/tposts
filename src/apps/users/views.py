import jwt
from django.conf import settings
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.users.models import CustomUser

from .serializers import LoginSerializer, SignUpSerializer
from .swagger import (
    confirm_sign_up_schema,
    login_schema,
    logout_schema,
    sign_up_schema,
)


class SignUpView(APIView):
    @sign_up_schema
    def post(self, request: Request):
        """
        Creates a new user account with the provided information. After
        registration, a confirmation token is sent to the user's email address.
        This token must be used to confirm the account before login is allowed.
        """
        serializer = SignUpSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                status=status.HTTP_204_NO_CONTENT,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ConfirmSignUpView(APIView):
    @confirm_sign_up_schema
    def get(self, request: Request, token: str):
        """
        Uses token sent to email by the sign-up route to validate the user
        registration
        """
        payload = jwt.decode(  # pyright: ignore
            token,
            settings.SECRET_KEY,
            algorithms=["HS256"],
        )
        uid = payload.get("uid")

        if not uid:
            return Response(
                {"detail": "Token inválido"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = get_object_or_404(CustomUser, pk=uid)

        if user.is_active:
            return Response(status=status.HTTP_204_NO_CONTENT)

        user.is_active = True
        user.save()
        return Response(
            status=status.HTTP_204_NO_CONTENT,
        )


class LoginView(APIView):
    @login_schema
    def post(self, request: Request):
        """
        Authenticates user with email and password and responds with and auth
        token
        """
        serializer = LoginSerializer(
            data=request.data,
            context={"request": request},
        )

        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = serializer.validated_data["user"]
        token, _ = Token.objects.get_or_create(user=user)
        return Response(
            {"token": f"Token {token.key}"},
            status=status.HTTP_200_OK,
        )


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    @logout_schema
    def post(self, request: Request):
        try:
            token = Token.objects.get(user=request.user)
            token.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Token.DoesNotExist:
            return Response(
                {"detail": "Token not found."},
                status=status.HTTP_401_UNAUTHORIZED,
            )
