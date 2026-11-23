from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend


class EmailOrUsernameBackend(ModelBackend):
    """Let members log in with their email address or username (FR-03)."""

    def authenticate(self, request, username=None, password=None, **kwargs):
        if username and "@" in username:
            User = get_user_model()
            match = User.objects.filter(email__iexact=username.strip()).order_by("pk").first()
            if match:
                username = match.get_username()
        return super().authenticate(request, username=username, password=password, **kwargs)
