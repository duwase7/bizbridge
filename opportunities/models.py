from django.db import models


class Opportunity(models.Model):
    class Category(models.TextChoices):
        FUNDING = "funding", "Funding"
        TRAINING = "training", "Training"
        COMPETITION = "competition", "Competition"
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
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-created_at", "title")

    def __str__(self):
        return self.title
