from django.db import models
from django.contrib.auth.models import User
from elections.models import Election, Party   

class PartyVote(models.Model):
    voter = models.ForeignKey(User, on_delete=models.CASCADE)
    election = models.ForeignKey(Election, on_delete=models.CASCADE)
    party = models.ForeignKey(Party, on_delete=models.CASCADE)
    cast_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("voter", "election")  # one vote gper election

    def __str__(self):
        return f"{self.voter.username} voted for {self.party.name} in {self.election.title}"
