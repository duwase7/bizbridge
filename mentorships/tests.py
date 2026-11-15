from django.test import TestCase
from django.urls import reverse

from accounts.models import User

from .models import MentorshipRequest


class MentorshipRequestFlowTests(TestCase):
    def setUp(self):
        self.entrepreneur = User.objects.create_user(
            username="founder",
            password="StrongPass!2026",
            role=User.Role.ENTREPRENEUR,
        )
        self.mentor = User.objects.create_user(
            username="mentor",
            password="StrongPass!2026",
            first_name="Amina",
            last_name="Mentor",
            organization="Growth Partners",
            role=User.Role.MENTOR,
        )
        self.client.force_login(self.entrepreneur)

    def create_request(self, **overrides):
        values = {
            "entrepreneur": self.entrepreneur,
            "mentor": self.mentor,
            "message": "I would value guidance on growing my business.",
        }
        values.update(overrides)
        return MentorshipRequest.objects.create(**values)

    def test_mentor_directory_requires_login(self):
        self.client.logout()
        response = self.client.get(reverse("mentor_directory"))
        self.assertRedirects(
            response,
            f"{reverse('login')}?next={reverse('mentor_directory')}",
        )

    def test_entrepreneur_can_browse_mentors(self):
        response = self.client.get(reverse("mentor_directory"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Amina Mentor")
        self.assertContains(response, "Growth Partners")

    def test_entrepreneur_can_send_mentorship_request(self):
        response = self.client.post(
            reverse("request_mentorship", args=[self.mentor.pk]),
            {"message": "I need advice on validating my business model."},
        )

        self.assertRedirects(response, reverse("mentorship_requests"))
        mentorship_request = MentorshipRequest.objects.get()
        self.assertEqual(mentorship_request.entrepreneur, self.entrepreneur)
        self.assertEqual(mentorship_request.mentor, self.mentor)
        self.assertEqual(mentorship_request.status, MentorshipRequest.Status.PENDING)
        self.assertEqual(
            mentorship_request.message,
            "I need advice on validating my business model.",
        )

    def test_duplicate_pending_request_is_not_created(self):
        self.create_request()
        self.client.post(
            reverse("request_mentorship", args=[self.mentor.pk]),
            {"message": "A second request."},
        )
        self.assertEqual(MentorshipRequest.objects.count(), 1)
        self.assertEqual(
            MentorshipRequest.objects.get().status,
            MentorshipRequest.Status.PENDING,
        )

    def test_declined_request_can_be_resubmitted(self):
        mentorship_request = self.create_request(
            status=MentorshipRequest.Status.DECLINED
        )
        self.client.post(
            reverse("request_mentorship", args=[self.mentor.pk]),
            {"message": "I would like to try again with a clearer goal."},
        )
        mentorship_request.refresh_from_db()
        self.assertEqual(mentorship_request.status, MentorshipRequest.Status.PENDING)
        self.assertEqual(
            mentorship_request.message,
            "I would like to try again with a clearer goal.",
        )
        self.assertEqual(MentorshipRequest.objects.count(), 1)

    def test_mentor_can_accept_a_pending_request(self):
        mentorship_request = self.create_request()
        self.client.force_login(self.mentor)

        response = self.client.post(
            reverse("respond_to_mentorship_request", args=[mentorship_request.pk]),
            {"decision": MentorshipRequest.Status.ACCEPTED},
        )

        self.assertRedirects(response, reverse("mentorship_requests"))
        mentorship_request.refresh_from_db()
        self.assertEqual(mentorship_request.status, MentorshipRequest.Status.ACCEPTED)

    def test_mentor_can_reject_a_pending_request(self):
        mentorship_request = self.create_request()
        self.client.force_login(self.mentor)

        self.client.post(
            reverse("respond_to_mentorship_request", args=[mentorship_request.pk]),
            {"decision": MentorshipRequest.Status.DECLINED},
        )

        mentorship_request.refresh_from_db()
        self.assertEqual(mentorship_request.status, MentorshipRequest.Status.DECLINED)

    def test_only_the_assigned_mentor_can_respond(self):
        other_mentor = User.objects.create_user(
            username="othermentor",
            password="StrongPass!2026",
            role=User.Role.MENTOR,
        )
        mentorship_request = self.create_request()
        self.client.force_login(other_mentor)

        response = self.client.post(
            reverse("respond_to_mentorship_request", args=[mentorship_request.pk]),
            {"decision": MentorshipRequest.Status.ACCEPTED},
        )

        self.assertEqual(response.status_code, 404)
        mentorship_request.refresh_from_db()
        self.assertEqual(mentorship_request.status, MentorshipRequest.Status.PENDING)

    def test_entrepreneur_cannot_respond_to_a_request(self):
        mentorship_request = self.create_request()

        response = self.client.post(
            reverse("respond_to_mentorship_request", args=[mentorship_request.pk]),
            {"decision": MentorshipRequest.Status.ACCEPTED},
        )

        self.assertRedirects(response, reverse("dashboard"))
        mentorship_request.refresh_from_db()
        self.assertEqual(mentorship_request.status, MentorshipRequest.Status.PENDING)

    def test_investor_cannot_send_a_mentorship_request(self):
        investor = User.objects.create_user(
            username="investor",
            password="StrongPass!2026",
            role=User.Role.INVESTOR,
        )
        self.client.force_login(investor)

        response = self.client.post(
            reverse("request_mentorship", args=[self.mentor.pk]),
            {"message": "Please mentor me."},
        )

        self.assertRedirects(response, reverse("dashboard"))
        self.assertEqual(MentorshipRequest.objects.count(), 0)

    def test_mentor_sees_received_requests(self):
        self.create_request()
        self.client.force_login(self.mentor)

        response = self.client.get(reverse("mentorship_requests"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "founder")
        self.assertContains(response, "I would value guidance on growing my business.")

    def test_entrepreneur_sees_sent_request_status(self):
        self.create_request()

        response = self.client.get(reverse("mentorship_requests"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Amina Mentor")
        self.assertContains(response, "Pending")
