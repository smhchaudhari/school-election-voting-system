from django.urls import path
from .views import voter_profile, confirm_vote

app_name='voter'

urlpatterns = [
    path("profile/", voter_profile, name="voter_profile"),
    path("confirm-vote/", confirm_vote, name="confirm_vote"),
]