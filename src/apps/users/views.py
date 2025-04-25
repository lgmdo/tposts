from typing import cast

import jwt
from django.conf import settings
from django.db.models import Count, F, Value
from django.db.models.functions import Concat
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.filters import SearchFilter
from rest_framework.generics import ListAPIView
from rest_framework.parsers import MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.utils.paginations import CustomPagination

from .models import CustomUser
from .serializers import (
    LoginSerializer,
    MyProfileSerializer,
    PasswordChangeSerializer,
    ProfilePictureUploadSerializer,
    SignUpSerializer,
    UserListQueryParamsSerializer,
    UserProfileSerializer,
)
from .swagger import (
    change_password_schema,
    confirm_sign_up_schema,
    login_schema,
    logout_schema,
    my_profile_schema,
    profile_picture_schema,
    profile_schema,
    sign_up_schema,
    users_list_schema,
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
        try:
            payload = jwt.decode(  # pyright: ignore
                token,
                settings.SECRET_KEY,
                algorithms=["HS256"],
            )
        except Exception as _:
            return Response(
                {"detail": "Invalid token."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        uid = payload.get("uid")

        if not uid:
            return Response(
                {"detail": "Invalid token."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = get_object_or_404(CustomUser, pk=uid)

        if user.is_email_confirmed:
            return Response(status=status.HTTP_204_NO_CONTENT)

        user.is_email_confirmed = True
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


class ProfilePictureUploadView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser]

    @profile_picture_schema
    def put(self, request: Request):
        try:
            serializer = ProfilePictureUploadSerializer(
                instance=request.user,
                data=request.data,
                partial=True,
            )

            if not serializer.is_valid():
                return Response(
                    serializer.errors, status=status.HTTP_400_BAD_REQUEST
                )

            serializer.save()
            user = cast(CustomUser, request.user)
            return Response(
                {"url": user.profile_picture.url},
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response(
                {"erro": f"{e}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    @change_password_schema
    def post(self, request: Request):
        serializer = PasswordChangeSerializer(
            data=request.data, context={"request": request}
        )
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"detail": "Password changed successfully!"},
                status=status.HTTP_200_OK,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]

    @profile_schema
    def get(self, request: Request, uid: int):
        user = get_object_or_404(CustomUser, pk=uid)
        serializer = UserProfileSerializer(user, context={"request": request})
        return Response(serializer.data)


class UsersViewSet(APIView):
    permission_classes = [IsAuthenticated]

    @profile_schema
    def get(self, request: Request, uid: int):
        user = get_object_or_404(CustomUser, pk=uid)
        serializer = UserProfileSerializer(user, context={"request": request})
        return Response(serializer.data)


class MyProfileView(APIView):
    permission_classes = [IsAuthenticated]

    @my_profile_schema
    def get(self, request: Request):
        user = request.user
        serializer = MyProfileSerializer(user, context={"request": request})
        return Response(serializer.data)


@users_list_schema
class UserListView(ListAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = CustomPagination
    filter_backends = [SearchFilter]
    search_fields = ["first_name", "last_name"]

    def get_queryset(self):
        user = self.request.user

        query_params_serializer = UserListQueryParamsSerializer(
            data=self.request.query_params
        )
        query_params_serializer.is_valid(raise_exception=True)
        validated_query_params = query_params_serializer.validated_data

        qs = CustomUser.objects.exclude(id=user.pk).annotate(
            full_name=Concat(F("first_name"), Value(" "), F("last_name")),
            followers_count=Count("followers", distinct=True),
        )

        if validated_query_params.get("is_following_you"):
            qs = qs.filter(following__followed=user)

        if validated_query_params.get("ordering_type") == "full_name":
            qs = qs.order_by("full_name")
        elif validated_query_params.get("ordering_type") == "followers_count":
            qs = qs.order_by("-followers_count")

        return qs
