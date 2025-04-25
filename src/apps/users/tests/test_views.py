from datetime import timedelta
from io import BytesIO
from typing import cast
from unittest.mock import ANY, MagicMock, patch

import jwt
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase
from django.urls import reverse
from django.utils import timezone
from PIL import Image
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient, APITestCase

from apps.following.models import Follow

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
        user = cast(
            CustomUser, User.objects.filter(email="test@example.com").first()
        )
        self.assertIsNotNone(user)
        self.assertFalse(user.is_email_confirmed)
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


class ConfirmSignUpTests(TestCase):
    def test_confirm_signup_success(self):
        user_data = {
            "email": "test@example.com",
            "first_name": "John",
            "last_name": "Doe",
            "password": "securepassword123",
        }
        user = cast(CustomUser, User.objects.create_user(**user_data))
        expiration = timezone.now() + timedelta(hours=1)
        token = jwt.encode(  # pyright: ignore
            {
                "uid": user.pk,
                "exp": expiration,
            },
            settings.SECRET_KEY,
            algorithm="HS256",
        )
        url = reverse("confirm-sign-up", args=[token])

        response = self.client.get(url)

        user.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertTrue(user.is_email_confirmed)

    def test_confirm_signup_missing_uid(self):
        expiration = timezone.now() + timedelta(hours=1)
        token = jwt.encode(  # pyright: ignore
            {
                "uid": 9999,
                "exp": expiration,
            },
            settings.SECRET_KEY,
            algorithm="HS256",
        )
        url = reverse("confirm-sign-up", args=[token])
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_confirm_signup_already_confirmed(self):
        user_data = {
            "email": "test@example.com",
            "first_name": "John",
            "last_name": "Doe",
            "password": "securepassword123",
        }
        user = cast(CustomUser, User.objects.create_user(**user_data))
        user.is_email_confirmed = True
        user.save()
        expiration = timezone.now() + timedelta(hours=1)
        token = jwt.encode(  # pyright: ignore
            {
                "uid": user.pk,
                "exp": expiration,
            },
            settings.SECRET_KEY,
            algorithm="HS256",
        )
        url = reverse("confirm-sign-up", args=[token])
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_confirm_signup_invalid_token(self):
        url = reverse("confirm-sign-up", args=["token_invalid"])
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class LoginViewTests(TestCase):
    def setUp(self):
        self.user_data = {
            "email": "test@example.com",
            "first_name": "John",
            "last_name": "Doe",
            "password": "securepassword123",
        }
        self.user = User.objects.create_user(**self.user_data)
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
        self.user = User.objects.create_user(**self.user_data)
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


class ProfilePictureUploadViewTests(APITestCase):
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


