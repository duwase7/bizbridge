from django.contrib import admin

from .models import InvestorConnectionRequest


@admin.register(InvestorConnectionRequest)
class InvestorConnectionRequestAdmin(admin.ModelAdmin):
    list_display = ("entrepreneur", "investor", "status", "created_at", "updated_at")
    list_filter = ("status", "created_at")
    search_fields = (
        "entrepreneur__username",
        "entrepreneur__organization",
        "investor__username",
        "investor__organization",
    )
    readonly_fields = ("created_at", "updated_at")
