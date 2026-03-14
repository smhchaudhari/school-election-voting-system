from django import forms
from .models import Voter

class VoterForm(forms.ModelForm):
    class Meta:
        model = Voter
        fields = ["roll_number", "class_name", "section"]
        widgets = {
            "roll_number": forms.TextInput(attrs={"class": "form-control"}),
            "class_name": forms.TextInput(attrs={"class": "form-control"}),
            "section": forms.TextInput(attrs={"class": "form-control"}),
        }
