from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ("BizBridge profile", {"fields": ("role", "organization", "location", "bio")}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ("BizBridge profile", {"fields": ("role", "organization", "location")}),
    )
    list_display = ("username", "email", "first_name", "last_name", "role", "is_staff")
    list_filter = ("role", "is_staff", "is_active")
