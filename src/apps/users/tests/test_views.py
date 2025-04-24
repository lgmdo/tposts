from io import BytesIO
from unittest.mock import ANY, MagicMock, patch

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase
from django.urls import reverse
from PIL import Image
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient, APITestCase
from typing_extensions import cast

from ..models import CustomUser

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


class LoginViewTests(TestCase):
    def setUp(self):
        self.user_data = {
            "email": "test@example.com",
            "first_name": "John",
            "last_name": "Doe",
            "password": "securepassword123",
        }
        self.user = get_user_model().objects.create_user(**self.user_data)
        self.user.is_active = True
        self.user.save()
        self.url = reverse("login")

    def test_login_success(self):
        login_data = {
            "email": self.user_data["email"],
            "password": self.user_data["password"],
        }

        response = self.client.post(self.url, login_data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("token", response.json())

        token = response.json()["token"]
        self.assertTrue(Token.objects.filter(key=token.split(" ")[1]).exists())

    def test_login_invalid_credentials(self):
        invalid_data = {
            "email": "wronguser@example.com",
            "password": "wrongpassword",
        }

        response = self.client.post(self.url, invalid_data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class LogoutViewTests(TestCase):
    def setUp(self):
        self.user_data = {
            "email": "user@example.com",
            "password": "strongpassword123",
            "first_name": "John",
            "last_name": "Doe",
        }
        self.user = get_user_model().objects.create_user(**self.user_data)
        self.user.is_active = True
        self.user.save()

        self.token = Token.objects.create(user=self.user)

        self.api_client: APIClient = APIClient()
        self.url = reverse("logout")

    def test_logout_success(self):
        self.api_client.credentials(
            HTTP_AUTHORIZATION=f"Token {self.token.key}"
        )

        response = self.api_client.post(self.url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        with self.assertRaises(Token.DoesNotExist):
            Token.objects.get(user=self.user)

    def test_logout_without_token(self):
        response = self.api_client.post(self.url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(
            response.json(),
            {"detail": "Authentication credentials were not provided."},
        )

    def test_logout_token_not_found(self):
        self.api_client.credentials(HTTP_AUTHORIZATION="Token invalid_token")

        response = self.api_client.post(self.url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.json(), {"detail": "Invalid token."})


class ProfilePictureUploadViewTest(APITestCase):
    def setUp(self):
        self.user_data = {
            "email": "user@example.com",
            "password": "strongpassword123",
            "first_name": "John",
            "last_name": "Doe",
        }
        self.user = User.objects.create_user(**self.user_data)
        self.url = reverse("profile-picture")
        self.client.force_authenticate(user=self.user)

    def test_upload_profile_picture_success(self):
        image = Image.new("RGB", (1, 1), color="red")  # 1x1 pixel vermelho
        buffer = BytesIO()
        image.save(buffer, format="BMP")
        buffer.seek(0)
        image = SimpleUploadedFile(
            name="test_image.bmp",
            content=buffer.read(),
            content_type="image/bmp",
        )
        response = self.client.put(
            self.url, {"profile_picture": image}, format="multipart"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("url", response.json())
        self.user.refresh_from_db()
        user = cast(CustomUser, self.user)
        print(user.profile_picture)

    def test_upload_profile_picture_invalid_format(self):
        # Simula upload de um arquivo inválido
        txt_file = SimpleUploadedFile(
            "file.txt", b"not an image", content_type="text/plain"
        )
        response = self.client.put(
            self.url, {"profile_picture": txt_file}, format="multipart"
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("profile_picture", response.json())

    def test_unauthenticated_user_cannot_upload(self):
        self.client.logout()
        image = SimpleUploadedFile(
            "profile.jpg", b"file_content", content_type="image/jpeg"
        )
        response = self.client.put(
            self.url, {"profile_picture": image}, format="multipart"
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
