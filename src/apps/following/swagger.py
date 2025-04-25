from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import (
    OpenApiParameter,
    OpenApiResponse,
    extend_schema,
)

from .serializers import (
    FollowedUsersSerializer,
    FollowingListQueryParamsSerializer,
    FollowSerializer,
)

following_list_schema = extend_schema(
    methods=["GET"],
    parameters=[
        OpenApiParameter(
            "mutual",
            type=OpenApiTypes.BOOL,
            description="Filter by mutual followers",
        ),
        OpenApiParameter(
            "ordering_type",
            type=OpenApiTypes.STR,
            enum=[
                e.value
                for e in FollowingListQueryParamsSerializer.OrderingType
            ],
            description="Sorting type: 'name' or 'created_at'",
        ),
        OpenApiParameter(
            "search",
            type=OpenApiTypes.STR,
            description="Search by first or last name",
        ),
    ],
    responses={200: FollowedUsersSerializer(many=True)},
    tags=["Following"],
)

follow_schema = extend_schema(
    request=FollowSerializer,
    responses={
        200: OpenApiResponse(description="Follow status updated."),
        400: OpenApiResponse(
            description="Invalid request or trying to follow yourself."
        ),
        404: OpenApiResponse(description="Target user not found."),
    },
    parameters=[
        OpenApiParameter(
            name="uid",
            description="ID of the user to follow/unfollow",
            required=True,
            type=int,
            location=OpenApiParameter.PATH,
        )
    ],
    description=(
        "Follow or unfollow a user based on the `follow` boolean in the "
        "payload."
    ),
    summary="Toggle follow status",
    tags=["Following"],
)
