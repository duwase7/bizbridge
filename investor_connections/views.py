from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_POST

from accounts.models import User
from networking.models import Connection
from notifications.models import Notification

from .forms import InvestorConnectionRequestForm
from .models import InvestorConnectionRequest


@login_required
def investor_directory(request):
    if request.user.role != User.Role.ENTREPRENEUR:
        messages.info(request, "Investor discovery is available to entrepreneur accounts.")
        return redirect("dashboard")

    query = request.GET.get("q", "").strip()
    investors = User.objects.filter(
        role=User.Role.INVESTOR,
        is_active=True,
    )
    if query:
        investors = investors.filter(
            Q(first_name__icontains=query)
            | Q(last_name__icontains=query)
            | Q(username__icontains=query)
            | Q(organization__icontains=query)
            | Q(location__icontains=query)
            | Q(bio__icontains=query)
        )

    return render(
        request,
        "investor_connections/investor_list.html",
        {"investors": investors.order_by("organization", "first_name", "username"), "query": query},
    )


@login_required
def request_investor_connection(request, investor_id):
    if request.user.role != User.Role.ENTREPRENEUR:
        messages.info(request, "Only entrepreneurs can initiate investor connection requests.")
        return redirect("dashboard")

    investor = get_object_or_404(
        User,
        pk=investor_id,
        role=User.Role.INVESTOR,
        is_active=True,
    )
    existing_request = InvestorConnectionRequest.objects.filter(
        entrepreneur=request.user,
        investor=investor,
    ).first()
    can_submit = (
        existing_request is None
        or existing_request.status == InvestorConnectionRequest.Status.DECLINED
    )

    if request.method == "POST":
        if not can_submit:
            messages.info(request, "You already have an active request with this investor.")
            return redirect("investor_connection_requests")

        form = InvestorConnectionRequestForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                connection_request, created = InvestorConnectionRequest.objects.get_or_create(
                    entrepreneur=request.user,
                    investor=investor,
                    defaults={"message": form.cleaned_data["message"]},
                )
                if (
                    not created
                    and connection_request.status == InvestorConnectionRequest.Status.DECLINED
                ):
                    connection_request.message = form.cleaned_data["message"]
                    connection_request.status = InvestorConnectionRequest.Status.PENDING
                    connection_request.save(
                        update_fields=("message", "status", "updated_at")
                    )
                    created = True

            if created:
                actor_name = request.user.get_full_name() or request.user.username
                Notification.objects.create(
                    recipient=investor,
                    actor=request.user,
                    message=f"{actor_name} sent you an investor connection request.",
                    link=reverse("investor_connection_requests"),
                )
                messages.success(request, "Your investor connection request has been sent.")
            else:
                messages.info(request, "You already have an active request with this investor.")
            return redirect("investor_connection_requests")
    else:
        form = InvestorConnectionRequestForm() if can_submit else None

    return render(
        request,
        "investor_connections/request_form.html",
        {
            "investor": investor,
            "existing_request": existing_request,
            "can_submit": can_submit,
            "form": form,
        },
    )


@login_required
def investor_connection_requests(request):
    if request.user.role == User.Role.ENTREPRENEUR:
        requests = InvestorConnectionRequest.objects.filter(
            entrepreneur=request.user
        ).select_related("investor")
        is_investor = False
    elif request.user.role == User.Role.INVESTOR:
        requests = InvestorConnectionRequest.objects.filter(
            investor=request.user
        ).select_related("entrepreneur")
        is_investor = True
    else:
        messages.info(
            request,
            "Investor connection requests are available to entrepreneurs and investors.",
        )
        return redirect("dashboard")

    return render(
        request,
        "investor_connections/requests.html",
        {"connection_requests": requests, "is_investor": is_investor},
    )


@login_required
@require_POST
def respond_to_investor_request(request, request_id):
    if request.user.role != User.Role.INVESTOR:
        messages.error(request, "Only investors can respond to investor connection requests.")
        return redirect("dashboard")

    connection_request = get_object_or_404(
        InvestorConnectionRequest,
        pk=request_id,
        investor=request.user,
    )
    if connection_request.status != InvestorConnectionRequest.Status.PENDING:
        messages.info(request, "This request has already been reviewed.")
        return redirect("investor_connection_requests")

    decision = request.POST.get("decision")
    if decision not in {
        InvestorConnectionRequest.Status.ACCEPTED,
        InvestorConnectionRequest.Status.DECLINED,
    }:
        messages.error(request, "Choose whether to accept or decline this request.")
        return redirect("investor_connection_requests")

    connection_request.status = decision
    connection_request.save(update_fields=("status", "updated_at"))
    if decision == "accepted":
        Connection.ensure_accepted(connection_request.entrepreneur, request.user)
    investor_name = request.user.get_full_name() or request.user.username
    Notification.objects.create(
        recipient=connection_request.entrepreneur,
        actor=request.user,
        message=f"Your investor connection request was {decision} by {investor_name}.",
        link=reverse("investor_connection_requests"),
    )
    messages.success(request, "Your response has been recorded.")
    return redirect("investor_connection_requests")
