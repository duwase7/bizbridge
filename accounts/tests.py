import os
from unittest.mock import patch

from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase
from django.urls import reverse

from investor_connections.models import InvestorConnectionRequest
from mentorships.models import MentorshipRequest
from networking.models import Connection, Message
from notifications.models import Notification
from opportunities.models import Opportunity

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



class DemoDataCommandTests(TestCase):
    password = "DemoAccess!2026"

    def seed_demo_data(self, **options):
        call_command("seed_demo_data", password=self.password, **options)

    def test_command_creates_demo_accounts_and_workflows(self):
        self.seed_demo_data()

        founder = User.objects.get(username="demo_founder")
        mentor = User.objects.get(username="demo_mentor")
        investor = User.objects.get(username="demo_investor")

        self.assertEqual(founder.role, User.Role.ENTREPRENEUR)
        self.assertEqual(mentor.role, User.Role.MENTOR)
        self.assertEqual(investor.role, User.Role.INVESTOR)
        self.assertTrue(founder.check_password(self.password))
        self.assertTrue(mentor.check_password(self.password))
        self.assertTrue(investor.check_password(self.password))
        self.assertTrue(mentor.is_verified)
        admin = User.objects.get(username="demo_admin")
        self.assertTrue(admin.is_staff)
        self.assertFalse(admin.is_superuser)
        self.assertEqual(
            Connection.between(founder, User.objects.get(username="demo_partner")).status,
            Connection.Status.ACCEPTED,
        )

        self.assertEqual(
            Opportunity.objects.filter(provider="BizBridge Demo Data").count(),
            5,
        )
        self.assertEqual(MentorshipRequest.objects.count(), 1)
        self.assertEqual(InvestorConnectionRequest.objects.count(), 1)
        self.assertEqual(Notification.objects.count(), 2)
        self.assertEqual(
            MentorshipRequest.objects.get().status,
            MentorshipRequest.Status.PENDING,
        )
        self.assertEqual(
            InvestorConnectionRequest.objects.get().status,
            InvestorConnectionRequest.Status.PENDING,
        )

    def test_command_is_idempotent_and_does_not_reset_passwords_by_default(self):
        self.seed_demo_data()
        founder = User.objects.get(username="demo_founder")
        founder.bio = "A profile edit that should be preserved."
        founder.set_password("UpdatedDemoPass!2026")
        founder.save()

        self.seed_demo_data()

        founder.refresh_from_db()
        self.assertEqual(founder.bio, "A profile edit that should be preserved.")
        self.assertTrue(founder.check_password("UpdatedDemoPass!2026"))
        self.assertEqual(User.objects.count(), 5)
        self.assertEqual(Message.objects.count(), 2)
        self.assertEqual(
            Opportunity.objects.filter(provider="BizBridge Demo Data").count(),
            5,
        )
        self.assertEqual(MentorshipRequest.objects.count(), 1)
        self.assertEqual(InvestorConnectionRequest.objects.count(), 1)
        self.assertEqual(Notification.objects.count(), 2)

        self.seed_demo_data(reset_passwords=True)
        founder.refresh_from_db()
        self.assertTrue(founder.check_password(self.password))

    def test_command_refuses_to_repurpose_an_account_with_another_role(self):
        User.objects.create_user(
            username="demo_mentor",
            password="ExistingPass!2026",
            role=User.Role.ENTREPRENEUR,
        )

        with self.assertRaises(CommandError):
            self.seed_demo_data()

        self.assertFalse(User.objects.filter(username="demo_founder").exists())
        self.assertEqual(User.objects.count(), 1)

    def test_command_rejects_an_unsafe_username_prefix(self):
        with self.assertRaises(CommandError):
            self.seed_demo_data(prefix="../unsafe")


    def test_command_refuses_to_repurpose_an_administrative_account(self):
        User.objects.create_user(
            username="demo_investor",
            password="ExistingPass!2026",
            role=User.Role.INVESTOR,
            is_staff=True,
        )

        with self.assertRaises(CommandError):
            self.seed_demo_data()

        self.assertFalse(User.objects.filter(username="demo_founder").exists())
        investor = User.objects.get(username="demo_investor")
        self.assertTrue(investor.is_staff)
        self.assertTrue(investor.check_password("ExistingPass!2026"))


