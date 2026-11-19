from django.contrib import admin
from django.urls import include, path

from accounts import views as account_views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", account_views.home, name="home"),
    path("accounts/", include("accounts.urls")),
    path("opportunities/", include("opportunities.urls")),
    path("mentorship/", include("mentorships.urls")),
    path("connections/", include("investor_connections.urls")),
]
