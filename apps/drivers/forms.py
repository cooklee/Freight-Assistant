from django import forms

from .models import Driver


class DriverForm(forms.ModelForm):
    class Meta:
        model = Driver
        exclude = ('carrier',)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'input input-bordered w-full'})
