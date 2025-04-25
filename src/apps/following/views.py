from typing import cast

from django.contrib.auth import get_user_model
from django.db.models import Case, F, Value, When
from django.db.models.functions import Concat
from django.shortcuts import get_object_or_404
from rest_framework import generics
from rest_framework.exceptions import ValidationError
from rest_framework.filters import SearchFilter
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.users.models import CustomUser
from apps.utils.paginations import CustomPagination

from ..utils.permissions import IsEmailConfirmed
from .models import Follow
from .serializers import (
    FollowedUsersSerializer,
    FollowingListQueryParamsSerializer,
    FollowSerializer,
)
from .swagger import follow_schema, following_list_schema

User = get_user_model()


class FollowView(APIView):
    permission_classes = [IsEmailConfirmed]

    @follow_schema
    def post(self, request: Request, uid: int):
        serializer = FollowSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        target_user = get_object_or_404(CustomUser, pk=uid)
        is_follow = serializer.validated_data["follow"]

        if target_user == request.user:
            raise ValidationError("You can't follow yourself.")

        if is_follow:
            _, created = Follow.objects.get_or_create(
                follower=request.user,
                followed=target_user,
            )
            return Response(
                {
                    "detail": "Now following."
                    if created
                    else "Already following."
                }
            )
        else:
            deleted, _ = Follow.objects.filter(
                follower=request.user,
                followed=target_user,
            ).delete()
            return Response(
                {"detail": "Unfollowed." if deleted else "Was not following."}
            )


@following_list_schema
class FollowingListView(generics.ListAPIView):
    serializer_class = FollowedUsersSerializer
    permission_classes = [IsEmailConfirmed]
    filter_backends = [SearchFilter]
    pagination_class = CustomPagination
    search_fields = ["first_name", "last_name"]

    def get_queryset(self):
        user = self.request.user
        query_params_serializer = FollowingListQueryParamsSerializer(
            data=self.request.query_params
        )
        if not query_params_serializer.is_valid():
            raise ValidationError(query_params_serializer.errors)
        validated_query_params = query_params_serializer.data

        qs = Follow.objects.filter(follower=user).annotate(
            full_name=Concat(
                F("followed__first_name"), Value(" "), F("followed__last_name")
            )
        )

        if validated_query_params["mutual"]:
            qs = qs.filter(followed__following__followed=user)

        if (
            cast(
                FollowingListQueryParamsSerializer.OrderingType,
                validated_query_params["ordering_type"],
            )
            == FollowingListQueryParamsSerializer.OrderingType.NAME
        ):
            qs = qs.order_by("full_name")

        followed_ids = qs.values_list("followed__id", flat=True)

        preserved_order = Case(
            *[When(pk=pk, then=pos) for pos, pk in enumerate(followed_ids)]
        )
        return CustomUser.objects.filter(id__in=followed_ids).order_by(
            preserved_order
        )
