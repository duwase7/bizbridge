from django.urls import path

from . import views

urlpatterns = [
    path("", views.admin_dashboard, name="admin_dashboard"),
    path("report.csv", views.report_csv, name="admin_report_csv"),
    path("users/", views.user_list, name="admin_users"),
    path("users/<int:user_id>/action/", views.user_action, name="admin_user_action"),
    path("opportunities/", views.opportunity_admin_list, name="admin_opportunities"),
    path("opportunities/new/", views.opportunity_edit, name="admin_opportunity_create"),
    path("opportunities/<int:pk>/edit/", views.opportunity_edit, name="admin_opportunity_edit"),
    path("opportunities/<int:pk>/delete/", views.opportunity_delete, name="admin_opportunity_delete"),
]
