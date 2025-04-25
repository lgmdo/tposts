from django.urls import path

from .views import (
    ChangePasswordView,
    ConfirmSignUpView,
    LoginView,
    LogoutView,
    MyProfileView,
    ProfilePictureUploadView,
    SignUpView,
    UserListView,
    UserProfileView,
)

urlpatterns = [
    path(
        "change-password",
        ChangePasswordView.as_view(),
        name="change-password",
    ),
    path(
        "confirm-sign-up/<str:token>",
        ConfirmSignUpView.as_view(),
        name="confirm-sign-up",
    ),
    path("login", LoginView.as_view(), name="login"),
    path("logout", LogoutView.as_view(), name="logout"),
    path(
        "profile-picture",
        ProfilePictureUploadView.as_view(),
        name="profile-picture",
    ),
    path("sign-up", SignUpView.as_view(), name="sign-up"),
    path(
        "me",
        MyProfileView.as_view(),
        name="my-profile",
    ),
    path("", UserListView.as_view(), name="user-list"),
    path(
        "<str:uid>",
        UserProfileView.as_view(),
        name="user-profile",
    ),
]
