from django.utils import timezone
from .models import Election

def get_current_phase():
    today = timezone.now().date()

    election = Election.objects.last()

    if not election:
        return None, "NO_ELECTION"

    candidate_start = election.candidate_start.date()
    candidate_end = election.candidate_end.date()
    voting_start = election.voting_start.date()
    voting_end = election.voting_end.date()

    if candidate_start <= today <= candidate_end:
        phase = "CANDIDATE_REGISTRATION"

    elif voting_start <= today <= voting_end:
        phase = "VOTING"

    elif today > voting_end:
        phase = "RESULT"

    else:
        phase = "NOT_STARTED"

    return election, phase