from django.urls import path

from . import views

urlpatterns = [
    path("investors/", views.investor_directory, name="investor_directory"),
    path(
        "investors/<int:investor_id>/request/",
        views.request_investor_connection,
        name="request_investor_connection",
    ),
    path(
        "requests/",
        views.investor_connection_requests,
        name="investor_connection_requests",
    ),
    path(
        "requests/<int:request_id>/respond/",
        views.respond_to_investor_request,
        name="respond_to_investor_request",
    ),
]
