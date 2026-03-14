from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Count, Q
from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from elections.models import Election, Party
from voters.models import Voter
from candidate.models import Candidate
from voting.models import PartyVote

def school_admin_check(user):
    return user.is_superuser or user.groups.filter(name="SchoolAdmin").exists()

def admin_only(view_func):
    @login_required(login_url="login")
    def _wrapped(request, *args, **kwargs):
        if not school_admin_check(request.user):
            raise PermissionDenied
        return view_func(request, *args, **kwargs)
    return _wrapped

def parse_dt_local(val: str):
    if not val:
        return None
    dt = parse_datetime(val)
    if dt:
        return dt
    return parse_datetime(val.replace("T", " ") + ":00")

def get_active_election(request):
    return Election.objects.filter(is_active=True).first()
   
def get_latest_election():
    return Election.objects.order_by("-start_time").first()

@admin_only
def set_active_election(request):
    if request.method == "POST":
        election_id = request.POST.get("election_id")

        if election_id:
            Election.objects.update(is_active=False)

            election = Election.objects.get(id=election_id)
            election.is_active = True
            election.save()

            messages.success(request, "Active election selected successfully.")
        else:
            messages.error(request, "Please select an election.")

    return redirect("control_center:dashboard_home")

@admin_only
def dashboard_home(request):
    if not Election.objects.exists():
        return render(request, "control_center/dashboard.html", {
            "election": None,
            "phase": None,
            "total_voters": 0,
            "votes_cast": 0,
            "turnout": 0,
            "pending_candidates": 0,
            "party_counts": [],
            "needs_election_create": True,
            "needs_active_election": False,
        })

    election = get_active_election(request)
    if not election:
        return render(request, "control_center/dashboard.html", {
            "election": None,
            "phase": None,
            "total_voters": 0,
            "votes_cast": 0,
            "turnout": 0,
            "pending_candidates": Candidate.objects.filter(approved=False).count(),
            "party_counts": [],
            "needs_election_create": False,
            "needs_active_election": True,
        })

    context = {
        "election": election,
        "phase": election.phase(),
        "total_voters": 0,
        "votes_cast": 0,
        "turnout": 0,
        "pending_candidates": Candidate.objects.filter(approved=False).count(),
        "party_counts": [],
        "needs_election_create": False,
        "needs_active_election": False,
    }

    total_voters = Voter.objects.count()
    votes_cast = PartyVote.objects.filter(election=election).count()

    context["total_voters"] = total_voters
    context["votes_cast"] = votes_cast
    context["turnout"] = round((votes_cast / total_voters) * 100, 2) if total_voters else 0

    context["party_counts"] = (
        PartyVote.objects
        .filter(election=election)
        .values("party__name")
        .annotate(total=Count("id"))
        .order_by("-total")
    )

    return render(request, "control_center/dashboard.html", context)

@admin_only
def live_monitor(request):
    election = get_active_election(request)
    if not election:
        messages.info(request, "Please select an active election first.")
        return redirect("control_center:election_manage")

    context = {
        "election": election,
        "phase": None,
        "total_voters": 0,
        "votes_cast": 0,
        "turnout": 0,
        "party_counts": [],
    }

    if election:
        context["phase"] = election.phase()

        total_voters = Voter.objects.count()
        votes_cast = PartyVote.objects.filter(election=election).count()

        context["total_voters"] = total_voters
        context["votes_cast"] = votes_cast
        context["turnout"] = round((votes_cast / total_voters) * 100, 2) if total_voters else 0

        context["party_counts"] = (
            PartyVote.objects
            .filter(election=election)
            .values("party__name")
            .annotate(total=Count("id"))
            .order_by("-total")
        )

    return render(request, "control_center/live_monitor.html", context)


@admin_only
def voters_list(request):
    q = request.GET.get("q", "").strip()
    class_name = request.GET.get("class", "").strip()
    section = request.GET.get("section", "").strip()

    voters = Voter.objects.all().order_by("class_name", "section", "roll_number")

    if q:
        voters = voters.filter(Q(user__username__icontains=q) | Q(roll_number__icontains=q))

    if class_name:
        voters = voters.filter(class_name__iexact=class_name)

    if section:
        voters = voters.filter(section__iexact=section)

    context = {
        "voters": voters,
        "q": q,
        "class_name": class_name,
        "section": section,
        "total": voters.count(),
    }
    return render(request, "control_center/voters_list.html", context)


@admin_only
def candidates_approval(request):
    if request.method == "POST":
        candidate_id = request.POST.get("candidate_id")
        action = request.POST.get("action")

        cand = get_object_or_404(Candidate, id=candidate_id)

        if action == "approve":
            cand.approved = True
            cand.save()
            messages.success(request, f"Approved candidate: {cand.user.username}")
        elif action == "unapprove":
            cand.approved = False
            cand.save()
            messages.warning(request, f"Unapproved candidate: {cand.user.username}")

        return redirect("control_center:candidates_approval")

    q = request.GET.get("q", "").strip()
    class_name = request.GET.get("class", "").strip()
    section = request.GET.get("section", "").strip()
    status = request.GET.get("status", "").strip()

    candidates = Candidate.objects.select_related("user", "party").order_by(
        "approved", "class_name", "section", "party__name", "slot"
    )

    if q:
        candidates = candidates.filter(Q(user__username__icontains=q) | Q(party__name__icontains=q))

    if class_name:
        candidates = candidates.filter(class_name__iexact=class_name)

    if section:
        candidates = candidates.filter(section__iexact=section)

    if status == "pending":
        candidates = candidates.filter(approved=False)
    elif status == "approved":
        candidates = candidates.filter(approved=True)

    context = {
        "candidates": candidates,
        "q": q,
        "class_name": class_name,
        "section": section,
        "status": status,
        "total": candidates.count(),
        "pending_total": Candidate.objects.filter(approved=False).count(),
    }
    return render(request, "control_center/candidates_approval.html", context)

