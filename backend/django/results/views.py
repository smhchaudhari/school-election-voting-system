from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from elections.models import Election, Party
from voting.models import PartyVote
from candidate.models import Candidate
from django.utils import timezone

@login_required
def party_results(request, election_id):
    election = get_object_or_404(Election, id=election_id)

    print("Current Time:", timezone.now())
    print("Voting End:", election.voting_end)

    if timezone.now() < election.voting_end:
        return render(request, "results/not_ready.html", {
            "election": election
        })

    counts = (
        PartyVote.objects
        .filter(election=election)
        .values("party__id", "party__name")
        .annotate(total=Count("id"))
        .order_by("-total")
    )

    total_votes = PartyVote.objects.filter(election=election).count()

    winning_party = None
    tie = False
    winning_margin = 0

    if counts:
        if len(counts) >= 2 and counts[0]["total"] == counts[1]["total"]:
            tie = True
        else:
            winning_party = Party.objects.get(id=counts[0]["party__id"])

        if len(counts) >= 2:
            winning_margin = counts[0]["total"] - counts[1]["total"]

    results = []
    for row in counts:
        percent = 0
        if total_votes > 0:
            percent = round((row["total"] / total_votes) * 100)

        results.append({
            "party_name": row["party__name"],
            "total": row["total"],
            "percent": percent
        })

    winners_by_class = []

    if winning_party and not tie:
        class_sections = (
            Candidate.objects
            .filter(party=winning_party, approved=True)
            .values("class_name", "section")
            .distinct()
            .order_by("class_name", "section")
        )

        for cs in class_sections:
            reps = (
                Candidate.objects
                .filter(
                    party=winning_party,
                    class_name=cs["class_name"],
                    section=cs["section"],
                    approved=True
                )
                .order_by("slot")
            )

            winners_by_class.append({
                "class_name": cs["class_name"],
                "section": cs["section"],
                "reps": reps
            })

    return render(request, "results/results.html", {
        "election": election,
        "results": results,
        "winner": winning_party,
        "tie": tie,
        "total_votes": total_votes,
        "winning_margin": winning_margin,
        "winners_by_class": winners_by_class
    })

@login_required
def results_home(request):
    elections = Election.objects.all().order_by("-id")
    return render(request, "results/home.html", {
        "elections": elections
    })