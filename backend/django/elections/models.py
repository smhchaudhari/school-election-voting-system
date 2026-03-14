from django.utils import timezone
from django.db import models

class Election(models.Model):
    title = models.CharField(max_length=200)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()

    # Candidate window
    candidate_start = models.DateTimeField()
    candidate_end = models.DateTimeField()

    # Voting window
    voting_start = models.DateTimeField()
    voting_end = models.DateTimeField()

    is_active = models.BooleanField(default=False)

    def phase(self):
        now = timezone.now()
        if now < self.candidate_start:
            return "UPCOMING"
        if self.candidate_start <= now <= self.candidate_end:
            return "CANDIDATE"
        if self.candidate_end < now < self.voting_start:
            return "GAP"
        if self.voting_start <= now <= self.voting_end:
            return "VOTING"
        return "RESULTS"
    

    def __str__(self):
        return self.title


class Party(models.Model):
    election = models.ForeignKey("Election", on_delete=models.CASCADE, related_name="parties")
    name = models.CharField(max_length=100)
    symbol = models.ImageField(upload_to="party_symbols/", blank=True, null=True)  # optional
    color = models.CharField(max_length=20, blank=True, null=True)  # optional like "#0d6efd"

    class Meta:
        unique_together = ("election", "name")

    def __str__(self):
        return f"{self.name} - {self.election}"
