from django.db.models import Q

from .models import Message


def unread_message_count(request):
    user = request.user
    if not user.is_authenticated:
        return {"unread_message_count": 0}
    count = (
        Message.objects.filter(is_read=False)
        .filter(Q(connection__requester=user) | Q(connection__receiver=user))
        .exclude(sender=user)
        .count()
    )
    return {"unread_message_count": count}
