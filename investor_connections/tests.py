from django.test import TestCase
from django.urls import reverse

from accounts.models import User
from notifications.models import Notification

from .models import InvestorConnectionRequest


class InvestorConnectionFlowTests(TestCase):
    def setUp(self):
        self.entrepreneur = User.objects.create_user(
            username="founder",
            password="StrongPass!2026",
            first_name="Amina",
            last_name="Founder",
            organization="Green Start",
            role=User.Role.ENTREPRENEUR,
        )
        self.investor = User.objects.create_user(
            username="investor",
            password="StrongPass!2026",
            first_name="Eric",
            last_name="Investor",
            organization="Impact Capital",
            location="Kigali",
            bio="Supporting early-stage climate and agriculture ventures.",
            role=User.Role.INVESTOR,
        )
        self.client.force_login(self.entrepreneur)

    def create_request(self, **overrides):
        values = {
            "entrepreneur": self.entrepreneur,
            "investor": self.investor,
            "message": "We are seeking investment to expand our sustainable agriculture business.",
        }
        values.update(overrides)
        return InvestorConnectionRequest.objects.create(**values)

    def test_investor_directory_requires_login(self):
        self.client.logout()
        response = self.client.get(reverse("investor_directory"))
        self.assertRedirects(
            response,
            f"{reverse('login')}?next={reverse('investor_directory')}",
        )

    def test_entrepreneur_can_browse_investors(self):
        response = self.client.get(reverse("investor_directory"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Eric Investor")
        self.assertContains(response, "Impact Capital")

    def test_investor_directory_can_be_searched(self):
        User.objects.create_user(
            username="secondinvestor",
            password="StrongPass!2026",
            organization="Rwanda Growth Fund",
            role=User.Role.INVESTOR,
        )
        response = self.client.get(reverse("investor_directory"), {"q": "Growth"})
        self.assertContains(response, "Rwanda Growth Fund")
        self.assertNotContains(response, "Impact Capital")

    def test_non_entrepreneur_cannot_browse_investors(self):
        mentor = User.objects.create_user(
            username="mentor",
            password="StrongPass!2026",
            role=User.Role.MENTOR,
        )
        self.client.force_login(mentor)
        response = self.client.get(reverse("investor_directory"))
        self.assertRedirects(response, reverse("dashboard"))

    def test_entrepreneur_can_send_investor_request(self):
        response = self.client.post(
            reverse("request_investor_connection", args=[self.investor.pk]),
            {"message": "We are looking for seed funding for our business."},
        )
        self.assertRedirects(response, reverse("investor_connection_requests"))
        connection_request = InvestorConnectionRequest.objects.get()
        self.assertEqual(connection_request.entrepreneur, self.entrepreneur)
        self.assertEqual(connection_request.investor, self.investor)
        self.assertEqual(connection_request.status, InvestorConnectionRequest.Status.PENDING)
        notification = Notification.objects.get(recipient=self.investor)
        self.assertEqual(notification.actor, self.entrepreneur)
        self.assertIn("investor connection request", notification.message)

    def test_duplicate_pending_request_is_not_created(self):
        self.create_request()
        self.client.post(
            reverse("request_investor_connection", args=[self.investor.pk]),
            {"message": "A second request."},
        )
        self.assertEqual(InvestorConnectionRequest.objects.count(), 1)
        self.assertEqual(
            InvestorConnectionRequest.objects.get().status,
            InvestorConnectionRequest.Status.PENDING,
        )

    def test_declined_request_can_be_resubmitted(self):
        connection_request = self.create_request(
            status=InvestorConnectionRequest.Status.DECLINED
        )
        self.client.post(
            reverse("request_investor_connection", args=[self.investor.pk]),
            {"message": "We have refined our funding proposal."},
        )
        connection_request.refresh_from_db()
        self.assertEqual(connection_request.status, InvestorConnectionRequest.Status.PENDING)
        self.assertEqual(connection_request.message, "We have refined our funding proposal.")
        self.assertEqual(InvestorConnectionRequest.objects.count(), 1)

    def test_investor_can_accept_a_pending_request(self):
        connection_request = self.create_request()
        self.client.force_login(self.investor)
        response = self.client.post(
            reverse("respond_to_investor_request", args=[connection_request.pk]),
            {"decision": InvestorConnectionRequest.Status.ACCEPTED},
        )
        self.assertRedirects(response, reverse("investor_connection_requests"))
        connection_request.refresh_from_db()
        self.assertEqual(connection_request.status, InvestorConnectionRequest.Status.ACCEPTED)
        notification = Notification.objects.get(recipient=self.entrepreneur)
        self.assertIn("accepted", notification.message)

    def test_investor_can_decline_a_pending_request(self):
        connection_request = self.create_request()
        self.client.force_login(self.investor)
        self.client.post(
            reverse("respond_to_investor_request", args=[connection_request.pk]),
            {"decision": InvestorConnectionRequest.Status.DECLINED},
        )
        connection_request.refresh_from_db()
        self.assertEqual(connection_request.status, InvestorConnectionRequest.Status.DECLINED)

    def test_only_the_assigned_investor_can_respond(self):
        other_investor = User.objects.create_user(
            username="otherinvestor",
            password="StrongPass!2026",
            role=User.Role.INVESTOR,
        )
        connection_request = self.create_request()
        self.client.force_login(other_investor)
        response = self.client.post(
            reverse("respond_to_investor_request", args=[connection_request.pk]),
            {"decision": InvestorConnectionRequest.Status.ACCEPTED},
        )
        self.assertEqual(response.status_code, 404)
        connection_request.refresh_from_db()
        self.assertEqual(connection_request.status, InvestorConnectionRequest.Status.PENDING)

    def test_entrepreneur_cannot_respond_to_investor_request(self):
        connection_request = self.create_request()
        response = self.client.post(
            reverse("respond_to_investor_request", args=[connection_request.pk]),
            {"decision": InvestorConnectionRequest.Status.ACCEPTED},
        )
        self.assertRedirects(response, reverse("dashboard"))
        connection_request.refresh_from_db()
        self.assertEqual(connection_request.status, InvestorConnectionRequest.Status.PENDING)

    def test_investor_sees_received_requests(self):
        self.create_request()
        self.client.force_login(self.investor)
        response = self.client.get(reverse("investor_connection_requests"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Amina Founder")
        self.assertContains(response, "Green Start")

    def test_entrepreneur_sees_sent_request_status(self):
        self.create_request(status=InvestorConnectionRequest.Status.ACCEPTED)
        response = self.client.get(reverse("investor_connection_requests"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Impact Capital")
        self.assertContains(response, "Accepted")

    def test_mentor_cannot_send_investor_request(self):
        mentor = User.objects.create_user(
            username="mentor",
            password="StrongPass!2026",
            role=User.Role.MENTOR,
        )
        self.client.force_login(mentor)
        response = self.client.post(
            reverse("request_investor_connection", args=[self.investor.pk]),
            {"message": "Please consider our business."},
        )
        self.assertRedirects(response, reverse("dashboard"))
        self.assertEqual(InvestorConnectionRequest.objects.count(), 0)
