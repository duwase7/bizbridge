from django.test import TestCase
from django.urls import reverse

from accounts.models import User
from mentorships.models import MentorshipRequest
from notifications.models import Notification

from .models import Connection, Message

PASSWORD = "StrongPass!2026"


class ConnectionAndMessagingTests(TestCase):
    def setUp(self):
        self.founder = User.objects.create_user(username="founder", first_name="Aline", password=PASSWORD, role=User.Role.ENTREPRENEUR)
        self.partner = User.objects.create_user(username="partner", first_name="Jean", password=PASSWORD, role=User.Role.ENTREPRENEUR)
        self.mentor = User.objects.create_user(username="mentor", first_name="Maya", password=PASSWORD, role=User.Role.MENTOR)
        self.outsider = User.objects.create_user(username="outsider", password=PASSWORD, role=User.Role.ENTREPRENEUR)

    def send(self, sender, receiver, note="Hello"):
        self.client.force_login(sender)
        return self.client.post(reverse("send_connection_request", args=[receiver.pk]), {"note": note})

    def test_send_request_creates_pending_connection_and_notification(self):
        self.send(self.founder, self.partner)
        connection = Connection.objects.get()
        self.assertEqual(connection.status, Connection.Status.PENDING)
        self.assertTrue(Notification.objects.filter(recipient=self.partner).exists())

    def test_duplicate_and_self_requests_are_blocked(self):
        self.send(self.founder, self.partner)
        self.send(self.founder, self.partner)
        self.send(self.partner, self.founder)
        self.assertEqual(Connection.objects.count(), 1)
        self.client.force_login(self.founder)
        self.client.post(reverse("send_connection_request", args=[self.founder.pk]))
        self.assertEqual(Connection.objects.count(), 1)

    def test_receiver_accepts_and_requester_is_notified(self):
        self.send(self.founder, self.partner)
        connection = Connection.objects.get()
        self.client.force_login(self.partner)
        self.client.post(reverse("respond_to_connection", args=[connection.pk]), {"decision": "accepted"})
        connection.refresh_from_db()
        self.assertEqual(connection.status, Connection.Status.ACCEPTED)
        self.assertTrue(Notification.objects.filter(recipient=self.founder, message__contains="accepted").exists())

    def test_requester_cannot_answer_own_request(self):
        self.send(self.founder, self.partner)
        connection = Connection.objects.get()
        response = self.client.post(reverse("respond_to_connection", args=[connection.pk]), {"decision": "accepted"})
        self.assertEqual(response.status_code, 404)

    def test_messaging_requires_accepted_connection(self):
        self.send(self.founder, self.partner)
        connection = Connection.objects.get()
        self.client.post(reverse("conversation", args=[connection.pk]), {"content": "Hi"})
        self.assertEqual(Message.objects.count(), 0)

        connection.status = Connection.Status.ACCEPTED
        connection.save()
        self.client.post(reverse("conversation", args=[connection.pk]), {"content": "Hi there"})
        self.assertEqual(Message.objects.count(), 1)
        self.assertTrue(Notification.objects.filter(recipient=self.partner, message__contains="New message").exists())

    def test_outsider_cannot_read_conversation(self):
        connection = Connection.objects.create(requester=self.founder, receiver=self.partner, status="accepted")
        Message.objects.create(connection=connection, sender=self.founder, content="secret plan")
        self.client.force_login(self.outsider)
        response = self.client.get(reverse("conversation", args=[connection.pk]), follow=True)
        self.assertNotContains(response, "secret plan")

    def test_message_history_newest_first_and_marked_read(self):
        connection = Connection.objects.create(requester=self.founder, receiver=self.partner, status="accepted")
        Message.objects.create(connection=connection, sender=self.founder, content="first message")
        Message.objects.create(connection=connection, sender=self.founder, content="second message")
        self.client.force_login(self.partner)
        response = self.client.get(reverse("conversation", args=[connection.pk]))
        body = response.content.decode()
        self.assertLess(body.index("second message"), body.index("first message"))
        self.assertFalse(Message.objects.filter(is_read=False).exists())

    def test_accepted_mentorship_opens_a_connection(self):
        request = MentorshipRequest.objects.create(entrepreneur=self.founder, mentor=self.mentor, message="Help with marketing")
        self.client.force_login(self.mentor)
        self.client.post(reverse("respond_to_mentorship_request", args=[request.pk]), {"decision": "accepted"})
        connection = Connection.between(self.founder, self.mentor)
        self.assertEqual(connection.status, Connection.Status.ACCEPTED)
        response = self.client.get(reverse("inbox"))
        self.assertContains(response, "Aline")
