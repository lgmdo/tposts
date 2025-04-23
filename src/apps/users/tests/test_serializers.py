from unittest.mock import ANY, MagicMock, patch

from django.conf import settings
from django.test import TestCase

from apps.users.models import CustomUser
from apps.users.serializers import SignUpSerializer


class SignUpSerializerTest(TestCase):
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