class ChangePasswordTests(APITestCase):
    def setUp(self):
        self.user_data = {
            "email": "user@example.com",
            "password": "old_password123",
            "first_name": "John",
            "last_name": "Doe",
        }
        self.user = User.objects.create_user(**self.user_data)
        self.client.force_authenticate(user=self.user)
        self.url = reverse("change-password")

    def test_change_password_success(self):
        data = {
            "old_password": "old_password123",
            "new_password": "new_secure_password456",
            "confirm_new_password": "new_secure_password456",
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password("new_secure_password456"))

    def test_wrong_old_password(self):
        data = {
            "old_password": "wrong_old_password",
            "new_password": "new_secure_password456",
            "confirm_new_password": "new_secure_password456",
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_mismatched_new_passwords(self):
        data = {
            "old_password": "old_password123",
            "new_password": "new_secure_password456",
            "confirm_new_password": "different_password789",
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class UserProfileViewTests(APITestCase):
    def setUp(self):
        user_data = {
            "email": "main@example.com",
            "password": "password123",
            "first_name": "Main",
            "last_name": "User",
        }
        self.user = cast(
            CustomUser,
            User.objects.create_user(**user_data),
        )
        other_user_data = {
            "email": "other@example.com",
            "password": "password123",
            "first_name": "Other",
            "last_name": "User",
        }
        self.other_user = cast(
            CustomUser,
            User.objects.create_user(**other_user_data),
        )

        self.url = reverse("user-profile", args=[self.other_user.pk])

    def test_unauthenticated_user_cannot_access_profile(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_authenticated_user_can_view_profile(self):
        self.client.force_authenticate(user=self.user)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(data["id"], self.other_user.pk)
        self.assertEqual(data["first_name"], self.other_user.first_name)
        self.assertEqual(data["last_name"], self.other_user.last_name)
        self.assertIsNone(data["profile_picture"])
        self.assertFalse(data["is_following_you"])

    def test_is_following_you_true(self):
        Follow.objects.create(follower=self.other_user, followed=self.user)
        self.client.force_authenticate(user=self.user)

        response = self.client.get(self.url)

        self.assertTrue(response.json()["is_following_you"])

    def test_user_not_found(self):
        self.client.force_authenticate(user=self.user)
        invalid_url = reverse("user-profile", args=[9999])

        response = self.client.get(invalid_url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class MyProfileViewTests(APITestCase):
    def setUp(self):
        self.user_data = {
            "email": "user@example.com",
            "password": "old_password123",
            "first_name": "John",
            "last_name": "Doe",
        }
        self.user = User.objects.create_user(**self.user_data)
        self.client.force_authenticate(self.user)
        self.url = reverse("my-profile")

    def test_get_my_profile(self):
        response = self.client.get(self.url)

        data = response.json()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data["email"], self.user.email)
        self.assertEqual(data["first_name"], self.user.first_name)
        self.assertEqual(data["last_name"], self.user.last_name)
        self.assertIsNone(data["profile_picture"])
        self.assertEqual(data["last_name"], self.user.last_name)


class UserListViewTests(APITestCase):
    def setUp(self):
        user_data = {
            "email": "me@example.com",
            "password": "pass",
            "first_name": "Me",
            "last_name": "Myself",
        }
        self.user = cast(CustomUser, User.objects.create_user(**user_data))
        other_one_data = {
            "email": "a@example.com",
            "password": "pass",
            "first_name": "Alice",
            "last_name": "Zed",
        }
        self.other_one = cast(
            CustomUser,
            User.objects.create_user(**other_one_data),
        )
        other_two_data = {
            "email": "b@example.com",
            "password": "pass",
            "first_name": "Bob",
            "last_name": "Yard",
        }
        self.other_two = cast(
            CustomUser,
            User.objects.create_user(**other_two_data),
        )
        self.client.force_authenticate(user=self.user)
        self.url = reverse("user-list")

    def test_list_users_successfully(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(len(data), 2)

        self.assertEqual(data[0]["id"], self.other_one.pk)
        self.assertEqual(data[0]["first_name"], self.other_one.first_name)
        self.assertEqual(data[0]["last_name"], self.other_one.last_name)
        self.assertEqual(data[0]["email"], self.other_one.email)
        self.assertIsNone(data[0]["profile_picture"])
        self.assertFalse(data[0]["is_following_you"])

        self.assertEqual(data[1]["id"], self.other_two.pk)
        self.assertEqual(data[1]["first_name"], self.other_two.first_name)
        self.assertEqual(data[1]["last_name"], self.other_two.last_name)
        self.assertEqual(data[1]["email"], self.other_two.email)
        self.assertIsNone(data[1]["profile_picture"])
        self.assertFalse(data[1]["is_following_you"])

    def test_search_users_by_name(self):
        response = self.client.get(self.url, {"search": "Alice"})
        data = response.json()

        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["id"], self.other_one.pk)
        self.assertEqual(data[0]["first_name"], self.other_one.first_name)
        self.assertEqual(data[0]["last_name"], self.other_one.last_name)
        self.assertEqual(data[0]["email"], self.other_one.email)
        self.assertIsNone(data[0]["profile_picture"])
        self.assertFalse(data[0]["is_following_you"])

    def test_filter_is_following_you(self):
        Follow.objects.create(follower=self.other_one, followed=self.user)

        response = self.client.get(self.url, {"is_following_you": True})
        data = response.json()

        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["id"], self.other_one.pk)
        self.assertEqual(data[0]["first_name"], self.other_one.first_name)
        self.assertEqual(data[0]["last_name"], self.other_one.last_name)
        self.assertEqual(data[0]["email"], self.other_one.email)
        self.assertIsNone(data[0]["profile_picture"])
        self.assertTrue(data[0]["is_following_you"])

    def test_ordering_by_name(self):
        response = self.client.get(self.url, {"ordering_type": "name"})
        data = response.json()

        names = [u["first_name"] for u in data]
        self.assertEqual(names, sorted(names))

    def test_ordering_by_followers_count(self):
        Follow.objects.create(follower=self.user, followed=self.other_one)

        response = self.client.get(
            self.url, {"ordering_type": "followers_count"}
        )
        data = response.json()

        self.assertEqual(data[0]["id"], self.other_one.pk)
        self.assertEqual(data[0]["first_name"], self.other_one.first_name)
        self.assertEqual(data[0]["last_name"], self.other_one.last_name)
        self.assertEqual(data[0]["email"], self.other_one.email)
        self.assertIsNone(data[0]["profile_picture"])
        self.assertFalse(data[0]["is_following_you"])

    def test_pagination(self):
        Follow.objects.create(follower=self.user, followed=self.other_one)

        response = self.client.get(self.url, {"page": 1, "page_size": 1})
        data = response.json()

        self.assertEqual(data["count"], 2)
        self.assertIn("page=2", data["next"])
        self.assertIsNone(data["previous"])
        data = data["results"]
        self.assertEqual(data[0]["id"], self.other_one.pk)
        self.assertEqual(data[0]["first_name"], self.other_one.first_name)
        self.assertEqual(data[0]["last_name"], self.other_one.last_name)
        self.assertEqual(data[0]["email"], self.other_one.email)
        self.assertIsNone(data[0]["profile_picture"])
        self.assertFalse(data[0]["is_following_you"])
