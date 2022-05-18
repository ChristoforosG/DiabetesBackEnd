from django.contrib import admin
from .models import Users
from django.contrib.auth.admin import UserAdmin


class UserAdminConfig(UserAdmin):
    ordering = ("-registration_date",)
    list_filter = ("email", "user_name", "first_name")
    list_display = (
        "pk",
        "email",
        "user_name",
        "first_name",
        "is_active",
        "is_staff",
        "gender",
        "date_of_birth",
        "is_in_insulin_therapy",
        "first_login",
        "registration_date",
    )
    fieldsets = (
        (None, {"fields": ("email", "user_name")}),
        ("Permissions", {"fields": ("is_staff", "is_active")}),
        (
            "Personal",
            {
                "fields": (
                    "first_name",
                    "gender",
                    "date_of_birth",
                    "is_in_insulin_therapy",
                    "first_login",
                )
            },
        ),
    )


admin.site.register(Users, UserAdminConfig)
