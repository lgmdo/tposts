from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import (
    OpenApiParameter,
    OpenApiResponse,
    extend_schema,
)

from .serializers import (
    LoginSerializer,
    ProfilePictureUploadSerializer,
    SignUpSerializer,
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
