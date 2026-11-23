from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ("BizBridge profile", {"fields": ("role", "is_verified", "organization", "location", "bio", "interest_sectors")}),
        (
            "Entrepreneur details",
            {"fields": ("business_name", "business_sector", "business_stage", "business_description")},
        ),
        (
            "Mentor details",
            {"fields": ("mentor_expertise", "mentor_availability")},
        ),
        (
            "Investor details",
            {"fields": ("investor_type", "website")},
        ),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ("BizBridge profile", {"fields": ("role", "organization", "location")}),
    )
    list_display = ("username", "email", "first_name", "last_name", "role", "is_verified", "is_active", "is_staff")
    list_filter = ("role", "is_verified", "is_staff", "is_active")
