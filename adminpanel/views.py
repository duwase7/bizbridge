import csv
from datetime import timedelta

from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from django.db.models import Count, Q, Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.http import require_POST

from accounts.models import User
from investor_connections.models import InvestorConnectionRequest
from mentorships.models import MentorshipRequest
from networking.models import Connection, Message
from notifications.models import Notification
from opportunities.models import Opportunity

from .forms import OpportunityForm

staff_required = user_passes_test(lambda u: u.is_active and u.is_staff, login_url="login")


def _rate(part, whole):
    return round(100 * part / whole) if whole else 0


def build_report():
    """Platform activity figures (FR-26) and the hypothesis targets from the proposal."""
    now = timezone.now()
    members = User.objects.filter(is_staff=False)
    roles = dict(members.values_list("role").annotate(n=Count("id")))
    connections = Connection.objects.aggregate(
        total=Count("id"),
        accepted=Count("id", filter=Q(status="accepted")),
        pending=Count("id", filter=Q(status="pending")),
        declined=Count("id", filter=Q(status="declined")),
    )
    mentorships = MentorshipRequest.objects.aggregate(
        total=Count("id"), accepted=Count("id", filter=Q(status="accepted"))
    )
    investor = InvestorConnectionRequest.objects.aggregate(
        total=Count("id"), accepted=Count("id", filter=Q(status="accepted"))
    )
    all_requests = connections["total"] + mentorships["total"] + investor["total"]
    all_accepted = connections["accepted"] + mentorships["accepted"] + investor["accepted"]
    entrepreneurs = roles.get(User.Role.ENTREPRENEUR, 0)
    supporters = roles.get(User.Role.MENTOR, 0) + roles.get(User.Role.INVESTOR, 0)
    return {
        "total_members": members.count(),
        "entrepreneurs": entrepreneurs,
        "mentors": roles.get(User.Role.MENTOR, 0),
        "investors": roles.get(User.Role.INVESTOR, 0),
        "suspended": members.filter(is_active=False).count(),
        "awaiting_verification": members.filter(
            role__in=(User.Role.MENTOR, User.Role.INVESTOR), is_verified=False
        ).count(),
        "new_last_7_days": members.filter(date_joined__gte=now - timedelta(days=7)).count(),
        "new_last_30_days": members.filter(date_joined__gte=now - timedelta(days=30)).count(),
        "connections": connections,
        "mentorships": mentorships,
        "investor_requests": investor,
        "all_requests": all_requests,
        "all_accepted": all_accepted,
        "acceptance_rate": _rate(all_accepted, all_requests),
        "messages": Message.objects.count(),
        "opportunities_live": Opportunity.visible().count(),
        "opportunities_total": Opportunity.objects.count(),
        "opportunity_views": Opportunity.objects.aggregate(v=Sum("view_count"))["v"] or 0,
        "top_opportunities": Opportunity.objects.order_by("-view_count", "title")[:5],
        "targets": [
            ("Entrepreneurs registered", entrepreneurs, 50),
            ("Mentors / investors registered", supporters, 10),
            ("Connection requests sent", all_requests, 100),
        ],
        "target_rate": ("Requests accepted", _rate(all_accepted, all_requests), 30),
    }


@staff_required
def admin_dashboard(request):
    report = build_report()
    report["targets"] = [
        (label, value, goal, min(100, _rate(value, goal))) for label, value, goal in report["targets"]
    ]
    return render(request, "adminpanel/dashboard.html", {"report": report})


@staff_required
def report_csv(request):
    report = build_report()
    response = HttpResponse(content_type="text/csv")
    stamp = timezone.localdate().isoformat()
    response["Content-Disposition"] = f'attachment; filename="bizbridge-report-{stamp}.csv"'
    writer = csv.writer(response)
    writer.writerow(["Metric", "Value"])
    rows = [
        ("Report date", stamp),
        ("Total members", report["total_members"]),
        ("Entrepreneurs", report["entrepreneurs"]),
        ("Mentors", report["mentors"]),
        ("Investors", report["investors"]),
        ("New members (7 days)", report["new_last_7_days"]),
        ("New members (30 days)", report["new_last_30_days"]),
        ("Suspended accounts", report["suspended"]),
        ("Connection requests", report["connections"]["total"]),
        ("Connections accepted", report["connections"]["accepted"]),
        ("Mentorship requests", report["mentorships"]["total"]),
        ("Mentorships accepted", report["mentorships"]["accepted"]),
        ("Investor requests", report["investor_requests"]["total"]),
        ("Investor requests accepted", report["investor_requests"]["accepted"]),
        ("Overall acceptance rate (%)", report["acceptance_rate"]),
        ("Messages sent", report["messages"]),
        ("Live opportunities", report["opportunities_live"]),
        ("Opportunity views", report["opportunity_views"]),
    ]
    writer.writerows(rows)
    writer.writerow([])
    writer.writerow(["Opportunity", "Views"])
    for opportunity in Opportunity.objects.order_by("-view_count"):
        writer.writerow([opportunity.title, opportunity.view_count])
    return response


