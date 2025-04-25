from enum import Enum
from typing import Any, cast

import jwt
from django.conf import settings
from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.mail import send_mail
from django.utils import timezone
from django.utils.timezone import timedelta
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from .managers import CustomUserManager
from .models import CustomUser


class SignUpSerializer(serializers.ModelSerializer):
    class Meta:  # pyright: ignore
        model = cast(CustomUser, get_user_model())
        fields = ["email", "first_name", "last_name", "password"]
        extra_kwargs = {
            "password": {"write_only": True},
        }

    def create(self, validated_data: Any) -> CustomUser:
        user_model = cast(CustomUserManager, get_user_model().objects)
        user = cast(
            CustomUser,
            user_model.create_user(
                first_name=validated_data["first_name"],
                last_name=validated_data.get("last_name"),
                email=validated_data["email"],
                password=validated_data["password"],
            ),
        )

        self.send_confirmation_email(user)

        return user

    def send_confirmation_email(self, user: CustomUser):
        subject = "Seu token de confirmação"

        expiration = timezone.now() + timedelta(hours=1)
        token = jwt.encode(  # pyright: ignore
            {
                "uid": user.pk,
                "exp": expiration,
            },
            settings.SECRET_KEY,
            algorithm="HS256",
        )

        confirmation_url = (
            settings.DOMAIN + f"/api/v1/users/confirm-sign-up/{token}"
        )
        message = (
            f"Olá {user.first_name},\n\n"
            f"Obrigado por se registrar conosco. Por favor, confirme seu "
            f"endereço de e-mail clicando no link abaixo:\n\n"
            f"{confirmation_url}\n\n"
            f"Se você não se cadastrou para uma conta, pode ignorar "
            f"este e-mail com segurança."
        )

        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user.email])


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(max_length=128)

    def validate(self, attrs: dict["str", Any]):
        email = attrs.get("email")
        password = attrs.get("password")

        user = authenticate(
            username=email,
            password=password,
        )

        if user is None:
            raise serializers.ValidationError("Invalid credentials.")

        attrs["user"] = user
        return attrs


class ProfilePictureUploadSerializer(serializers.ModelSerializer):
    profile_picture = serializers.ImageField()

    class Meta:  # pyright: ignore
        model = CustomUser
        fields = ["profile_picture"]


class PasswordChangeSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True)
    confirm_new_password = serializers.CharField(write_only=True)

    def validate(self, attrs: dict[str, Any]):
        user = self.context["request"].user

        old_password = attrs["old_password"]
        new_password = attrs["new_password"]
        confirm_new_password = attrs["confirm_new_password"]

        if not user.check_password(old_password):
            raise serializers.ValidationError(
                {"old_password": "Old password is incorrect."}
            )

        if new_password != confirm_new_password:
            raise serializers.ValidationError(
                {"new_password": "The new passwords don't match."}
            )

        try:
            validate_password(new_password, user)
        except ValidationError as e:
            raise serializers.ValidationError({"new_password": f"{e}"})

        return attrs

    def save(self, **_: Any):
        user = self.context["request"].user
        new_password = self.validated_data["new_password"]
        user.set_password(new_password)
        user.save()


class UserProfileSerializer(serializers.ModelSerializer):
    is_following_you = serializers.SerializerMethodField()

    class Meta:  # pyright: ignore
        model = CustomUser
        fields = (
            "id",
            "first_name",
            "last_name",
            "email",
            "profile_picture",
            "is_following_you",
        )

    def get_is_following_you(self, obj: CustomUser):
        request_user = self.context["request"].user
        return request_user.followers.filter(follower=obj).exists()


class MyProfileSerializer(serializers.ModelSerializer):
    class Meta:  # pyright: ignore
        model = CustomUser
        fields = (
            "id",
            "first_name",
            "last_name",
            "email",
            "profile_picture",
        )


class UserListQueryParamsSerializer(serializers.Serializer):
    class OrderingType(str, Enum):
        NAME = "name"
        FOLLOWERS = "followers_count"

    search = serializers.CharField(required=False)
    ordering_type = serializers.ChoiceField(
        choices=OrderingType, default=OrderingType.FOLLOWERS
    )
    is_following_you = serializers.BooleanField(required=False)
