from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q


class Connection(models.Model):
    """A request between two users that, once accepted, lets them message (FR-16, FR-17)."""

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        ACCEPTED = "accepted", "Accepted"
        DECLINED = "declined", "Declined"

    requester = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="sent_connections"
    )
    receiver = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="received_connections"
    )
    note = models.CharField(max_length=500, blank=True)
    status = models.CharField(max_length=12, choices=Status.choices, default=Status.PENDING)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("-updated_at",)
        constraints = [
            models.UniqueConstraint(fields=("requester", "receiver"), name="unique_connection_pair"),
            models.CheckConstraint(
                condition=~Q(requester=models.F("receiver")), name="connection_not_self"
            ),
        ]

    def clean(self):
        if self.requester_id and self.requester_id == self.receiver_id:
            raise ValidationError("You cannot connect with yourself.")

    def other(self, user):
        return self.receiver if user.pk == self.requester_id else self.requester

    def involves(self, user):
        return user.pk in (self.requester_id, self.receiver_id)

    @classmethod
    def between(cls, a, b):
        return cls.objects.filter(
            Q(requester=a, receiver=b) | Q(requester=b, receiver=a)
        ).first()

    @classmethod
    def for_user(cls, user):
        return cls.objects.filter(Q(requester=user) | Q(receiver=user))

    @classmethod
    def ensure_accepted(cls, a, b):
        """Accepted mentorships and investor introductions also open a connection."""
        connection = cls.between(a, b)
        if connection is None:
            return cls.objects.create(requester=a, receiver=b, status=cls.Status.ACCEPTED)
        if connection.status != cls.Status.ACCEPTED:
            connection.status = cls.Status.ACCEPTED
            connection.save(update_fields=("status", "updated_at"))
        return connection

    def __str__(self):
        return f"{self.requester} → {self.receiver} ({self.get_status_display()})"


class Message(models.Model):
    """A message between two connected users (FR-20, FR-21, BR-02)."""

    connection = models.ForeignKey(Connection, on_delete=models.CASCADE, related_name="messages")
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="sent_messages"
    )
    content = models.TextField(max_length=2000)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-created_at",)

    def __str__(self):
        return f"{self.sender}: {self.content[:40]}"