@staff_required
def user_list(request):
    users = User.objects.order_by("-date_joined")
    query = request.GET.get("q", "").strip()
    role = request.GET.get("role", "")
    status = request.GET.get("status", "")
    if query:
        users = users.filter(
            Q(username__icontains=query) | Q(email__icontains=query)
            | Q(first_name__icontains=query) | Q(last_name__icontains=query)
        )
    if role in User.Role.values:
        users = users.filter(role=role, is_staff=False)
    elif role == "admin":
        users = users.filter(is_staff=True)
    if status == "suspended":
        users = users.filter(is_active=False)
    elif status == "unverified":
        users = users.filter(role__in=(User.Role.MENTOR, User.Role.INVESTOR), is_verified=False, is_staff=False)
    return render(
        request,
        "adminpanel/users.html",
        {"users": users, "query": query, "role": role, "status": status, "roles": User.Role.choices},
    )


@staff_required
@require_POST
def user_action(request, user_id):
    """Suspend, reactivate, verify or delete an account (FR-24, FR-25, BR-06)."""
    target = get_object_or_404(User, pk=user_id)
    action = request.POST.get("action")
    back = request.POST.get("next") or reverse("admin_users")
    if not back.startswith("/"):
        back = reverse("admin_users")
    if target == request.user or target.is_superuser:
        messages.error(request, "You cannot change your own or a superuser account here.")
        return redirect(back)

    name = target.display_name
    if action == "suspend":
        target.is_active = False
        target.save(update_fields=("is_active",))
        messages.success(request, f"{name} has been suspended and can no longer log in.")
    elif action == "reactivate":
        target.is_active = True
        target.save(update_fields=("is_active",))
        messages.success(request, f"{name} has been reactivated.")
    elif action in ("verify", "unverify"):
        if target.role not in (User.Role.MENTOR, User.Role.INVESTOR):
            messages.error(request, "Only mentor and investor profiles are verified.")
            return redirect(back)
        target.is_verified = action == "verify"
        target.save(update_fields=("is_verified",))
        if target.is_verified:
            Notification.objects.create(
                recipient=target, actor=request.user,
                message="Your profile has been verified by BizBridge.",
                link=reverse("person_detail", args=[target.pk]),
            )
        messages.success(request, f"{name} is now {'verified' if target.is_verified else 'unverified'}.")
    elif action == "delete":
        target.delete()
        messages.success(request, f"The account for {name} was deleted.")
        return redirect("admin_users")
    else:
        messages.error(request, "Unknown action.")
    return redirect(back)


@staff_required
def opportunity_admin_list(request):
    opportunities = Opportunity.objects.order_by("-created_at")
    return render(request, "adminpanel/opportunities.html", {"opportunities": opportunities})


@staff_required
def opportunity_edit(request, pk=None):
    """Create and edit opportunities (FR-14, BR-04)."""
    opportunity = get_object_or_404(Opportunity, pk=pk) if pk else None
    form = OpportunityForm(request.POST or None, instance=opportunity)
    if request.method == "POST" and form.is_valid():
        saved = form.save()
        messages.success(request, f"Opportunity “{saved.title}” saved.")
        return redirect("admin_opportunities")
    return render(request, "adminpanel/opportunity_form.html", {"form": form, "opportunity": opportunity})


@staff_required
@require_POST
def opportunity_delete(request, pk):
    opportunity = get_object_or_404(Opportunity, pk=pk)
    title = opportunity.title
    opportunity.delete()
    messages.success(request, f"Opportunity “{title}” removed.")
    return redirect("admin_opportunities")
