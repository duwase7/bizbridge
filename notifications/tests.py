from django.test import TestCase
from django.urls import reverse

from accounts.models import User

from .models import Notification


class NotificationInboxTests(TestCase):
    def setUp(self):
        self.recipient = User.objects.create_user(
            username="recipient",
            password="StrongPass!2026",
            role=User.Role.ENTREPRENEUR,
        )
        self.other_user = User.objects.create_user(
            username="other",
            password="StrongPass!2026",
            role=User.Role.MENTOR,
        )

    def create_notification(self, recipient=None):
        return Notification.objects.create(
            recipient=recipient or self.recipient,
            actor=self.other_user,
            message="A new request update is available.",
            link=reverse("dashboard"),
        )

    def test_user_sees_only_their_own_notifications(self):
        self.create_notification()
        self.create_notification(recipient=self.other_user)
        self.client.force_login(self.recipient)

        response = self.client.get(reverse("notification_list"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "A new request update is available.")
        self.assertEqual(len(response.context["notifications"]), 1)

    def test_recipient_can_mark_notification_as_read(self):
        notification = self.create_notification()
        self.client.force_login(self.recipient)

        response = self.client.post(
            reverse("mark_notification_read", args=[notification.pk])
        )

        self.assertRedirects(response, reverse("notification_list"))
        notification.refresh_from_db()
        self.assertTrue(notification.is_read)

    def test_user_cannot_mark_another_users_notification_as_read(self):
        notification = self.create_notification(recipient=self.other_user)
        self.client.force_login(self.recipient)

        response = self.client.post(
            reverse("mark_notification_read", args=[notification.pk])
        )

        self.assertEqual(response.status_code, 404)
        notification.refresh_from_db()
        self.assertFalse(notification.is_read)

    def test_unread_count_is_shown_in_navigation(self):
        self.create_notification()
        self.client.force_login(self.recipient)

        response = self.client.get(reverse("dashboard"))

        self.assertContains(response, 'class="notification-count">1</span>')
