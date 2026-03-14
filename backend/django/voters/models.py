from django.db import models
from django.contrib.auth.models import User

class Voter(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    roll_number = models.CharField(max_length=20, unique=True)
    class_name = models.CharField(max_length=20)
    section = models.CharField(max_length=10)

    has_voted = models.BooleanField(default=False) 

    def __str__(self):
        return f"{self.user.username} ({self.roll_number})"
