from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import (
    OpenApiParameter,
    OpenApiResponse,
    extend_schema,
)

from .serializers import (
    LoginSerializer,
    MyProfileSerializer,
    PasswordChangeSerializer,
    ProfilePictureUploadSerializer,
    SignUpSerializer,
    UserListQueryParamsSerializer,
    UserProfileSerializer,
)

sign_up_schema = extend_schema(
    summary="User sign-up",
    request=SignUpSerializer(),
    responses={
        204: OpenApiResponse(
            response=None,
            description=(
                "Registration successful. Check your email "
                "to confirm your account."
            ),
        ),
        400: OpenApiResponse(
            response=None, description="Invalid data for registration."
        ),
    },
    tags=["Authentication"],
)

confirm_sign_up_schema = extend_schema(
    summary="Confirm user registration",
    parameters=[
        OpenApiParameter(
            name="token",
            description="Token received via email.",
            location=OpenApiParameter.PATH,
            type=OpenApiTypes.STR,
            required=True,
        )
    ],
    responses={
        204: OpenApiResponse(
            response=None,
            description=(
                "Email successfully confirmed or user already confirmed."
            ),
        ),
        400: OpenApiResponse(
            response=None,
            description="Invalid or malformed token.",
        ),
        404: OpenApiResponse(
            response=None,
            description="User not found for the given token.",
        ),
    },
    tags=["Authentication"],
)

login_schema = extend_schema(
    summary="Logs in user",
    request=LoginSerializer(),
    responses={
        200: OpenApiResponse(
            description=("Login successfull"),
        ),
    },
    tags=["Authentication"],
)


logout_schema = extend_schema(
    summary="Logs out user",
    request=None,
    responses={
        204: OpenApiResponse(
            description=("Logout successfull"),
        ),
        401: OpenApiResponse(
            description=("Unauthorized."),
        ),
    },
    tags=["Authentication"],
)

profile_picture_schema = extend_schema(
    methods=["PUT"],
    request=ProfilePictureUploadSerializer(),
    responses={
        200: OpenApiResponse(
            description="Public url of the profile picture.",
            response={"url": "picture_url"},
        ),
        400: OpenApiResponse(
            description="Validation error for the submitted data"
        ),
    },
    description=(
        "Uploads a profile picture to S3 and returns the public image URL."
    ),
    summary="Profile picture upload",
    tags=["Users"],
)

change_password_schema = extend_schema(
    methods=["POST"],
    request=PasswordChangeSerializer,
    responses={
        200: OpenApiTypes.OBJECT,
        400: OpenApiTypes.OBJECT,
    },
    description="Change the current authenticated user's password.",
    summary="Change password",
    tags=["Authentication"],
)

profile_schema = extend_schema(
    description="Retrieve the public profile of a user by UID.",
    responses={200: UserProfileSerializer},
    parameters=[
        OpenApiParameter(
            name="uid",
            type=OpenApiTypes.INT,
            location=OpenApiParameter.PATH,
            description="ID of the user whose profile is being requested.",
            required=True,
        )
    ],
    tags=["Users"],
)

my_profile_schema = extend_schema(
    description="Retrieve the public profile of authenticacted user.",
    responses={200: MyProfileSerializer},
    tags=["Users"],
)

users_list_schema = extend_schema(
    parameters=[
        OpenApiParameter(
            name="search",
            type=OpenApiTypes.STR,
            location=OpenApiParameter.QUERY,
            description="Search by user's full name",
        ),
        OpenApiParameter(
            name="ordering_type",
            type=OpenApiTypes.STR,
            location=OpenApiParameter.QUERY,
            enum=[e.value for e in UserListQueryParamsSerializer.OrderingType],
            description='Ordering option: "name" or "followers_count"',
            required=False,
        ),
        OpenApiParameter(
            name="is_following_you",
            type=OpenApiTypes.BOOL,
            location=OpenApiParameter.QUERY,
            description="Filter users who follow you",
            required=False,
        ),
        OpenApiParameter(
            name="page",
            type=OpenApiTypes.INT,
            location=OpenApiParameter.QUERY,
            description="Page number for pagination (optional)",
            required=False,
        ),
        OpenApiParameter(
            name="page_size",
            type=OpenApiTypes.INT,
            location=OpenApiParameter.QUERY,
            description="Page size for pagination (optional)",
            required=False,
        ),
    ],
    tags=["Users"],
)
