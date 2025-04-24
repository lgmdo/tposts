from typing import cast

from django.contrib.auth import get_user_model
from django.test import TestCase

from apps.users.models import CustomUser

from ..managers import CustomUserManager


class UsersManagersTests(TestCase):
    def test_create_user(self):
        User = cast(CustomUserManager, get_user_model().objects)
        user = cast(
            CustomUser,
            User.create_user(
                email="normal@user.com",
                first_name="leonardo",
                last_name="moreira",
                password="foo",
            ),
        )
        self.assertEqual(user.email, "normal@user.com")
        self.assertFalse(user.is_active)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

    def test_create_superuser(self):
        User = cast(CustomUserManager, get_user_model().objects)
        admin_user = cast(
            CustomUser,
            User.create_superuser(
                email="super@user.com",
                first_name="leonardo",
                last_name="moreira",
                password="foo",
            ),
        )
        self.assertEqual(admin_user.email, "super@user.com")
        self.assertTrue(admin_user.is_active)
        self.assertTrue(admin_user.is_staff)
        self.assertTrue(admin_user.is_superuser)
