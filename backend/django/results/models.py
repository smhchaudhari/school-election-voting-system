from django.db import models
from elections.models import Election
from elections.models import Party

class Result(models.Model):
    election = models.ForeignKey(Election, on_delete=models.CASCADE)
    party = models.ForeignKey(Party, on_delete=models.CASCADE)
    vote_count = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.party.name} - {self.vote_count}"
