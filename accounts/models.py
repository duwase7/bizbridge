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

    # Administrator verification of mentor/investor profiles (FR-25, NFR-04)
    is_verified = models.BooleanField(default=False)

    # Mentor and investor matching (SRS FR-10 to FR-12)
    interest_sectors = models.CharField(
        "Sectors of interest",
        max_length=200,
        blank=True,
        help_text="Comma-separated sectors you support, e.g. Agriculture, Fintech.",
    )

    @property
    def display_name(self):
        return self.get_full_name() or self.username

    @property
    def sector_label(self):
        if self.role == self.Role.ENTREPRENEUR:
            return self.business_sector
        return self.interest_sectors

    def __str__(self):
        return f"{self.get_full_name() or self.username} ({self.get_role_display()})"
