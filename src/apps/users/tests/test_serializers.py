from unittest.mock import ANY, MagicMock, patch

from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import TestCase

from apps.users.models import CustomUser
from apps.users.serializers import LoginSerializer, SignUpSerializer


class SignUpSerializerTests(TestCase):
    def setUp(self):
        self.valid_data = {
            "email": "test@example.com",
            "first_name": "John",
            "last_name": "Doe",
            "password": "securepassword123",
        }

    @patch("apps.users.serializers.SignUpSerializer.send_confirmation_email")
    def test_create_user_and_send_confirmation_email(
        self,
        send_confirmation_email: MagicMock,
    ):
        serializer = SignUpSerializer(data=self.valid_data)
        self.assertTrue(serializer.is_valid())

        serializer.save()

        created_user = CustomUser.objects.get(email="test@example.com")
        created_user.first_name
        self.assertEqual(created_user.first_name, "John")
        self.assertEqual(created_user.last_name, "Doe")
        self.assertTrue(created_user.check_password("securepassword123"))
        send_confirmation_email.assert_called_once_with(created_user)

    @patch("apps.users.serializers.send_mail")
    def test_send_confirmation_mail(self, send_mail: MagicMock):
        subject = "Seu token de confirmação"

        serializer = SignUpSerializer(data=self.valid_data)
        serializer.is_valid()
        serializer.save()

        send_mail.assert_called_once_with(
            subject,
            ANY,
            settings.DEFAULT_FROM_EMAIL,
            [self.valid_data["email"]],
        )


class LoginSerializerTests(TestCase):
    def setUp(self):
        self.user_data = {
            "email": "user@example.com",
            "first_name": "John",
            "last_name": "Doe",
            "password": "strongpassword123",
        }
        self.user = get_user_model().objects.create_user(**self.user_data)
        self.user.save()

    def test_valid_credentials(self):
        serializer = LoginSerializer(data=self.user_data)

        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.validated_data["user"], self.user)

    def test_invalid_password(self):
        data = {"email": "user@example.com", "password": "wrongpassword"}
        serializer = LoginSerializer(data=data)

        self.assertFalse(serializer.is_valid())

    def test_invalid_email(self):
        data = {"email": "wrong@example.com", "password": "strongpassword123"}
        serializer = LoginSerializer(data=data)

        self.assertFalse(serializer.is_valid())

    def test_inactive_user(self):
        self.user.is_active = False
        self.user.save()
        data = {"email": "user@example.com", "password": "strongpassword123"}
        serializer = LoginSerializer(data=data)

        self.assertFalse(serializer.is_valid())
