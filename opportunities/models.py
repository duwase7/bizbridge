from django.db import models


class Opportunity(models.Model):
    class Category(models.TextChoices):
        FUNDING = "funding", "Funding"
        TRAINING = "training", "Training"
        COMPETITION = "competition", "Competition"
        INCUBATOR = "incubator", "Incubator / accelerator"
        MENTORSHIP = "mentorship", "Mentorship"
        PARTNERSHIP = "partnership", "Partnership"
        OTHER = "other", "Other"

    title = models.CharField(max_length=180)
    provider = models.CharField(max_length=150)
    description = models.TextField()
    category = models.CharField(
        max_length=20,
        choices=Category.choices,
        default=Category.OTHER,
    )
    sector = models.CharField(max_length=120, blank=True)
    location = models.CharField(max_length=120, blank=True)
    deadline = models.DateField(blank=True, null=True)
    application_url = models.URLField(blank=True)
    is_active = models.BooleanField(default=True)
    view_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-created_at", "title")

    def __str__(self):
        return self.title

    @property
    def is_expired(self):
        from django.utils import timezone

        return bool(self.deadline and self.deadline < timezone.localdate())

    @classmethod
    def visible(cls):
        """Active opportunities whose deadline has not passed (FR-15, BR-07)."""
        from django.db.models import Q
        from django.utils import timezone

        return cls.objects.filter(is_active=True).filter(
            Q(deadline__isnull=True) | Q(deadline__gte=timezone.localdate())
        )
