from django.contrib import admin

from .models import Opportunity


@admin.register(Opportunity)
class OpportunityAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "provider",
        "category",
        "location",
        "deadline",
        "is_active",
    )
    list_filter = ("category", "is_active", "location")
    search_fields = ("title", "provider", "description", "sector", "location")
    list_editable = ("is_active",)
    ordering = ("-created_at",)
