from django.contrib import admin
from django.urls import path, include
from django.shortcuts import render
from django.views.generic import TemplateView
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static
from school_voting_system.admin_site import admin_site
from account.views import RoleBasedLoginView
from elections.views import status_page 
from django.shortcuts import redirect

def start(request):
    if request.user.is_authenticated:
        return redirect("status")  
    return redirect("login")       



def home(request):
    return render(request, "home.html")

urlpatterns = [
    path("admin/", admin_site.urls),
    path("control/", include("control_center.urls")),

    path("", TemplateView.as_view(template_name="home.html"), name="home"),
    path("about/", TemplateView.as_view(template_name="about.html"), name="about"),

    path("start/", start, name="start"),

    path("login/", RoleBasedLoginView.as_view(template_name="registration/login.html"), name="login"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),

    
    path("status/", status_page, name="status"),

    
    path("", home, name="home"),

    path(
        "accounts/login/",
        RoleBasedLoginView.as_view(template_name="registration/login.html"),
        name="account_login",
    ),
    path("accounts/logout/", auth_views.LogoutView.as_view(), name="account_logout"),

    path("accounts/", include("django.contrib.auth.urls")),
    path("vote/", include("voting.urls")),
    path("results/", include(("results.urls", "results"), namespace="results")),
    path("elections/", include("elections.urls")),
    path("candidates/", include("candidate.urls")),
    path("", include("account.urls")),
    path("voter/", include("voters.urls")),
    



]

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )

