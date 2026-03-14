from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Voter
from .forms import VoterForm
from elections.utils import get_current_phase
from elections.models import Party
from voting.models import PartyVote
from django.shortcuts import get_object_or_404

@login_required
def voter_profile(request):
    election, phase = get_current_phase()
    print("ELECTION:", election, "PHASE:", phase)
    voter = Voter.objects.filter(user=request.user).first()
    print("VOTER:", voter, "HAS_VOTED:", voter.has_voted if voter else None)
    if not election:
        messages.warning(request, "No active election right now.")
        return redirect("status")


    already_voted = PartyVote.objects.filter(
        voter=request.user,
        election=election
    ).exists()

    if voter and already_voted:
        return redirect("voting:already_voted")

    if voter and not already_voted:
        return redirect("voting:vote_page", election_id=election.id)
    
    if request.method == "POST":
        form = VoterForm(request.POST)

        if form.is_valid():
            voter = form.save(commit=False)
            voter.user = request.user
            voter.save()

            messages.success(request, "Voter profile created successfully!")

            
            return redirect("voting:vote_page", election_id=election.id)

            

    else:
        form = VoterForm()

    return render(request, "voter/profile.html", {
        "form": form,
        "election": election,
        "role": "Voter"
    })

def confirm_vote(request):
    if request.method == "POST":
        messages.success(request, "You have successfully voted!")
        return redirect("status")  