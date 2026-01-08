from django import forms
from django.contrib.auth.models import User


class LoginViewForm(forms.Form):
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
