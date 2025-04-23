from django.contrib import admin

from apps.users.models import CustomUser


class UserAdmin(admin.ModelAdmin):  # type: ignore[type-arg]
    list_display = [
        "email",
        "first_name",
        "last_name",
        "is_active",
        "is_staff",
        "profile_picture",
    ]


admin.site.register(CustomUser, UserAdmin)
