from django import forms
from .models import Candidate
from elections.models import Party


class CandidateForm(forms.ModelForm):

    class Meta:
        model = Candidate
        fields = ["party", "class_name", "section", "slot", "photo", "manifesto"]
        widgets = {
            "party": forms.Select(attrs={"class": "form-select"}),
            "class_name": forms.TextInput(attrs={"class": "form-control", "placeholder": "e.g. TYBCA"}),
            "section": forms.TextInput(attrs={"class": "form-control", "placeholder": "e.g. A"}),
            "slot": forms.Select(attrs={"class": "form-select"}),
            "manifesto": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 6,
                "placeholder": "Write your manifesto here..."
            }),
        }

    def __init__(self, *args, **kwargs):
        election = kwargs.pop("election", None)
        super().__init__(*args, **kwargs)

        if election:
            self.fields["party"].queryset = Party.objects.filter(election=election)