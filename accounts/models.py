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

    # Entrepreneur details (SRS FR-07)
    business_name = models.CharField(max_length=150, blank=True)
    business_sector = models.CharField(max_length=120, blank=True)
    business_stage = models.CharField(max_length=80, blank=True)
    business_description = models.TextField(blank=True)

    # Mentor details (SRS FR-08)
    mentor_expertise = models.CharField(max_length=200, blank=True)
    mentor_availability = models.CharField(max_length=120, blank=True)

    # Investor details (SRS FR-09)
    investor_type = models.CharField(max_length=80, blank=True)
    website = models.URLField(blank=True)

    def __str__(self):
        return f"{self.get_full_name() or self.username} ({self.get_role_display()})"
