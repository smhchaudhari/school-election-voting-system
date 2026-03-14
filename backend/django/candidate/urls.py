from django.urls import path
from . import views

app_name = "candidate"

urlpatterns = [
    
    path("", views.candidate_list, name="list"),
    path("dashboard/", views.candidate_dashboard, name="dashboard"),
    path("apply/", views.candidate_apply, name="apply"),
    path("<int:id>/", views.candidate_detail, name="detail"),
]
