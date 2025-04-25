from django.urls import path

from .views import (
    FollowingListView,
    FollowView,
)

urlpatterns = [
    path(
        "following",
        FollowingListView.as_view(),
        name="following",
    ),
    path(
        "following/<str:uid>",
        FollowView.as_view(),
        name="follow",
    ),
]
