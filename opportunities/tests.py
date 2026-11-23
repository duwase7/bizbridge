from django.test import TestCase
from django.urls import reverse

from accounts.models import User
from .models import Opportunity


class OpportunityDiscoveryTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="founder",
            password="StrongPass!2026",
            role=User.Role.ENTREPRENEUR,
        )
        self.client.force_login(self.user)

    def create_opportunity(self, **overrides):
        values = {
            "title": "Clean Energy Fund",
            "provider": "Green Growth Rwanda",
            "description": "Funding for early-stage clean energy businesses.",
            "category": Opportunity.Category.FUNDING,
            "sector": "Energy",
            "location": "Kigali",
        }
        values.update(overrides)
        return Opportunity.objects.create(**values)

    def test_opportunity_page_requires_login(self):
        self.client.logout()
        response = self.client.get(reverse("opportunity_list"))
        self.assertRedirects(
            response,
            f"{reverse('login')}?next={reverse('opportunity_list')}",
        )

    def test_active_opportunities_are_displayed_and_inactive_are_hidden(self):
        self.create_opportunity()
        self.create_opportunity(
            title="Closed Training",
            category=Opportunity.Category.TRAINING,
            is_active=False,
        )

        response = self.client.get(reverse("opportunity_list"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Clean Energy Fund")
        self.assertNotContains(response, "Closed Training")

    def test_search_matches_opportunity_details(self):
        self.create_opportunity()
        self.create_opportunity(
            title="Agriculture Skills Bootcamp",
            provider="Rwanda Skills Hub",
            description="Practical training for founders.",
            category=Opportunity.Category.TRAINING,
            sector="Agriculture",
        )

        response = self.client.get(
            reverse("opportunity_list"),
            {"q": "Agriculture"},
        )

        self.assertContains(response, "Agriculture Skills Bootcamp")
        self.assertNotContains(response, "Clean Energy Fund")

    def test_category_filter_returns_only_selected_category(self):
        self.create_opportunity()
        self.create_opportunity(
            title="Founder Training",
            category=Opportunity.Category.TRAINING,
        )

        response = self.client.get(
            reverse("opportunity_list"),
            {"category": Opportunity.Category.TRAINING},
        )

        self.assertContains(response, "Founder Training")
        self.assertNotContains(response, "Clean Energy Fund")

    def test_invalid_category_is_ignored(self):
        self.create_opportunity()

        response = self.client.get(
            reverse("opportunity_list"),
            {"category": "not-a-category"},
        )

        self.assertContains(response, "Clean Energy Fund")


class OpportunityDetailAndExpiryTests(TestCase):
    def setUp(self):
        from datetime import timedelta

        from django.utils import timezone

        from accounts.models import User

        self.user = User.objects.create_user(username="viewer", password="StrongPass!2026")
        today = timezone.localdate()
        self.open_opp = Opportunity.objects.create(
            title="Open Grant", provider="P", description="d", sector="Agriculture",
            location="Kigali", deadline=today + timedelta(days=5),
        )
        self.expired_opp = Opportunity.objects.create(
            title="Old Grant", provider="P", description="d", deadline=today - timedelta(days=1),
        )
        self.client.force_login(self.user)

    def test_expired_opportunities_are_hidden(self):
        response = self.client.get(reverse("opportunity_list"))
        self.assertContains(response, "Open Grant")
        self.assertNotContains(response, "Old Grant")
        response = self.client.get(reverse("opportunity_detail", args=[self.expired_opp.pk]))
        self.assertEqual(response.status_code, 404)

    def test_detail_page_counts_views(self):
        self.client.get(reverse("opportunity_detail", args=[self.open_opp.pk]))
        self.client.get(reverse("opportunity_detail", args=[self.open_opp.pk]))
        self.open_opp.refresh_from_db()
        self.assertEqual(self.open_opp.view_count, 2)

    def test_filter_by_sector_and_location(self):
        response = self.client.get(reverse("opportunity_list"), {"sector": "agri", "location": "kig"})
        self.assertContains(response, "Open Grant")
        response = self.client.get(reverse("opportunity_list"), {"location": "Huye"})
        self.assertNotContains(response, "Open Grant")
