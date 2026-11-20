import os
from unittest.mock import patch

from django.core.management import call_command
from django.test import TestCase
from django.urls import reverse

from .forms import ProfileForm
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
                "username": "founder1", "first_name": "Amina", "last_name": "Founder",
                "email": "amina@example.com", "role": User.Role.ENTREPRENEUR,
                "organization": "Green Start", "location": "Kigali",
                "password1": "StrongPass!2026", "password2": "StrongPass!2026",
            },
        )
        self.assertRedirects(response, reverse("dashboard"))
        user = User.objects.get(username="founder1")
        self.assertEqual(user.role, User.Role.ENTREPRENEUR)
        self.assertTrue(user.check_password("StrongPass!2026"))

    def test_authenticated_user_can_open_dashboard(self):
        user = User.objects.create_user(username="mentor1", password="StrongPass!2026", role=User.Role.MENTOR)
        self.client.force_login(user)
        response = self.client.get(reverse("dashboard"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Mentor")

    def test_dashboard_requires_authentication(self):
        response = self.client.get(reverse("dashboard"))
        self.assertRedirects(response, f"{reverse('login')}?next={reverse('dashboard')}")


class ProfileManagementTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="founder2", password="StrongPass!2026",
            email="founder@example.com", role=User.Role.ENTREPRENEUR,
        )
        self.client.force_login(self.user)

    def test_profile_page_displays_existing_details(self):
        response = self.client.get(reverse("edit_profile"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Edit your profile")
        self.assertContains(response, "founder@example.com")

    def test_entrepreneur_can_save_business_profile_without_changing_role(self):
        response = self.client.post(reverse("edit_profile"), {
            "first_name": "Amina", "last_name": "Founder", "email": "amina@example.com",
            "organization": "Green Start", "location": "Kigali",
            "bio": "Building sustainable agriculture solutions.",
            "business_name": "Green Start Farms", "business_sector": "Agriculture",
            "business_stage": "Operating", "business_description": "Growing sustainable produce.",
        })
        self.assertRedirects(response, reverse("dashboard"))
        self.user.refresh_from_db()
        self.assertEqual(self.user.business_name, "Green Start Farms")
        self.assertEqual(self.user.business_sector, "Agriculture")
        self.assertEqual(self.user.business_stage, "Operating")
        self.assertEqual(self.user.role, User.Role.ENTREPRENEUR)

    def test_profile_form_shows_only_fields_for_the_users_role(self):
        entrepreneur_form = ProfileForm(instance=self.user)
        self.assertIn("business_name", entrepreneur_form.fields)
        self.assertNotIn("mentor_expertise", entrepreneur_form.fields)
        self.assertNotIn("investor_type", entrepreneur_form.fields)

        mentor = User.objects.create_user(username="mentor3", password="StrongPass!2026", role=User.Role.MENTOR)
        mentor_form = ProfileForm(instance=mentor)
        self.assertIn("mentor_expertise", mentor_form.fields)
        self.assertIn("mentor_availability", mentor_form.fields)
        self.assertNotIn("business_name", mentor_form.fields)

        investor = User.objects.create_user(username="investor3", password="StrongPass!2026", role=User.Role.INVESTOR)
        investor_form = ProfileForm(instance=investor)
        self.assertIn("investor_type", investor_form.fields)
        self.assertIn("website", investor_form.fields)
        self.assertNotIn("mentor_expertise", investor_form.fields)

    def test_mentor_can_save_expertise_and_availability(self):
        mentor = User.objects.create_user(
            username="mentor4", password="StrongPass!2026",
            email="mentor4@example.com", role=User.Role.MENTOR,
        )
        self.client.force_login(mentor)
        response = self.client.post(reverse("edit_profile"), {
            "first_name": "Maya", "last_name": "Mentor", "email": "maya@example.com",
            "organization": "Growth Hub", "location": "Kigali", "bio": "Supporting founders.",
            "mentor_expertise": "Marketing and sales", "mentor_availability": "Weekday evenings",
        })
        self.assertRedirects(response, reverse("dashboard"))
        mentor.refresh_from_db()
        self.assertEqual(mentor.mentor_expertise, "Marketing and sales")
        self.assertEqual(mentor.mentor_availability, "Weekday evenings")

    def test_investor_can_save_investor_type_and_website(self):
        investor = User.objects.create_user(
            username="investor4", password="StrongPass!2026",
            email="investor4@example.com", role=User.Role.INVESTOR,
        )
        self.client.force_login(investor)
        response = self.client.post(reverse("edit_profile"), {
            "first_name": "Irene", "last_name": "Investor", "email": "irene@example.com",
            "organization": "Impact Capital", "location": "Kigali",
            "bio": "Investing in sustainable businesses.",
            "investor_type": "Impact investor", "website": "https://example.com",
        })
        self.assertRedirects(response, reverse("dashboard"))
        investor.refresh_from_db()
        self.assertEqual(investor.investor_type, "Impact investor")
        self.assertEqual(investor.website, "https://example.com")

    def test_user_cannot_claim_another_accounts_email(self):
        User.objects.create_user(
            username="mentor2", password="StrongPass!2026",
            email="mentor@example.com", role=User.Role.MENTOR,
        )
        response = self.client.post(reverse("edit_profile"), {
            "first_name": "", "last_name": "", "email": "mentor@example.com",
            "organization": "", "location": "", "bio": "", "business_name": "",
            "business_sector": "", "business_stage": "", "business_description": "",
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "An account with this email already exists.")
        self.user.refresh_from_db()
        self.assertEqual(self.user.email, "founder@example.com")

    def test_profile_page_requires_authentication(self):
        self.client.logout()
        response = self.client.get(reverse("edit_profile"))
        self.assertRedirects(response, f"{reverse('login')}?next={reverse('edit_profile')}")


class BootstrapAdminCommandTests(TestCase):
    def setUp(self):
        self.credentials = {
            "DJANGO_SUPERUSER_USERNAME": "siteadmin",
            "DJANGO_SUPERUSER_EMAIL": "siteadmin@example.com",
            "DJANGO_SUPERUSER_PASSWORD": "ComplexAdminPass!2026",
        }

    def test_command_skips_when_credentials_are_missing(self):
        with patch.dict(os.environ, {
            "DJANGO_SUPERUSER_USERNAME": "", "DJANGO_SUPERUSER_EMAIL": "",
            "DJANGO_SUPERUSER_PASSWORD": "",
        }):
            call_command("bootstrap_admin")
        self.assertFalse(User.objects.exists())

    def test_command_creates_superuser_from_environment(self):
        with patch.dict(os.environ, self.credentials):
            call_command("bootstrap_admin")
        admin = User.objects.get(username="siteadmin")
        self.assertTrue(admin.is_staff)
        self.assertTrue(admin.is_superuser)
        self.assertTrue(admin.check_password("ComplexAdminPass!2026"))

    def test_existing_username_is_never_promoted_or_reset(self):
        existing_user = User.objects.create_user(
            username="siteadmin", password="ExistingPass!2026", email="existing@example.com",
        )
        with patch.dict(os.environ, self.credentials):
            call_command("bootstrap_admin")
        existing_user.refresh_from_db()
        self.assertFalse(existing_user.is_staff)
        self.assertFalse(existing_user.is_superuser)
        self.assertTrue(existing_user.check_password("ExistingPass!2026"))
