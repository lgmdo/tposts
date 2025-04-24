from django.urls import path

from .views import ConfirmSignUpView, LoginView, LogoutView, SignUpView

urlpatterns = [
    path(
        "confirm-sign-up/<str:token>",
        ConfirmSignUpView.as_view(),
        name="confirm-sign-up",
    ),
    path("login", LoginView.as_view(), name="login"),
    path("logout", LogoutView.as_view(), name="logout"),
    path("sign-up", SignUpView.as_view(), name="sign-up"),
]
