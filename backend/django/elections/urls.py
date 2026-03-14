from django.urls import path
from .views import status_page

app_name = "elections"

urlpatterns = [
    path("", status_page, name="status"),
]
