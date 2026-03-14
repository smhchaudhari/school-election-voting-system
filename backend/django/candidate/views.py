from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from elections.utils import get_current_phase
from .models import Candidate
from .forms import CandidateForm
from django.utils import timezone
from django.shortcuts import get_object_or_404

@login_required
def candidate_list(request):
    election, phase = get_current_phase()

    if election:
        candidates = Candidate.objects.filter(party__election=election,approved=True)
    else:
        candidates = Candidate.objects.none()

    return render(request, "candidate/list.html", {
        "candidates": candidates,
        "election": election
    })


@login_required
def candidate_apply(request):
    election, phase = get_current_phase()
    
    print("PHASE:", phase)
    print("NOW:", timezone.now())
    print("START:", election.candidate_start)
    print("END:", election.candidate_end)


    if phase != "CANDIDATE_REGISTRATION":
        return redirect("elections:status")

    existing = Candidate.objects.filter(user=request.user).first()
    if existing:
        return redirect("candidate:dashboard")

    if request.method == "POST":
        form = CandidateForm(request.POST, request.FILES,election=election)
        if form.is_valid():
            candidate = form.save(commit=False)
            candidate.user = request.user
            candidate.approved = False
            candidate.save()  
            messages.success(request, "Application submitted! Wait for admin approval.")
            return redirect("candidate:dashboard")
    else:
        form = CandidateForm(election=election)

    return render(request, "candidate/apply.html", {"form": form})

def candidate_dashboard(request):
    election, phase = get_current_phase()
    phase = phase.upper()

    if phase != "CANDIDATE_REGISTRATION":
        return redirect("elections:status")


    candidate = Candidate.objects.filter(user=request.user).first()
    if not candidate:
        return redirect("candidate:apply")

    if request.method == "POST":
        form = CandidateForm(request.POST, request.FILES, instance=candidate, election=election)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully.")
            return redirect("candidate:dashboard")
    else:
        form = CandidateForm(instance=candidate, election=election)

    return render(request, "candidate/dashboard.html", {
        "candidate": candidate,
        "form": form
    })

@login_required
def candidate_detail(request, id):
    candidate = get_object_or_404(Candidate, id=id, approved=True)

    return render(request, "candidate/detail.html", {
        "candidate": candidate
    })