from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    class Role(models.TextChoices):
        ENTREPRENEUR = "entrepreneur", "Entrepreneur"
        MENTOR = "mentor", "Mentor"
        INVESTOR = "investor", "Investor"

    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.ENTREPRENEUR,
    )
    organization = models.CharField(max_length=150, blank=True)
    location = models.CharField(max_length=120, blank=True)
    bio = models.TextField(blank=True)

    def __str__(self):
        return f"{self.get_full_name() or self.username} ({self.get_role_display()})"
