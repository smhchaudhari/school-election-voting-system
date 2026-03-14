from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.utils import timezone
from account.models import Profile

from elections.models import Election


def _role_for(user):
    if user.is_staff or user.is_superuser:
        return "ADMIN"

    profile = Profile.objects.filter(user=user).first()
    if profile and profile.role:
        return profile.role

    return "GUEST"


@login_required
def status_page(request):
    role = _role_for(request.user)
    election = Election.objects.order_by("-id").first()

    if not election:
        return render(request, "elections/status.html", {
            "role": role,
            "election": None,
            "phase": "NO_ELECTION",
        })

    phase = election.phase()
    return render(request, "elections/status.html", {
        "role": role,
        "election": election,
        "phase": phase,
    })
