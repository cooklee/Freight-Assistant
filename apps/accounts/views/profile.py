from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect
from django.views import View

from apps.accounts.forms import UserProfileForm, PasswordChangeForm


class ProfileView(LoginRequiredMixin, View):
    def get(self, request):
        profile = request.user.profile
        form = UserProfileForm(instance=profile, user=request.user)
        password_form = PasswordChangeForm(user=request.user)
        return render(request, 'accounts/profile.html', {
            'form': form,
            'profile': profile,
            'password_form': password_form,
        })

    def post(self, request):
        #todo request.user.profile może nie istnieć, teoretycznie robisz to sygnałami ale moze sie zdarzyć jakiś fuckup w systemi i beda leciały błedy
        # lepiej sie zabezpieczyć przez profile, _ = UserProfile.objects.get_or_create(user=request.user)

        profile = request.user.profile
        # todo Rozpoznawanie “który formularz wysłano” po 'old_password' in request.POST
        # zdecydowanie lepiej miec dwa osobne end-pointy kazdy formularz prowadzi do osobnego endpointu
        if 'old_password' in request.POST:
            #todo Zmiana hasła: brak walidatorów haseł(nie używasz wbudowanych walidatorów)
            password_form = PasswordChangeForm(request.POST, user=request.user)
            form = UserProfileForm(instance=profile, user=request.user)
            if password_form.is_valid():
                new_password = password_form.cleaned_data['new_password']
                request.user.set_password(new_password)
                request.user.save()
                update_session_auth_hash(request, request.user)
                messages.success(request, 'Password changed successfully.')
                return redirect('profile')

        else:
            form = UserProfileForm(
                request.POST,
                request.FILES,
                instance=profile,
                user=request.user
            )
            password_form = PasswordChangeForm(user=request.user)
            if form.is_valid():
                form.save()
                #todo formularz sam zapisuje sobie dane do profilu wiec warto by i użytkownika sam updatował
                request.user.first_name = form.cleaned_data['first_name']
                request.user.last_name = form.cleaned_data['last_name']
                request.user.save()
                messages.success(request, 'Profile updated.')
                return redirect('profile')

        return render(request, 'accounts/profile.html', {
            'form': form,
            'profile': profile,
            'password_form': password_form
        })
#todo przykład własnego folmularza z walidatorami
"""
from django import forms
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError

class CustomPasswordChangeForm(forms.Form):
    old_password = forms.CharField(widget=forms.PasswordInput)
    new_password1 = forms.CharField(widget=forms.PasswordInput)
    new_password2 = forms.CharField(widget=forms.PasswordInput)

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user

    def clean_new_password1(self):
        pwd = self.cleaned_data["new_password1"]
        validate_password(pwd, user=self.user)  # <-- wbudowane walidatory
        return pwd

    def clean(self):
        cleaned = super().clean()
        if cleaned.get("new_password1") != cleaned.get("new_password2"):
            raise ValidationError("Hasła muszą być identyczne.")
        return cleaned

"""
#todo natomiast naljhepiej napisać to tak
"""
class MyPasswordChangeForm(PasswordChangeForm):
    pass
    
chba ze masz jakis inny konkretny powód by tego tak nie robić
"""
class ProfileImageDeleteView(LoginRequiredMixin, View):
    def get(self, request):
        profile = request.user.profile
        profile.profile_image.delete()
        profile.save()
        return redirect('dashboard')
#todo usuwanie danych zawsze przez POST
#todo jak bym jednak wracał na profil a nie na dashboard
#todo przed usunieciem obrazka warto sprawdzić czy istneje