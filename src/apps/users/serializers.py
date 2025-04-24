from typing import Any, cast

import jwt
from django.conf import settings
from django.contrib.auth import authenticate, get_user_model
from django.core.mail import send_mail
from django.utils import timezone
from django.utils.timezone import timedelta
from rest_framework import serializers

from apps.users.managers import CustomUserManager
from apps.users.models import CustomUser


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
