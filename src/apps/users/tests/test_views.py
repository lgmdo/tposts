from unittest.mock import ANY, MagicMock, patch

from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

User = get_user_model()


class SignUpViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse("sign-up")  # Update if your name is different
        self.data = {
            "email": "test@example.com",
            "first_name": "John",
            "last_name": "Doe",
            "password": "securepassword123",
        }

    @patch("apps.users.serializers.send_mail")
    def test_user_signup_success(self, send_mail: MagicMock):
        response = self.client.post(
            self.url, self.data, content_type="application/json"
        )

        self.assertEqual(response.status_code, 204)
        self.assertTrue(User.objects.filter(email="test@example.com").exists())
        send_mail.assert_called_once_with(
            ANY,
            ANY,
            settings.DEFAULT_FROM_EMAIL,
            [self.data["email"]],
        )

    @patch("apps.users.serializers.send_mail")
    def test_user_signup_missing_email(self, send_mail: MagicMock):
        data = self.data.copy()
        data.pop("email")
        response = self.client.post(
            self.url, data, content_type="application/json"
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("email", response.json())
        send_mail.assert_not_called()

    @patch("apps.users.serializers.send_mail")
    def test_user_signup_missing_first_name(self, send_mail: MagicMock):
        data = self.data.copy()
        data.pop("first_name")
        response = self.client.post(
            self.url, data, content_type="application/json"
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("first_name", response.json())
        send_mail.assert_not_called()

    @patch("apps.users.serializers.send_mail")
    def test_user_signup_missing_password(self, send_mail: MagicMock):
        data = self.data.copy()
        data.pop("password")
        response = self.client.post(
            self.url, data, content_type="application/json"
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("password", response.json())
        send_mail.assert_not_called()
