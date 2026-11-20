from django import forms
from django.contrib.auth.forms import UserCreationForm

from .models import User


class SignUpForm(UserCreationForm):
    first_name = forms.CharField(max_length=150)
    last_name = forms.CharField(max_length=150)
    email = forms.EmailField()
    role = forms.ChoiceField(choices=User.Role.choices)
    organization = forms.CharField(max_length=150, required=False)
    location = forms.CharField(max_length=120, required=False)

    class Meta:
        model = User
        fields = (
            "username",
            "first_name",
            "last_name",
            "email",
            "role",
            "organization",
            "location",
            "password1",
            "password2",
        )

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("An account with this email already exists.")
        return email


class ProfileForm(forms.ModelForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = (
            "first_name",
            "last_name",
            "email",
            "organization",
            "location",
            "bio",
            "business_name",
            "business_sector",
            "business_stage",
            "business_description",
            "mentor_expertise",
            "mentor_availability",
            "investor_type",
            "website",
        )
        widgets = {
            "bio": forms.Textarea(attrs={"rows": 4}),
            "business_description": forms.Textarea(attrs={"rows": 4}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        role = self.instance.role
        role_fields = {
            User.Role.ENTREPRENEUR: (
                "business_name",
                "business_sector",
                "business_stage",
                "business_description",
            ),
            User.Role.MENTOR: ("mentor_expertise", "mentor_availability"),
            User.Role.INVESTOR: ("investor_type", "website"),
        }
        visible_fields = set(role_fields.get(role, ()))
        all_role_fields = {
            "business_name",
            "business_sector",
            "business_stage",
            "business_description",
            "mentor_expertise",
            "mentor_availability",
            "investor_type",
            "website",
        }
        for field_name in all_role_fields - visible_fields:
            self.fields.pop(field_name)

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()
        existing_users = User.objects.filter(email__iexact=email).exclude(
            pk=self.instance.pk
        )
        if existing_users.exists():
            raise forms.ValidationError("An account with this email already exists.")
        return email
