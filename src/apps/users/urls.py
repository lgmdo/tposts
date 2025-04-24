from django.urls import path

from .views import ConfirmSignUpView, SignUpView

urlpatterns = [
    path("sign-up", SignUpView.as_view(), name="sign-up"),
    path(
        "confirm-sign-up/<str:token>",
        ConfirmSignUpView.as_view(),
        name="sign-up",
    ),
]
