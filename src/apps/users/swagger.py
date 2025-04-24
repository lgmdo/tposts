from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import (
    OpenApiParameter,
    OpenApiResponse,
    extend_schema,
)

from .serializers import SignUpSerializer

sign_up_schema = extend_schema(
    summary="User sign-up",
    request=SignUpSerializer(),
    responses={
        204: OpenApiResponse(
            response=None,
            description=(
                "Cadastro realizado com sucesso. Verifique seu email "
                "para confirmar o cadastro."
            ),
        ),
        400: OpenApiResponse(
            response=None, description="Dados inválidos para cadastro."
        ),
    },
    tags=["Authentication"],
)

confirm_sign_up_schema = extend_schema(
    summary="Confirm user registration",
    parameters=[
        OpenApiParameter(
            name="token",
            description="Token received in email.",
            location=OpenApiParameter.PATH,
            type=OpenApiTypes.STR,
            required=True,
        )
    ],
    responses={
        204: OpenApiResponse(
            response=None,
            description=(
                "Email confirmado com sucesso ou usuário já confirmado."
            ),
        ),
        400: OpenApiResponse(
            response=None,
            description="Token inválido ou malformado.",
        ),
        404: OpenApiResponse(
            response=None,
            description="Usuário não encontrado com base no token.",
        ),
    },
    tags=["Authentication"],
)
