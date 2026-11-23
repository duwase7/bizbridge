from django import forms

from .models import Message


class ConnectionRequestForm(forms.Form):
    note = forms.CharField(
        label="Add a short note (optional)",
        max_length=500,
        required=False,
        widget=forms.Textarea(attrs={"rows": 3, "placeholder": "Say why you would like to connect."}),
    )


class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ("content",)
        labels = {"content": "Your message"}
        widgets = {"content": forms.Textarea(attrs={"rows": 3, "placeholder": "Write a message..."})}

    def clean_content(self):
        content = self.cleaned_data["content"].strip()
        if not content:
            raise forms.ValidationError("Message cannot be empty.")
        return content
