from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Profile
from .forms import SignUpForm
from .models import Profile
from django.contrib.auth.views import LoginView
from django.urls import reverse
from django.utils.http import url_has_allowed_host_and_scheme
from django.conf import settings

def signup(request):
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Account created successfully.")
            return redirect("status")   
    else:
        form = SignUpForm()

    return render(request, "registration/signup.html", {"form": form})
    

@login_required
def choose_candidate(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)
    profile.role = "CANDIDATE"
    profile.save()
    return redirect("candidate:apply")   

@login_required
def choose_voter(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)
    profile.role = "VOTER"
    profile.save()
    return redirect("status")  

class RoleBasedLoginView(LoginView):
    template_name = "registration/login.html"

    def get_success_url(self):
        user = self.request.user

        
        if user.is_superuser or user.groups.filter(name="SchoolAdmin").exists():
            return reverse("control_center:dashboard_home")

        
        next_url = self.request.POST.get("next") or self.request.GET.get("next")
        if next_url and url_has_allowed_host_and_scheme(next_url, allowed_hosts={self.request.get_host()}):
            return next_url

        
        return reverse("status")