from django.urls import path
from .views import signup, choose_candidate, choose_voter, RoleBasedLoginView

urlpatterns = [
    path("signup/", signup, name="signup"),
    path("choose/candidate/", choose_candidate, name="choose_candidate"),
    path("choose/voter/", choose_voter, name="choose_voter"),
]