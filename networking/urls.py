from django.urls import path

from . import views

urlpatterns = [
    path("network/", views.connection_list, name="connection_list"),
    path("network/connect/<int:user_id>/", views.send_connection_request, name="send_connection_request"),
    path("network/<int:pk>/respond/", views.respond_to_connection, name="respond_to_connection"),
    path("messages/", views.inbox, name="inbox"),
    path("messages/<int:pk>/", views.conversation, name="conversation"),
    path("messages/with/<int:user_id>/", views.start_conversation, name="start_conversation"),
]
