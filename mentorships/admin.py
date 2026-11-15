from django.contrib import admin

from .models import MentorshipRequest


@admin.register(MentorshipRequest)
class MentorshipRequestAdmin(admin.ModelAdmin):
    list_display = ("entrepreneur", "mentor", "status", "created_at")
    list_filter = ("status", "created_at")
    search_fields = (
        "entrepreneur__username",
        "entrepreneur__email",
        "mentor__username",
        "mentor__email",
    )
