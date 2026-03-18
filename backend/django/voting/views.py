from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.contrib import messages

from elections.models import Party
from elections.models import Election
from candidate.models import Candidate
from .models import PartyVote
from results.models import Result
from elections.utils import get_current_phase
from voters.models import Voter

@login_required
def vote_page(request, election_id):
    
    election = get_object_or_404(Election, id=election_id)
    print("PAGE OPENED ELECTION",election_id)
    phase = election.phase()
    if phase not in ["VOTING", "VOTING_PERIOD"]:
        return redirect("status")

    now = timezone.now()
    if now < election.start_time:
        return render(request, "voting/not_active.html", {"election": election})

    if timezone.now() > election.end_time:
        return render(request, "voting/closed.html", {"election": election})
    
    voter = get_object_or_404(Voter, user=request.user)

    already_voted = PartyVote.objects.filter(
    voter=request.user,
    election=election
    ).exists()

    if already_voted:
        messages.warning(request, "You have already voted in this election.")
        return redirect("voting:already_voted")
    parties = Party.objects.filter(election=election)

    if request.method == "POST":

        print("POST REQUEST ELECTION", election_id)

        party_id = request.POST.get("party")

        if not party_id:
            messages.error(request, "Please select a party.")
            return redirect(request.path)
        
        selected_party = get_object_or_404(Party, id=party_id, election=election)

        PartyVote.objects.create(
            voter=request.user,
            election=election,
            party=selected_party
            

        )
        
        result, created = Result.objects.get_or_create(
            election=election,
            party=selected_party
        )
        result.vote_count += 1
        result.save()
            
        messages.success(request, "Vote submitted successfully!")
        return redirect("voting:vote_success")

    return render(request, "voter/vote.html", {
        "election": election,
        "parties": parties
    })

@login_required
def already_voted(request):
    return render(request, "voter/already_voted.html")

@login_required
def vote_success(request):
    return render(request, 'voter/vote_success.html')

