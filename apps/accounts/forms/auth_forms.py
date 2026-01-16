from django import forms
from django.contrib.auth.models import User
#todo nie bede pisał wiecej tego co najwyżej zrobie samo todo jak zobacze
#todo Nie używaj django.contrib.auth.models.User “na sztywno”
"""

"""
from django.contrib.auth import get_user_model
User = get_user_model()
#todo to zastępuje a masz luźne wiązanie wiec jak cos zmienisz usera to nie wypieprza ci sie projekt

class LoginViewForm(forms.Form):
#todo Jeśli nie potrzebujesz custom logiki, to warto dziedziczyć po AuthenticationForm zamiast tworzyć od zera.
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'input input-bordered w-full'
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'input input-bordered w-full'
        })
    )


class RegisterViewForm(forms.Form):
    #todo stała CSS_INPUT = "input input-bordered w-full" zamiast z palca wrzucać
    username = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'input input-bordered w-full'})
    )
    first_name = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'input input-bordered w-full'})
    )
    last_name = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'input input-bordered w-full'})
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'input input-bordered w-full'})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'input input-bordered w-full'})
    )
    password2 = forms.CharField(
        label='Confirm Password',
        widget=forms.PasswordInput(attrs={'class': 'input input-bordered w-full'})
    )

    def clean(self):
        cleaned = super().clean()

        if cleaned.get("password") != cleaned.get("password2"):
            raise forms.ValidationError("Passwords don't match.")

        if User.objects.filter(username=cleaned.get("username")).exists():
            #todo lepiej przy polu , albo w metodzie clean_username niz w metodzie clean
            raise forms.ValidationError("User with this username already exists.")

        return cleaned


class PasswordChangeForm(forms.Form):
    old_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'input input-bordered w-full'})
    )
    new_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'input input-bordered w-full'})
    )
    new_password_2 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'input input-bordered w-full'})
    )

    def __init__(self, *args, user=None, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)
    # todo
    """
    PasswordChangeForm: ryzyko, że user będzie None
    Jeśli ktoś zapomni przekazać user=..., self.user.check_password() wywali wyjątek.
    Zabezpieczenie:
        albo user wymagany,
        albo w __init__ rzucić błąd, jeśli user is None.
    """
    def clean_old_password(self):
        old_password = self.cleaned_data.get('old_password')
        if not self.user.check_password(old_password):
            raise forms.ValidationError("Old password is incorrect.")
        return old_password

    def clean(self):
        cleaned = super().clean()
        new = cleaned.get("new_password")
        new2 = cleaned.get("new_password_2")
        if new and new2 and new != new2:
            raise forms.ValidationError("New passwords do not match.")
        return cleaned


#todo
"""
Django ma wbudowane walidatory haseł (AUTH_PASSWORD_VALIDATORS). W Twoich formach:
nie sprawdzasz minimalnej siły hasła
nie używasz password_validation.validate_password
To jest ważne, bo inaczej polityka haseł z settingsów nie działa.
"""