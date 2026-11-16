import os

from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = "Create the first hosted admin account when bootstrap credentials are configured."

    def handle(self, *args, **options):
        username = os.getenv("DJANGO_SUPERUSER_USERNAME", "").strip()
        email = os.getenv("DJANGO_SUPERUSER_EMAIL", "").strip()
        password = os.getenv("DJANGO_SUPERUSER_PASSWORD", "")

        if not username or not email or not password:
            self.stdout.write(
                "Skipping admin bootstrap: set all DJANGO_SUPERUSER_* variables to enable it."
            )
            return

        User = get_user_model()
        if User.objects.filter(username=username).exists():
            self.stdout.write(
                f"Admin bootstrap skipped: username '{username}' already exists; no changes made."
            )
            return

        try:
            validate_password(password)
        except ValidationError as error:
            raise CommandError(
                "The bootstrap password does not meet Django's password requirements: "
                + "; ".join(error.messages)
            ) from error

        User.objects.create_superuser(
            username=username,
            email=email,
            password=password,
        )
        self.stdout.write(self.style.SUCCESS("Bootstrap admin account created."))
