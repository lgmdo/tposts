import jwt
from django.conf import settings
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.users.models import CustomUser

from .serializers import SignUpSerializer
from .swagger import confirm_sign_up_schema, sign_up_schema


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
