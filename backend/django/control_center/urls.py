from django.urls import path
from . import views

app_name = "control_center"

urlpatterns = [
    path("", views.dashboard_home, name="dashboard_home"),

    path("election/set-active/", views.set_active_election, name="set_active_election"),
    path("live/", views.live_monitor, name="live_monitor"),
    path("voters/", views.voters_list, name="voters_list"),
    path("candidates/", views.candidates_approval, name="candidates_approval"),
    path("election/", views.election_manage, name="election_manage"),
    path("parties/", views.parties_manage, name="parties_manage"),
    path("reports/", views.reports_home, name="reports_home"),

]