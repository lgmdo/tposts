from typing import cast

from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APITestCase

from apps.following.models import Follow
from apps.users.models import CustomUser

User = get_user_model()


class FollowingListViewTests(APITestCase):
    def setUp(self):
        self.url = reverse("following")

        email_confirmed_user_data_one = {
            "email": "emailconfirmedone@example.com",
            "first_name": "email",
            "last_name": "confirmed",
            "password": "testpass123",
        }
        self.email_confirmed_user_one = cast(
            CustomUser,
            User.objects.create_user(**email_confirmed_user_data_one),
        )
        self.email_confirmed_user_one.is_email_confirmed = True
        self.email_confirmed_user_one.save()

        email_confirmed_user_data_two = {
            "email": "emailconfirmedtwo@example.com",
            "first_name": "Anais",
            "last_name": "Claudia",
            "password": "testpass123",
        }
        self.email_confirmed_user_two = cast(
            CustomUser,
            User.objects.create_user(**email_confirmed_user_data_two),
        )
        self.email_confirmed_user_two.is_email_confirmed = True
        self.email_confirmed_user_two.save()

        email_confirmed_user_data_three = {
            "email": "emailconfirmedthree@example.com",
            "first_name": "Ana",
            "last_name": "Lucia",
            "password": "testpass123",
        }
        self.email_confirmed_user_three = cast(
            CustomUser,
            User.objects.create_user(**email_confirmed_user_data_three),
        )
        self.email_confirmed_user_three.is_email_confirmed = True
        self.email_confirmed_user_three.save()

        active_user_data = {
            "email": "zeno@example.com",
            "first_name": "Zeno",
            "last_name": "Batista",
            "password": "testpass123",
        }
        self.active_user = cast(
            CustomUser,
            User.objects.create_user(**active_user_data),
        )

        inactive_user_data = {
            "email": "inactive@example.com",
            "first_name": "inactive",
            "last_name": "inactive",
            "password": "testpass123",
        }
        self.inactive_user = User.objects.create_user(**inactive_user_data)
        self.inactive_user.is_active = False

    def test_unauthenticated_user_cannot_access(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 401)

    def test_inactive_user_cannot_access(self):
        self.client.force_authenticate(self.inactive_user)
        self.client.login(
            email=self.inactive_user.email,
            password=self.inactive_user.password,
        )
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403)

    def test_active_user_without_email_confirmed_cannot_access(self):
        self.client.force_authenticate(self.active_user)
        self.client.login(
            email=self.active_user.email,
            password=self.active_user.password,
        )
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403)

    def test_email_confirmed_user_can_access(self):
        Follow.objects.create(
            follower=self.email_confirmed_user_one,
            followed=self.email_confirmed_user_two,
        )
        Follow.objects.create(
            follower=self.email_confirmed_user_one,
            followed=self.email_confirmed_user_three,
        )
        Follow.objects.create(
            follower=self.email_confirmed_user_three,
            followed=self.email_confirmed_user_one,
        )
        Follow.objects.create(
            follower=self.email_confirmed_user_one,
            followed=self.active_user,
        )
        self.client.force_authenticate(self.email_confirmed_user_one)

        # Default response
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        following = response.json()
        self.assertEqual(len(following), 3)
        self.assertEqual(
            following[0],
            {
                "id": self.active_user.pk,
                "first_name": self.active_user.first_name,
                "last_name": self.active_user.last_name,
                "email": self.active_user.email,
                "is_mutual": False,
                "profile_picture": (
                    self.active_user.profile_picture.url
                    if self.active_user.profile_picture
                    else None
                ),
            },
        )
        self.assertEqual(
            following[1],
            {
                "id": self.email_confirmed_user_three.pk,
                "first_name": self.email_confirmed_user_three.first_name,
                "last_name": self.email_confirmed_user_three.last_name,
                "email": self.email_confirmed_user_three.email,
                "is_mutual": True,
                "profile_picture": (
                    self.email_confirmed_user_three.profile_picture.url
                    if self.email_confirmed_user_three.profile_picture
                    else None
                ),
            },
        )
        self.assertEqual(
            following[2],
            {
                "id": self.email_confirmed_user_two.pk,
                "first_name": self.email_confirmed_user_two.first_name,
                "last_name": self.email_confirmed_user_two.last_name,
                "email": self.email_confirmed_user_two.email,
                "is_mutual": False,
                "profile_picture": (
                    self.email_confirmed_user_two.profile_picture.url
                    if self.email_confirmed_user_two.profile_picture
                    else None
                ),
            },
        )

        # Ordered by name
        response = self.client.get(self.url, {"ordering_type": "name"})

        self.assertEqual(response.status_code, 200)
        following = response.json()
        self.assertEqual(len(following), 3)
        self.assertEqual(
            following[0],
            {
                "id": self.email_confirmed_user_two.pk,
                "first_name": self.email_confirmed_user_two.first_name,
                "last_name": self.email_confirmed_user_two.last_name,
                "email": self.email_confirmed_user_two.email,
                "is_mutual": False,
                "profile_picture": (
                    self.email_confirmed_user_two.profile_picture.url
                    if self.email_confirmed_user_two.profile_picture
                    else None
                ),
            },
        )
        self.assertEqual(
            following[1],
            {
                "id": self.email_confirmed_user_three.pk,
                "first_name": self.email_confirmed_user_three.first_name,
                "last_name": self.email_confirmed_user_three.last_name,
                "email": self.email_confirmed_user_three.email,
                "is_mutual": True,
                "profile_picture": (
                    self.email_confirmed_user_three.profile_picture.url
                    if self.email_confirmed_user_three.profile_picture
                    else None
                ),
            },
        )
        self.assertEqual(
            following[2],
            {
                "id": self.active_user.pk,
                "first_name": self.active_user.first_name,
                "last_name": self.active_user.last_name,
                "email": self.active_user.email,
                "is_mutual": False,
                "profile_picture": (
                    self.active_user.profile_picture.url
                    if self.active_user.profile_picture
                    else None
                ),
            },
        )

        # Ordered by creation (same as default response)
        response = self.client.get(self.url, {"ordering_type": "creation"})

        self.assertEqual(response.status_code, 200)
        following = response.json()
        self.assertEqual(len(following), 3)
        self.assertEqual(
            following[0],
            {
                "id": self.active_user.pk,
                "first_name": self.active_user.first_name,
                "last_name": self.active_user.last_name,
                "email": self.active_user.email,
                "is_mutual": False,
                "profile_picture": (
                    self.active_user.profile_picture.url
                    if self.active_user.profile_picture
                    else None
                ),
            },
        )
        self.assertEqual(
            following[1],
            {
                "id": self.email_confirmed_user_three.pk,
                "first_name": self.email_confirmed_user_three.first_name,
                "last_name": self.email_confirmed_user_three.last_name,
                "email": self.email_confirmed_user_three.email,
                "is_mutual": True,
                "profile_picture": (
                    self.email_confirmed_user_three.profile_picture.url
                    if self.email_confirmed_user_three.profile_picture
                    else None
                ),
            },
        )
        self.assertEqual(
            following[2],
            {
                "id": self.email_confirmed_user_two.pk,
                "first_name": self.email_confirmed_user_two.first_name,
                "last_name": self.email_confirmed_user_two.last_name,
                "email": self.email_confirmed_user_two.email,
                "is_mutual": False,
                "profile_picture": (
                    self.email_confirmed_user_two.profile_picture.url
                    if self.email_confirmed_user_two.profile_picture
                    else None
                ),
            },
        )

        # List only mutual following
        response = self.client.get(self.url, {"mutual": True})

        self.assertEqual(response.status_code, 200)
        following = response.json()
        self.assertEqual(len(following), 1)
        self.assertEqual(
            following[0],
            {
                "id": self.email_confirmed_user_three.pk,
                "first_name": self.email_confirmed_user_three.first_name,
                "last_name": self.email_confirmed_user_three.last_name,
                "email": self.email_confirmed_user_three.email,
                "is_mutual": True,
                "profile_picture": (
                    self.email_confirmed_user_three.profile_picture.url
                    if self.email_confirmed_user_three.profile_picture
                    else None
                ),
            },
        )

        # Search
        response = self.client.get(self.url, {"search": "Ana"})

        self.assertEqual(response.status_code, 200)
        following = response.json()
        self.assertEqual(len(following), 2)
        self.assertEqual(
            following[0],
            {
                "id": self.email_confirmed_user_three.pk,
                "first_name": self.email_confirmed_user_three.first_name,
                "last_name": self.email_confirmed_user_three.last_name,
                "email": self.email_confirmed_user_three.email,
                "is_mutual": True,
                "profile_picture": (
                    self.email_confirmed_user_three.profile_picture.url
                    if self.email_confirmed_user_three.profile_picture
                    else None
                ),
            },
        )
        self.assertEqual(
            following[1],
            {
                "id": self.email_confirmed_user_two.pk,
                "first_name": self.email_confirmed_user_two.first_name,
                "last_name": self.email_confirmed_user_two.last_name,
                "email": self.email_confirmed_user_two.email,
                "is_mutual": False,
                "profile_picture": (
                    self.email_confirmed_user_two.profile_picture.url
                    if self.email_confirmed_user_two.profile_picture
                    else None
                ),
            },
        )

        # Pagination
        response = self.client.get(self.url, {"page": 1, "page_size": 1})

        self.assertEqual(response.status_code, 200)
        res = response.json()
        self.assertEqual(res["count"], 3)
        self.assertIn("page=2", res["next"])
        self.assertIsNone(res["previous"])
        self.assertEqual(
            res["results"][0],
            {
                "id": self.active_user.pk,
                "first_name": self.active_user.first_name,
                "last_name": self.active_user.last_name,
                "email": self.active_user.email,
                "is_mutual": False,
                "profile_picture": (
                    self.active_user.profile_picture.url
                    if self.active_user.profile_picture
                    else None
                ),
            },
        )


