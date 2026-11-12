from django.test import TestCase
from django.urls import reverse

from .models import User


class AccountFlowTests(TestCase):
    def test_home_page_loads(self):
        response = self.client.get(reverse("home"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Build your business.")

    def test_registration_creates_an_entrepreneur_account(self):
        response = self.client.post(
            reverse("signup"),
            {
                "username": "founder1",
                "first_name": "Amina",
                "last_name": "Founder",
                "email": "amina@example.com",
                "role": User.Role.ENTREPRENEUR,
                "organization": "Green Start",
                "location": "Kigali",
                "password1": "StrongPass!2026",
                "password2": "StrongPass!2026",
            },
        )
        self.assertRedirects(response, reverse("dashboard"))
        user = User.objects.get(username="founder1")
        self.assertEqual(user.role, User.Role.ENTREPRENEUR)
        self.assertTrue(user.check_password("StrongPass!2026"))

    def test_authenticated_user_can_open_dashboard(self):
        user = User.objects.create_user(
            username="mentor1",
            password="StrongPass!2026",
            role=User.Role.MENTOR,
        )
        self.client.force_login(user)
        response = self.client.get(reverse("dashboard"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Mentor")

    def test_dashboard_requires_authentication(self):
        response = self.client.get(reverse("dashboard"))
        self.assertRedirects(
            response,
            f"{reverse('login')}?next={reverse('dashboard')}",
        )