@admin_only
def election_manage(request):
    elections = Election.objects.order_by("-start_time")
    create_mode = request.GET.get("create") == "1"
    edit_id = request.GET.get("edit")

    active = get_active_election(request)

    election = None
    if not create_mode:
        if edit_id:
            election = Election.objects.filter(id=edit_id).first()
        elif active:
            election = active
        else:
            election = elections.first()

    if request.method == "POST":
        action = request.POST.get("action", "save")

        title = (request.POST.get("title") or "").strip()
        cs = parse_dt_local(request.POST.get("candidate_start"))
        ce = parse_dt_local(request.POST.get("candidate_end"))
        vs = parse_dt_local(request.POST.get("voting_start"))
        ve = parse_dt_local(request.POST.get("voting_end"))

        if not title:
            messages.error(request, "Election title is required.")
            return redirect("control_center:election_manage" + ("?create=1" if action == "create" else ""))

        if not (cs and ce and vs and ve):
            messages.error(request, "All date/time fields are required.")
            return redirect("control_center:election_manage" + ("?create=1" if action == "create" else ""))

        if not (cs <= ce):
            messages.error(request, "Candidate End must be after Candidate Start.")
            return redirect("control_center:election_manage" + ("?create=1" if action == "create" else ""))

        if not (vs <= ve):
            messages.error(request, "Voting End must be after Voting Start.")
            return redirect("control_center:election_manage" + ("?create=1" if action == "create" else ""))

        if ce > vs:
            messages.error(request, "Voting Start should be after Candidate End.")
            return redirect("control_center:election_manage" + ("?create=1" if action == "create" else ""))

        if action == "create":
            new_election = Election.objects.create(
                title=title,
                start_time=cs,
                end_time=ve,
                candidate_start=cs,
                candidate_end=ce,
                voting_start=vs,
                voting_end=ve,
            )
            Election.objects.update(is_active=False)
            new_election.is_active = True
            new_election.save()
            messages.success(request, "Election created and set as active.")
            return redirect("control_center:election_manage")

        eid = request.POST.get("election_id")
        election = Election.objects.filter(id=eid).first() if eid else election
        if not election:
            messages.error(request, "No election selected to update.")
            return redirect("control_center:election_manage")

        election.title = title
        election.start_time = cs
        election.end_time = ve
        election.candidate_start = cs
        election.candidate_end = ce
        election.voting_start = vs
        election.voting_end = ve
        election.save()

        messages.success(request, "Election updated.")
        return redirect("control_center:election_manage")

    return render(request, "control_center/election_manage.html", {
        "election": election,
        "phase": election.phase() if election else None,
        "create_mode": create_mode,
        "elections": elections,
        "active": active,
    })


@admin_only
def parties_manage(request):
    election = get_active_election(request)
    if not election:
        messages.info(request, "Please set an active election first from Election Management.")
        return redirect("control_center:election_manage")

    if request.method == "POST":
        action = request.POST.get("action")

        if action == "add":
            name = (request.POST.get("name") or "").strip()
            color = (request.POST.get("color") or "").strip()

            if not name:
                messages.error(request, "Party name is required.")
                return redirect("control_center:parties_manage")

            Party.objects.create(
                election=election,
                name=name,
                color=color if color else None,
            )
            messages.success(request, f"Party '{name}' added.")
            return redirect("control_center:parties_manage")

        if action == "delete":
            party_id = request.POST.get("party_id")
            party = get_object_or_404(Party, id=party_id, election=election)
            pname = party.name
            party.delete()
            messages.warning(request, f"Party '{pname}' deleted.")
            return redirect("control_center:parties_manage")

    parties = Party.objects.filter(election=election).order_by("name")

    return render(
        request,
        "control_center/parties_manage.html",
        {
            "election": election,
            "phase": election.phase(),
            "parties": parties,
            "total": parties.count(),
        },
    )

@admin_only
def reports_home(request):
    election = get_active_election(request)
    if not election:
        messages.info(request, "Please select an active election first.")
        return redirect("control_center:election_manage")

    context = {
        "election": election,
        "phase": None,
        "total_voters": 0,
        "votes_cast": 0,
        "turnout": 0,
        "party_counts": [],
        "winner_party": None,
        "is_tie": False,
    }

    if election:
        context["phase"] = election.phase()

        total_voters = Voter.objects.count()
        votes_cast = PartyVote.objects.filter(election=election).count()

        context["total_voters"] = total_voters
        context["votes_cast"] = votes_cast
        context["turnout"] = round((votes_cast / total_voters) * 100, 2) if total_voters else 0

        party_counts = (
            PartyVote.objects
            .filter(election=election)
            .values("party__id", "party__name")
            .annotate(total=Count("id"))
            .order_by("-total")
        )
        context["party_counts"] = party_counts

        if party_counts:
            if len(party_counts) > 1 and party_counts[0]["total"] == party_counts[1]["total"]:
                context["is_tie"] = True
            else:
                context["winner_party"] = Party.objects.get(id=party_counts[0]["party__id"])

    return render(request, "control_center/reports_home.html", context)
