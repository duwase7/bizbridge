from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_POST

from accounts.models import User
from networking.models import Connection
from notifications.models import Notification

from .forms import MentorshipRequestForm
from .models import MentorshipRequest


@login_required
def mentor_directory(request):
    if request.user.role != User.Role.ENTREPRENEUR:
        messages.info(request, "Mentor discovery is available to entrepreneur accounts.")
        return redirect("dashboard")

    mentors = User.objects.filter(
        role=User.Role.MENTOR,
        is_active=True,
    ).order_by("first_name", "last_name", "username")

    return render(request, "mentorships/mentor_list.html", {"mentors": mentors})


@login_required
def request_mentorship(request, mentor_id):
    if request.user.role != User.Role.ENTREPRENEUR:
        messages.info(request, "Only entrepreneurs can send mentorship requests.")
        return redirect("dashboard")

    mentor = get_object_or_404(
        User,
        pk=mentor_id,
        role=User.Role.MENTOR,
        is_active=True,
    )
    existing_request = MentorshipRequest.objects.filter(
        entrepreneur=request.user,
        mentor=mentor,
    ).first()
    can_submit = (
        existing_request is None
        or existing_request.status == MentorshipRequest.Status.DECLINED
    )

    if request.method == "POST":
        if not can_submit:
            messages.info(request, "You already have an active request with this mentor.")
            return redirect("mentorship_requests")

        form = MentorshipRequestForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                mentorship_request, created = MentorshipRequest.objects.get_or_create(
                    entrepreneur=request.user,
                    mentor=mentor,
                    defaults={"message": form.cleaned_data["message"]},
                )
                if not created and mentorship_request.status == MentorshipRequest.Status.DECLINED:
                    mentorship_request.message = form.cleaned_data["message"]
                    mentorship_request.status = MentorshipRequest.Status.PENDING
                    mentorship_request.save(
                        update_fields=("message", "status", "updated_at")
                    )
                    created = True

            if created:
                actor_name = request.user.get_full_name() or request.user.username
                Notification.objects.create(
                    recipient=mentor,
                    actor=request.user,
                    message=f"{actor_name} sent you a mentorship request.",
                    link=reverse("mentorship_requests"),
                )
                messages.success(request, "Your mentorship request has been sent.")
            else:
                messages.info(request, "You already have an active request with this mentor.")
            return redirect("mentorship_requests")
    else:
        form = MentorshipRequestForm() if can_submit else None

    return render(
        request,
        "mentorships/request_form.html",
        {
            "mentor": mentor,
            "existing_request": existing_request,
            "can_submit": can_submit,
            "form": form,
        },
    )


@login_required
def mentorship_requests(request):
    if request.user.role == User.Role.ENTREPRENEUR:
        requests = MentorshipRequest.objects.filter(
            entrepreneur=request.user
        ).select_related("mentor")
        is_mentor = False
    elif request.user.role == User.Role.MENTOR:
        requests = MentorshipRequest.objects.filter(
            mentor=request.user
        ).select_related("entrepreneur")
        is_mentor = True
    else:
        messages.info(request, "Mentorship requests are available to entrepreneurs and mentors.")
        return redirect("dashboard")

    return render(
        request,
        "mentorships/requests.html",
        {"mentorship_requests": requests, "is_mentor": is_mentor},
    )


@login_required
@require_POST
def respond_to_mentorship_request(request, request_id):
    if request.user.role != User.Role.MENTOR:
        messages.error(request, "Only mentors can respond to mentorship requests.")
        return redirect("dashboard")

    mentorship_request = get_object_or_404(
        MentorshipRequest,
        pk=request_id,
        mentor=request.user,
    )
    if mentorship_request.status != MentorshipRequest.Status.PENDING:
        messages.info(request, "This request has already been reviewed.")
        return redirect("mentorship_requests")

    decision = request.POST.get("decision")
    if decision not in {
        MentorshipRequest.Status.ACCEPTED,
        MentorshipRequest.Status.DECLINED,
    }:
        messages.error(request, "Choose whether to accept or reject this request.")
        return redirect("mentorship_requests")

    mentorship_request.status = decision
    mentorship_request.save(update_fields=("status", "updated_at"))
    if decision == "accepted":
        Connection.ensure_accepted(mentorship_request.entrepreneur, request.user)
    mentor_name = request.user.get_full_name() or request.user.username
    Notification.objects.create(
        recipient=mentorship_request.entrepreneur,
        actor=request.user,
        message=f"Your mentorship request was {decision} by {mentor_name}.",
        link=reverse("mentorship_requests"),
    )
    messages.success(request, "Your response has been recorded.")
    return redirect("mentorship_requests")
