from django.urls import path
from .views import results_home, party_results
app_name = "results"
urlpatterns = [
    path("", results_home, name="results_home"),
    path("<int:election_id>/", party_results, name="results"),
]