class SearchAndRecommendationTests(TestCase):
    def setUp(self):
        self.founder = User.objects.create_user(
            username="aline", password="StrongPass!2026", role=User.Role.ENTREPRENEUR,
            business_sector="Agriculture", business_stage="Early stage", location="Kigali",
        )
        self.mentor = User.objects.create_user(
            username="maya", first_name="Maya", password="StrongPass!2026", role=User.Role.MENTOR,
            interest_sectors="Agriculture, Fintech", location="Kigali", mentor_expertise="Marketing",
        )
        self.other_mentor = User.objects.create_user(
            username="paul", first_name="Paul", password="StrongPass!2026", role=User.Role.MENTOR,
            interest_sectors="Health", location="Musanze",
        )
        self.investor = User.objects.create_user(
            username="eric", password="StrongPass!2026", role=User.Role.INVESTOR,
            interest_sectors="Agriculture", location="Kigali",
        )

    def test_entrepreneur_can_filter_people_by_role_and_sector(self):
        self.client.force_login(self.founder)
        response = self.client.get(reverse("people_directory"), {"role": "mentor", "sector": "agri"})
        self.assertContains(response, "Maya")
        self.assertNotContains(response, "Paul")
        self.assertNotContains(response, "eric")

    def test_investor_searches_businesses_only(self):
        self.client.force_login(self.investor)
        response = self.client.get(reverse("people_directory"), {"stage": "Early stage"})
        people = list(response.context["people"])
        self.assertEqual(people, [self.founder])

    def test_mentor_cannot_view_other_mentor_profile(self):
        self.client.force_login(self.mentor)
        response = self.client.get(reverse("person_detail", args=[self.other_mentor.pk]))
        self.assertRedirects(response, reverse("people_directory"))

    def test_dashboard_ranks_matching_people_first(self):
        self.client.force_login(self.founder)
        response = self.client.get(reverse("dashboard"))
        recommended = list(response.context["recommended_people"])
        self.assertIn(self.mentor, recommended)
        self.assertIn(self.investor, recommended)
        self.assertNotIn(self.other_mentor, recommended)

    def test_verified_profile_shows_badge(self):
        self.mentor.is_verified = True
        self.mentor.save()
        self.client.force_login(self.founder)
        response = self.client.get(reverse("person_detail", args=[self.mentor.pk]))
        self.assertContains(response, "Verified")
        self.assertContains(response, "Request mentorship")



class AccountSecurityTests(TestCase):
    password = "StrongPass!2026"

    def setUp(self):
        self.user = User.objects.create_user(
            username="aline", email="aline@example.com", password=self.password,
            role=User.Role.ENTREPRENEUR,
        )

    def test_login_with_email(self):
        response = self.client.post(reverse("login"), {"username": "aline@example.com", "password": self.password})
        self.assertRedirects(response, reverse("dashboard"))

    def test_suspended_account_gets_clear_message(self):
        self.user.is_active = False
        self.user.save()
        response = self.client.post(reverse("login"), {"username": "aline", "password": self.password})
        self.assertContains(response, "suspended")

    def test_wrong_password_does_not_reveal_suspension(self):
        self.user.is_active = False
        self.user.save()
        response = self.client.post(reverse("login"), {"username": "aline", "password": "wrong-password"})
        self.assertNotContains(response, "suspended")

    def test_password_reset_sends_email_link(self):
        from django.core import mail

        response = self.client.post(reverse("password_reset"), {"email": "aline@example.com"})
        self.assertRedirects(response, reverse("password_reset_done"))
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn("/accounts/reset/", mail.outbox[0].body)

    def test_short_password_is_rejected_at_signup(self):
        response = self.client.post(reverse("signup"), {
            "username": "new", "first_name": "N", "last_name": "U", "email": "new@example.com",
            "role": "mentor", "password1": "short", "password2": "short",
        })
        self.assertContains(response, "at least 8 characters")
        self.assertFalse(User.objects.filter(username="new").exists())

    def test_user_can_delete_own_account(self):
        self.client.force_login(self.user)
        response = self.client.post(reverse("delete_account"), {"password": self.password})
        self.assertRedirects(response, reverse("home"))
        self.assertFalse(User.objects.filter(pk=self.user.pk).exists())

    def test_delete_requires_correct_password(self):
        self.client.force_login(self.user)
        self.client.post(reverse("delete_account"), {"password": "nope"})
        self.assertTrue(User.objects.filter(pk=self.user.pk).exists())

    def test_help_page_is_public(self):
        response = self.client.get(reverse("help"))
        self.assertContains(response, "does not accept payments")

    def test_session_expires_after_30_minutes(self):
        from django.conf import settings

        self.assertEqual(settings.SESSION_COOKIE_AGE, 1800)
        self.assertTrue(settings.SESSION_SAVE_EVERY_REQUEST)
