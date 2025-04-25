from typing import cast

from rest_framework.permissions import BasePermission
from rest_framework.request import Request
from rest_framework.views import APIView

from apps.users.models import CustomUser


class IsEmailConfirmed(BasePermission):
    """
    Permission that allows access only to users with a confirmed email
    (is_active=True).
    """

    def has_permission(self, request: Request, view: APIView):
        user = cast(CustomUser, request.user)
        return user and user.is_authenticated and user.is_email_confirmed
