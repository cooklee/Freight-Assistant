from django import forms
from django.contrib.auth.models import User

from apps.accounts.models import AppUser


class ConversationForm(forms.Form):
    user2 = forms.ModelChoiceField(
        queryset=User.objects.none(),
        label="Recipient",
        empty_label='Choose recipient',
        widget=forms.Select(attrs={
            "class": "select select-bordered w-full",
        }),
    )
    subject = forms.CharField(
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={
            "class": "input input-bordered w-full",
            "placeholder": "Conversation topic (optional)"
        }),
    )
    text = forms.CharField(
        widget=forms.Textarea(attrs={
            "class": "textarea textarea-neutral w-full min-h-32",
            "placeholder": "Write your first message..."
        }),
        label="Message",
    )

    def __init__(self, *args, **kwargs):
        request_user = kwargs.pop("request_user")
        super().__init__(*args, **kwargs)

        self.fields["user2"].queryset = AppUser.objects.exclude(id=request_user.id)
