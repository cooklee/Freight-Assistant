from django import forms
from django.contrib.auth.models import User
# TODO: Nie importu usera bez pośrednio

from apps.accounts.models import AppUser
# TODO: troche nie potrzebnie skomplikowane jakbys miał customUsera problem byłby rozwiązany


class ConversationForm(forms.Form):
    user2 = forms.ModelChoiceField(
        queryset=User.objects.none(),
        # TODO: queryset startowy jest User.objects.none(), ale później ustawiasz AppUser queryset.
        #       Jeśli AppUser != User, to może być mylące dla czytelności
        label="Recipient",
        empty_label='Choose recipient',
        # TODO: Dla spójności stylistycznej w projekcie warto ujednolicić cudzysłowy (" vs ').
        widget=forms.Select(attrs={
            "class": "select select-bordered w-full",
            # TODO: Jeśli używasz DaisyUI/Tailwind, OK. Upewnij się, że select ma poprawne klasy pod walidację błędów.
        }),
    )
    subject = forms.CharField(
        max_length=255,
        required=False,
        # TODO: required=False → subject może być pusty; upewnij się,
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
        # TODO: kwargs.pop("request_user") bez defaultu rzuci KeyError, jeśli ktoś zapomni przekazać argument.
        #       Jeśli to celowe, warto to opisać w docstringu klasy/formularza.
        super().__init__(*args, **kwargs)

        self.fields["user2"].queryset = AppUser.objects.exclude(id=request_user.id)
        # TODO: Jeśli AppUser ma pole is_active, często warto dodać .filter(is_active=True), żeby nie wysyłać do nieaktywnych.


#todo nie dokonca rozumiem dlaczego nie używasz modelform
