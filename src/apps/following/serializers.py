from enum import Enum

from django.contrib.auth import get_user_model
from rest_framework import serializers

from apps.users.models import CustomUser

User = get_user_model()


class FollowedUsersSerializer(serializers.ModelSerializer):
    is_mutual = serializers.SerializerMethodField()

    class Meta:  # pyright: ignore
        model = User
        fields = (
            "id",
            "first_name",
            "last_name",
            "email",
            "is_mutual",
            "profile_picture",
        )

    def get_is_mutual(self, obj: CustomUser) -> bool:
        request_user = self.context["request"].user
        return request_user.followers.filter(follower=obj).exists()  # pyright: ignore


class FollowingListQueryParamsSerializer(serializers.Serializer):
    class OrderingType(str, Enum):
        CREATION = "creation"
        NAME = "name"

    mutual = serializers.BooleanField(required=False, default=False)
    ordering_type = serializers.ChoiceField(
        choices=OrderingType,
        required=False,
        default=OrderingType.CREATION,
    )
    search = serializers.CharField(required=False, max_length=100)


class FollowSerializer(serializers.Serializer):
    follow = serializers.BooleanField()
