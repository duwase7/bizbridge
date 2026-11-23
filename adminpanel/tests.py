from django.test import TestCase
from django.urls import reverse

from accounts.models import User
from networking.models import Connection
from opportunities.models import Opportunity

PASSWORD = "StrongPass!2026"


class AdminConsoleTests(TestCase):
    def setUp(self):
        self.admin = User.objects.create_user(username="admin1", password=PASSWORD, is_staff=True)
        self.mentor = User.objects.create_user(username="mentor1", password=PASSWORD, role=User.Role.MENTOR)
        self.founder = User.objects.create_user(username="founder1", password=PASSWORD, role=User.Role.ENTREPRENEUR)
        self.client.force_login(self.admin)

    def act(self, user, action):
        return self.client.post(reverse("admin_user_action", args=[user.pk]), {"action": action})

    def test_members_cannot_open_admin_console(self):
        self.client.force_login(self.founder)
        for name in ("admin_dashboard", "admin_users", "admin_opportunities"):
            response = self.client.get(reverse(name))
            self.assertEqual(response.status_code, 302)

    def test_admin_dashboard_shows_report(self):
        Connection.objects.create(requester=self.founder, receiver=self.mentor, status="accepted")
        response = self.client.get(reverse("admin_dashboard"))
        self.assertContains(response, "Platform activity")
        self.assertEqual(response.context["report"]["all_requests"], 1)
        self.assertEqual(response.context["report"]["acceptance_rate"], 100)

    def test_csv_report_downloads(self):
        response = self.client.get(reverse("admin_report_csv"))
        self.assertEqual(response["Content-Type"], "text/csv")
        self.assertIn("Entrepreneurs", response.content.decode())

    def test_suspended_user_cannot_log_in_until_reactivated(self):
        self.act(self.founder, "suspend")
        self.founder.refresh_from_db()
        self.assertFalse(self.founder.is_active)
        self.client.logout()
        self.assertFalse(self.client.login(username="founder1", password=PASSWORD))
        self.client.force_login(self.admin)
        self.act(self.founder, "reactivate")
        self.client.logout()
        self.assertTrue(self.client.login(username="founder1", password=PASSWORD))

    def test_verify_mentor_shows_badge_and_notifies(self):
        self.act(self.mentor, "verify")
        self.mentor.refresh_from_db()
        self.assertTrue(self.mentor.is_verified)
        self.assertTrue(self.mentor.notifications.filter(message__contains="verified").exists())

    def test_entrepreneurs_are_not_verified(self):
        self.act(self.founder, "verify")
        self.founder.refresh_from_db()
        self.assertFalse(self.founder.is_verified)

    def test_delete_account(self):
        self.act(self.founder, "delete")
        self.assertFalse(User.objects.filter(pk=self.founder.pk).exists())

    def test_admin_cannot_suspend_self(self):
        self.act(self.admin, "suspend")
        self.admin.refresh_from_db()
        self.assertTrue(self.admin.is_active)

    def test_create_edit_and_delete_opportunity(self):
        self.client.post(reverse("admin_opportunity_create"), {
            "title": "Seed Fund", "category": "funding", "provider": "BDF",
            "description": "Grants", "sector": "All sectors", "location": "Rwanda", "is_active": "on",
        })
        opportunity = Opportunity.objects.get(title="Seed Fund")
        self.client.post(reverse("admin_opportunity_edit", args=[opportunity.pk]), {
            "title": "Seed Fund 2026", "category": "funding", "provider": "BDF",
            "description": "Grants", "is_active": "on",
        })
        opportunity.refresh_from_db()
        self.assertEqual(opportunity.title, "Seed Fund 2026")
        self.client.post(reverse("admin_opportunity_delete", args=[opportunity.pk]))
        self.assertFalse(Opportunity.objects.exists())

    def test_staff_dashboard_redirects_to_console(self):
        self.assertRedirects(self.client.get(reverse("dashboard")), reverse("admin_dashboard"))
