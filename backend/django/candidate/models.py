from django.db import models
from django.core.exceptions import ValidationError
from elections.models import Party
from django.contrib.auth.models import User

class Candidate(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    party = models.ForeignKey(Party, on_delete=models.CASCADE, related_name="candidates", null=True, blank=True)
 
    class_name = models.CharField(max_length=20)
    section = models.CharField(max_length=10)

    photo = models.ImageField(upload_to="candidate_photos/", blank=True, null=True)
    manifesto = models.TextField()
    
    SLOT_CHOICES = (
        (1, "Candidate 1"),
        (2, "Candidate 2")
    )
    slot = models.IntegerField(choices = SLOT_CHOICES)

    approved = models.BooleanField(default=False)

    class Meta:
        unique_together = ("party" , "class_name", "section", "slot")

    def clean(self):
        qs = Candidate.objects.filter(
            party = self.party,
            class_name=self.class_name,
            section=self.section
        )
        if self.pk:
            qs = qs.exclude(pk=self.pk)

        if qs.count() >= 2:
            raise ValidationError(
                "Only 2 candidated allowed per party per class_section"
            )
        

    def __str__(self):
        return f"{self.user.username} | {self.class_name}-{self.section} | {self.party.name}"