class FollowViewTests(APITestCase):
    def setUp(self):
        user_data = {
            "email": "user@example.com",
            "first_name": "user",
            "last_name": "user",
            "password": "testpass123",
        }
        self.user = cast(CustomUser, User.objects.create_user(**user_data))
        self.user.is_email_confirmed = True
        self.user.save()

        target_user_data = {
            "email": "target_user@example.com",
            "first_name": "target_user",
            "last_name": "target_user",
            "password": "testpass123",
        }
        self.target = cast(
            CustomUser, User.objects.create_user(**target_user_data)
        )
        self.client.force_authenticate(self.user)
        self.url = reverse("follow", args=[self.target.pk])

    def test_follow_user(self):
        response = self.client.post(self.url, {"follow": True})

        self.assertEqual(response.status_code, 200)
        self.assertTrue(
            Follow.objects.filter(
                follower=self.user, followed=self.target
            ).exists()
        )
        self.assertEqual(response.json()["detail"], "Now following.")

    def test_follow_user_already_following(self):
        Follow.objects.create(follower=self.user, followed=self.target)

        response = self.client.post(self.url, {"follow": True})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["detail"], "Already following.")

    def test_unfollow_user(self):
        Follow.objects.create(follower=self.user, followed=self.target)

        response = self.client.post(self.url, {"follow": False})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["detail"], "Unfollowed.")
        self.assertFalse(
            Follow.objects.filter(
                follower=self.user, followed=self.target
            ).exists()
        )

    def test_unfollow_not_following(self):
        response = self.client.post(self.url, {"follow": False})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["detail"], "Was not following.")

    def test_cannot_follow_self(self):
        url = reverse("follow", args=[self.user.pk])

        response = self.client.post(url, {"follow": True})

        self.assertEqual(response.status_code, 400)
        self.assertIn("can't follow yourself", response.json()[0].lower())

    def test_user_not_found(self):
        url = reverse("follow", args=[9999])

        response = self.client.post(url, {"follow": True})

        self.assertEqual(response.status_code, 404)
