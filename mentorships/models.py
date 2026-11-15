from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models


class MentorshipRequest(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        ACCEPTED = "accepted", "Accepted"
        DECLINED = "declined", "Declined"

    entrepreneur = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="sent_mentorship_requests",
    )
    mentor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="received_mentorship_requests",
    )
    message = models.TextField(max_length=1000)
    status = models.CharField(
        max_length=12,
        choices=Status.choices,
        default=Status.PENDING,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("-created_at",)
        constraints = [
            models.UniqueConstraint(
                fields=("entrepreneur", "mentor"),
                name="unique_mentorship_request_pair",
            )
        ]

    def clean(self):
        if self.entrepreneur_id and self.entrepreneur.role != "entrepreneur":
            raise ValidationError(
                {"entrepreneur": "Only entrepreneurs can send mentorship requests."}
            )
        if self.mentor_id and self.mentor.role != "mentor":
            raise ValidationError(
                {"mentor": "A mentorship request must be sent to a mentor."}
            )
        if self.entrepreneur_id and self.entrepreneur_id == self.mentor_id:
            raise ValidationError("A user cannot request mentorship from themselves.")

    def __str__(self):
        return f"{self.entrepreneur} → {self.mentor} ({self.get_status_display()})"
