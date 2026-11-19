from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models


class InvestorConnectionRequest(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        ACCEPTED = "accepted", "Accepted"
        DECLINED = "declined", "Declined"

    entrepreneur = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="sent_investor_requests",
    )
    investor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="received_investor_requests",
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
                fields=("entrepreneur", "investor"),
                name="unique_investor_connection_pair",
            )
        ]

    def clean(self):
        if self.entrepreneur_id and self.entrepreneur.role != "entrepreneur":
            raise ValidationError(
                {"entrepreneur": "Only entrepreneurs can initiate investor connections."}
            )
        if self.investor_id and self.investor.role != "investor":
            raise ValidationError(
                {"investor": "An investor connection request must be sent to an investor."}
            )
        if self.entrepreneur_id and self.entrepreneur_id == self.investor_id:
            raise ValidationError("A user cannot send a connection request to themselves.")

    def __str__(self):
        return f"{self.entrepreneur} → {self.investor} ({self.get_status_display()})"
