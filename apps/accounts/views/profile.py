from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.shortcuts import render, redirect
from django.views import View

from apps.accounts.forms import UserProfileForm, PasswordChangeForm


class ProfileView(View):
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
        profile = request.user.profile

        if 'old_password' in request.POST:
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


class ProfileImageDeleteView(View):
    def get(self, request):
        profile = request.user.profile
        profile.profile_image.delete()
        profile.save()
        return redirect('dashboard')
