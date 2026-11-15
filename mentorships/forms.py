from django import forms

from .models import MentorshipRequest


class MentorshipRequestForm(forms.ModelForm):
    class Meta:
        model = MentorshipRequest
        fields = ("message",)
        widgets = {
            "message": forms.Textarea(
                attrs={
                    "rows": 5,
                    "placeholder": "Introduce your business and explain the guidance you are looking for.",
                }
            )
        }

    def clean_message(self):
        message = self.cleaned_data["message"].strip()
        if not message:
            raise forms.ValidationError("Add a short message to your mentor.")
        return message
