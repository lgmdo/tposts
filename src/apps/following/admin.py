from django.contrib import admin

from .models import Follow


class FollowAdmin(admin.ModelAdmin):  # pyright: ignore
    list_display = (
        "follower",
        "followed",
        "created_at",
    )
    list_filter = ("created_at",)
    search_fields = (
        "follower__email",
        "followed__email",
    )

    ordering = ("-created_at",)


admin.site.register(Follow, FollowAdmin)
