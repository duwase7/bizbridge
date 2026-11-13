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


class ProfileManagementTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="founder2",
            password="StrongPass!2026",
            email="founder@example.com",
            role=User.Role.ENTREPRENEUR,
        )
        self.client.force_login(self.user)

    def test_profile_page_displays_existing_details(self):
        response = self.client.get(reverse("edit_profile"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Edit your profile")
        self.assertContains(response, "founder@example.com")

    def test_user_can_update_profile_without_changing_role(self):
        response = self.client.post(
            reverse("edit_profile"),
            {
                "first_name": "Amina",
                "last_name": "Founder",
                "email": "amina@example.com",
                "organization": "Green Start",
                "location": "Kigali",
                "bio": "Building sustainable agriculture solutions.",
            },
        )

        self.assertRedirects(response, reverse("dashboard"))
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, "Amina")
        self.assertEqual(self.user.last_name, "Founder")
        self.assertEqual(self.user.email, "amina@example.com")
        self.assertEqual(self.user.organization, "Green Start")
        self.assertEqual(self.user.location, "Kigali")
        self.assertEqual(
            self.user.bio,
            "Building sustainable agriculture solutions.",
        )
        self.assertEqual(self.user.role, User.Role.ENTREPRENEUR)

    def test_user_cannot_claim_another_accounts_email(self):
        User.objects.create_user(
            username="mentor2",
            password="StrongPass!2026",
            email="mentor@example.com",
            role=User.Role.MENTOR,
        )
        response = self.client.post(
            reverse("edit_profile"),
            {
                "first_name": "",
                "last_name": "",
                "email": "mentor@example.com",
                "organization": "",
                "location": "",
                "bio": "",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "An account with this email already exists.")
        self.user.refresh_from_db()
        self.assertEqual(self.user.email, "founder@example.com")

    def test_profile_page_requires_authentication(self):
        self.client.logout()
        response = self.client.get(reverse("edit_profile"))
        self.assertRedirects(
            response,
            f"{reverse('login')}?next={reverse('edit_profile')}",
        )
