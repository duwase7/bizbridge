from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Max, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_POST

from accounts.models import User
from accounts.views import searchable_roles_for
from notifications.models import Notification

from .forms import ConnectionRequestForm, MessageForm
from .models import Connection, Message


def _notify(recipient, actor, text, link):
    Notification.objects.create(recipient=recipient, actor=actor, message=text, link=link)


@login_required
@require_POST
def send_connection_request(request, user_id):
    """FR-16 with BR-03: no self-requests and no duplicate pending requests."""
    receiver = get_object_or_404(User, pk=user_id, is_active=True, is_staff=False)
    profile_url = reverse("person_detail", args=[receiver.pk])
    if receiver == request.user:
        messages.error(request, "You cannot send a connection request to yourself.")
        return redirect("dashboard")
    if receiver.role not in searchable_roles_for(request.user):
        messages.error(request, "Your role cannot connect with this account.")
        return redirect("people_directory")

    form = ConnectionRequestForm(request.POST)
    note = form.cleaned_data["note"] if form.is_valid() else ""
    existing = Connection.between(request.user, receiver)
    if existing and existing.status == Connection.Status.PENDING:
        messages.info(request, "A connection request between you is already pending.")
        return redirect(profile_url)
    if existing and existing.status == Connection.Status.ACCEPTED:
        messages.info(request, "You are already connected.")
        return redirect(profile_url)
    if existing:  # previously declined: send a fresh request
        existing.requester, existing.receiver = request.user, receiver
        existing.note, existing.status = note, Connection.Status.PENDING
        existing.save()
    else:
        Connection.objects.create(requester=request.user, receiver=receiver, note=note)

    _notify(
        receiver,
        request.user,
        f"{request.user.display_name} sent you a connection request.",
        reverse("connection_list"),
    )
    messages.success(request, f"Connection request sent to {receiver.display_name}.")
    return redirect(profile_url)


@login_required
def connection_list(request):
    connections = Connection.for_user(request.user).select_related("requester", "receiver")
    accepted = list(connections.filter(status=Connection.Status.ACCEPTED))
    for connection in accepted:
        connection.partner = connection.other(request.user)
    return render(
        request,
        "networking/connections.html",
        {
            "incoming": connections.filter(receiver=request.user, status=Connection.Status.PENDING),
            "outgoing": connections.filter(requester=request.user).exclude(status=Connection.Status.ACCEPTED),
            "accepted": accepted,
        },
    )


@login_required
@require_POST
def respond_to_connection(request, pk):
    """FR-17: the receiver accepts or declines; the requester sees the status."""
    connection = get_object_or_404(Connection, pk=pk, receiver=request.user)
    decision = request.POST.get("decision")
    if connection.status != Connection.Status.PENDING:
        messages.info(request, "This request has already been answered.")
        return redirect("connection_list")
    if decision not in (Connection.Status.ACCEPTED, Connection.Status.DECLINED):
        messages.error(request, "Choose accept or decline.")
        return redirect("connection_list")

    connection.status = decision
    connection.save(update_fields=("status", "updated_at"))
    _notify(
        connection.requester,
        request.user,
        f"{request.user.display_name} {decision} your connection request.",
        reverse("conversation", args=[connection.pk])
        if decision == Connection.Status.ACCEPTED
        else reverse("connection_list"),
    )
    messages.success(request, f"Connection {decision}.")
    return redirect("connection_list")


@login_required
def inbox(request):
    conversations = (
        Connection.for_user(request.user)
        .filter(status=Connection.Status.ACCEPTED)
        .select_related("requester", "receiver")
        .annotate(
            last_message_at=Max("messages__created_at"),
            unread=Count(
                "messages",
                filter=Q(messages__is_read=False) & ~Q(messages__sender=request.user),
            ),
        )
        .order_by("-last_message_at", "-updated_at")
    )
    for conversation in conversations:
        conversation.partner = conversation.other(request.user)
        conversation.last_message = conversation.messages.first()
    return render(request, "networking/inbox.html", {"conversations": conversations})


@login_required
def conversation(request, pk):
    """FR-20/FR-21 and BR-02: only accepted connections can exchange messages."""
    connection = get_object_or_404(Connection, pk=pk)
    if not connection.involves(request.user):
        messages.error(request, "You do not have access to that conversation.")
        return redirect("inbox")
    if connection.status != Connection.Status.ACCEPTED:
        messages.info(request, "You can message this person once your connection is accepted.")
        return redirect("connection_list")

    partner = connection.other(request.user)
    if request.method == "POST":
        form = MessageForm(request.POST)
        if form.is_valid():
            Message.objects.create(
                connection=connection, sender=request.user, content=form.cleaned_data["content"]
            )
            connection.save(update_fields=("updated_at",))
            _notify(
                partner,
                request.user,
                f"New message from {request.user.display_name}.",
                reverse("conversation", args=[connection.pk]),
            )
            return redirect("conversation", pk=connection.pk)
    else:
        form = MessageForm()

    connection.messages.filter(is_read=False).exclude(sender=request.user).update(is_read=True)
    return render(
        request,
        "networking/conversation.html",
        {
            "connection": connection,
            "partner": partner,
            "chat_messages": connection.messages.select_related("sender"),
            "form": form,
        },
    )


@login_required
def start_conversation(request, user_id):
    other = get_object_or_404(User, pk=user_id)
    connection = Connection.between(request.user, other)
    if connection and connection.status == Connection.Status.ACCEPTED:
        return redirect("conversation", pk=connection.pk)
    messages.info(request, "Messaging opens once a connection request is accepted.")
    return redirect("person_detail", user_id=other.pk)
