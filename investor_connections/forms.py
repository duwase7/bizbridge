from django import forms

from .models import InvestorConnectionRequest


class InvestorConnectionRequestForm(forms.ModelForm):
    class Meta:
        model = InvestorConnectionRequest
        fields = ("message",)
        widgets = {
            "message": forms.Textarea(
                attrs={
                    "rows": 5,
                    "placeholder": "Introduce your business, its stage and what kind of investment or support you are seeking.",
                }
            )
        }

    def clean_message(self):
        message = self.cleaned_data["message"].strip()
        if not message:
            raise forms.ValidationError("Add a short introduction for the investor.")
        return message
