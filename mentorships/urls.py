from django.urls import path

from . import views

urlpatterns = [
    path("mentors/", views.mentor_directory, name="mentor_directory"),
    path(
        "mentors/<int:mentor_id>/request/",
        views.request_mentorship,
        name="request_mentorship",
    ),
    path("requests/", views.mentorship_requests, name="mentorship_requests"),
    path(
        "requests/<int:request_id>/respond/",
        views.respond_to_mentorship_request,
        name="respond_to_mentorship_request",
    ),
]
