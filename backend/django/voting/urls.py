from django.urls import path
from . import views

app_name = "voting"

urlpatterns = [
    path("<int:election_id>/", views.vote_page, name="vote_page"),
    path("already-voted/", views.already_voted, name="already_voted"),
    path('vote-success/', views.vote_success, name='vote_success'),
]
