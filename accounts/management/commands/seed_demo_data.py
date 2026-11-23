import re

from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.urls import reverse

from datetime import timedelta

from django.utils import timezone

from investor_connections.models import InvestorConnectionRequest
from networking.models import Connection, Message
from mentorships.models import MentorshipRequest
from notifications.models import Notification
from opportunities.models import Opportunity


class Command(BaseCommand):
    help = "Create repeatable sample accounts and workflows for a BizBridge demonstration."

    def add_arguments(self, parser):
        parser.add_argument(
            "--password",
            required=True,
            help="Password to assign to newly created demo accounts.",
        )
        parser.add_argument(
            "--prefix",
            default="demo",
            help="Username prefix for the three demo accounts (default: demo).",
        )
        parser.add_argument(
            "--reset-passwords",
            action="store_true",
            help="Also reset passwords for existing non-staff demo accounts.",
        )

    def handle(self, *args, **options):
        password = options["password"]
        prefix = options["prefix"].strip().lower()
        reset_passwords = options["reset_passwords"]

        if not re.fullmatch(r"[a-z0-9_]{1,130}", prefix):
            raise CommandError(
                "The prefix must contain only lowercase letters, numbers or underscores "
                "and be no longer than 130 characters."
            )

        try:
            validate_password(password)
        except ValidationError as error:
            raise CommandError(
                "The demo password does not meet Django's password requirements: "
                + "; ".join(error.messages)
            ) from error

        User = get_user_model()
        specifications = {
            "founder": {
                "email": f"{prefix}_founder@example.test",
                "first_name": "Aline",
                "last_name": "Uwimana",
                "role": User.Role.ENTREPRENEUR,
                "organization": "Demo GreenGrow Rwanda",
                "location": "Kigali, Rwanda",
                "bio": (
                    "Building an early-stage agritech venture that helps smallholder "
                    "farmers access affordable inputs and market information."
                ),
                "business_name": "Demo GreenGrow Rwanda",
                "business_sector": "Agriculture",
                "business_stage": "Early stage",
                "business_description": (
                    "A sample agritech venture focused on practical tools for "
                    "smallholder farmers."
                ),
            },
            "mentor": {
                "email": f"{prefix}_mentor@example.test",
                "first_name": "Maya",
                "last_name": "Mentor",
                "role": User.Role.MENTOR,
                "organization": "Demo Founder Network",
                "location": "Kigali, Rwanda",
                "bio": (
                    "Supports early-stage founders with business models, customer "
                    "discovery and go-to-market planning."
                ),
                "mentor_expertise": (
                    "Business strategy, customer discovery, go-to-market"
                ),
                "mentor_availability": "Weekday evenings",
                "interest_sectors": "Agriculture, Retail, Fintech",
                "is_verified": True,
            },
            "investor": {
                "email": f"{prefix}_investor@example.test",
                "first_name": "Eric",
                "last_name": "Investor",
                "role": User.Role.INVESTOR,
                "organization": "Demo Impact Capital",
                "location": "Kigali, Rwanda",
                "bio": (
                    "Interested in early-stage, impact-driven businesses in "
                    "agriculture and climate solutions."
                ),
                "investor_type": "Impact investor",
                "interest_sectors": "Agriculture, Climate, Energy",
                "website": "https://example.org",
                "is_verified": True,
            },
            "partner": {
                "email": f"{prefix}_partner@example.test",
                "first_name": "Jean",
                "last_name": "Habimana",
                "role": User.Role.ENTREPRENEUR,
                "organization": "Demo AgroLink Logistics",
                "location": "Kigali, Rwanda",
                "bio": "Runs a small logistics business moving produce from farms to Kigali markets.",
                "business_name": "Demo AgroLink Logistics",
                "business_sector": "Agriculture",
                "business_stage": "Early stage",
                "business_description": "Sample cold-chain delivery start-up looking for farm partners.",
            },
            "admin": {
                "email": f"{prefix}_admin@example.test",
                "first_name": "BizBridge",
                "last_name": "Admin",
                "role": User.Role.ENTREPRENEUR,
                "is_staff": True,
            },
        }

        usernames = {
            key: f"{prefix}_{key}" for key in specifications
        }

        with transaction.atomic():
            # Check all existing usernames before writing anything. Never repurpose
            # an account with a different role or an administrative account.
            for key, fields in specifications.items():
                existing = User.objects.filter(username=usernames[key]).first()
                if existing and key == "admin" and (existing.is_superuser or not existing.is_staff):
                    raise CommandError(
                        f"Username '{usernames[key]}' exists but is not a demo administrator."
                    )
                if existing and key != "admin" and existing.role != fields["role"]:
                    raise CommandError(
                        f"Username '{usernames[key]}' already belongs to a different role."
                    )
                if existing and key != "admin" and (existing.is_staff or existing.is_superuser):
                    raise CommandError(
                        f"Username '{usernames[key]}' is an administrative account; "
                        "choose another --prefix."
                    )

            users = {}
            for key, fields in specifications.items():
                username = usernames[key]
                user = User.objects.filter(username=username).first()
                if user is None:
                    user = User.objects.create_user(
                        username=username,
                        password=password,
                        **fields,
                    )
                elif reset_passwords:
                    user.set_password(password)
                    user.save(update_fields=["password"])
                users[key] = user

            founder = users["founder"]
            mentor = users["mentor"]
            investor = users["investor"]
            partner = users["partner"]
            today = timezone.localdate()

            demo_opportunities = [
                {
                    "title": "[DEMO] Rwanda Agritech Growth Grant",
                    "category": Opportunity.Category.FUNDING,
                    "sector": "Agriculture",
                    "location": "Rwanda",
                    "deadline": today + timedelta(days=45),
                    "description": (
                        "Sample funding opportunity for demonstrating the BizBridge "
                        "discovery workflow. Replace with verified programme details "
                        "before using this platform for real applications."
                    ),
                },
                {
                    "title": "[DEMO] Founder Business Readiness Workshop",
                    "category": Opportunity.Category.TRAINING,
                    "sector": "All sectors",
                    "location": "Kigali, Rwanda",
                    "description": (
                        "Sample workshop opportunity for demonstrating search and "
                        "category filters. This is not a live programme."
                    ),
                },
                {
                    "title": "[DEMO] Youth Enterprise Pitch Challenge",
                    "category": Opportunity.Category.COMPETITION,
                    "sector": "All sectors",
                    "location": "Rwanda",
                    "deadline": today + timedelta(days=20),
                    "description": (
                        "Sample pitch competition for demonstrating the opportunity "
                        "directory. This is not an open application call."
                    ),
                },
                {
                    "title": "[DEMO] Kigali Climate Incubator Cohort",
                    "category": Opportunity.Category.INCUBATOR,
                    "sector": "Agriculture, Climate",
                    "location": "Kigali, Rwanda",
                    "deadline": today + timedelta(days=60),
                    "description": (
                        "Sample six-month incubator programme used to demonstrate "
                        "recommendations. This is not a live programme."
                    ),
                },
                {
                    "title": "[DEMO] Expired Seed Fund (hidden)",
                    "category": Opportunity.Category.FUNDING,
                    "sector": "All sectors",
                    "location": "Rwanda",
                    "deadline": today - timedelta(days=3),
                    "description": "Sample expired opportunity. It should not appear to members.",
                },
            ]

            for opportunity in demo_opportunities:
                Opportunity.objects.get_or_create(
                    title=opportunity["title"],
                    provider="BizBridge Demo Data",
                    defaults={
                        **opportunity,
                        "provider": "BizBridge Demo Data",
                        "is_active": True,
                    },
                )

            MentorshipRequest.objects.get_or_create(
                entrepreneur=founder,
                mentor=mentor,
                defaults={
                    "message": (
                        "I am building an early-stage agritech venture and would "
                        "appreciate guidance on validating the business model and "
                        "reaching smallholder farmers."
                    ),
                    "status": MentorshipRequest.Status.PENDING,
                },
            )
            InvestorConnectionRequest.objects.get_or_create(
                entrepreneur=founder,
                investor=investor,
                defaults={
                    "message": (
                        "We are preparing to scale our agritech pilot and would "
                        "welcome a conversation about impact investment."
                    ),
                    "status": InvestorConnectionRequest.Status.PENDING,
                },
            )

            connection = Connection.between(founder, partner)
            if connection is None:
                connection = Connection.objects.create(
                    requester=founder,
                    receiver=partner,
                    note="Let's explore moving GreenGrow produce with AgroLink.",
                    status=Connection.Status.ACCEPTED,
                )
                Message.objects.create(
                    connection=connection,
                    sender=founder,
                    content="Hi Jean, could AgroLink collect produce from our farmer groups in Bugesera?",
                )
                Message.objects.create(
                    connection=connection,
                    sender=partner,
                    content="Yes! We run a route there every Tuesday. Let's plan a pilot.",
                )

            Notification.objects.get_or_create(
                recipient=mentor,
                actor=founder,
                message=f"New mentorship request from {founder.get_full_name()}.",
                link=reverse("mentorship_requests"),
                defaults={"is_read": False},
            )
            Notification.objects.get_or_create(
                recipient=investor,
                actor=founder,
                message=f"New investor connection request from {founder.get_full_name()}.",
                link=reverse("investor_connection_requests"),
                defaults={"is_read": False},
            )

        self.stdout.write(self.style.SUCCESS("BizBridge demo data is ready."))
        self.stdout.write("Demo accounts:")
        for key in specifications:
            role = "administrator" if key == "admin" else specifications[key]["role"]
            self.stdout.write(f"  {usernames[key]} ({role})")
        self.stdout.write(
            "The supplied password is not printed. Use --reset-passwords only "
            "when you intentionally want to change existing demo account passwords."
        )
        self.stdout.write(
            "Created or reused 5 sample opportunities (1 expired), 1 mentorship request, "
            "1 investor request, 1 accepted connection with messages and 2 notifications."
        )
