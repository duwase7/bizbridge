from django import forms

from opportunities.models import Opportunity


class OpportunityForm(forms.ModelForm):
    class Meta:
        model = Opportunity
        fields = (
            "title", "category", "provider", "description", "sector",
            "location", "deadline", "application_url", "is_active",
        )
        widgets = {
            "description": forms.Textarea(attrs={"rows": 5}),
            "deadline": forms.DateInput(attrs={"type": "date"}),
        }
        help_texts = {
            "sector": 'Use "All sectors" if the opportunity is open to every sector.',
            "deadline": "Leave empty for rolling opportunities. Expired opportunities are hidden automatically.",
        }
