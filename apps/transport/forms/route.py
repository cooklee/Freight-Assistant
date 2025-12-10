from django import forms
from ..models import Route
class RouteForm(forms.ModelForm):
    class Meta:
        model = Route
        fields = ["name"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "input input-bordered w-full"}),
        }

