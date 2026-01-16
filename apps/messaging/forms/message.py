from django import forms


class MessageForm(forms.Form):
    text = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'textarea textarea-neutral',
            'rows': 3,
        }),
        label="Message",
        max_length=10000,
    )
#todo znow nie wiem dlaczego nei modelform