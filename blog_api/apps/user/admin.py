from django.contrib import admin
from dajngo.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import User


# Register your models here.
@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ("email", "first_name", "last_name", "is_staff")

    search_fields = ("email", "first_name", "last_name")

    list_filter = ("is_staff", "is_active")

    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Personal info", {"fields": ("first_name", "last_name", "avatar")})(
            "Permissions", {"fields": ("is_active", "is_staff", "is_superuser")}
        )("Important dates", {"fields": ("date_joined")}),
    )

    readonly_fields = ("date_joined",)
    ordering = ("email",)
