from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
#todo nie importuj User na sztywno
from django.shortcuts import render, redirect
from django.views import View

from apps.accounts.forms import LoginViewForm, RegisterViewForm


class LoginView(View):
    def get(self, request):
        form = LoginViewForm()
        return render(request, 'accounts/login.html', {'form': form})

    def post(self, request):
        form = LoginViewForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(username=username, password=password)

            if user:
                login(request, user)
                return redirect('dashboard')
            #todo Brakuje obsługi next po logowaniu
            else:
                form.add_error(None, "Invalid username or password")

        return render(request, 'accounts/login.html', {'form': form})


class LogoutView(View):
    def get(self, request):
        logout(request)
        return redirect('login')

#todo Nie korzystasz z gotowych widoków Django auth, o ile podczas zajęć uczylismy sie jak je napisać to na produkcji
# używa sie wbudowanych chba ze jest jakis istotny powód by zrobić to inaczej
class RegisterView(View):
    def get(self, request):
        form = RegisterViewForm()
        return render(request, 'accounts/register.html', {'form': form})

    def post(self, request):
        form = RegisterViewForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            email = form.cleaned_data['email']
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']

            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name
            )

            login(request, user)
            return redirect('dashboard')

        return render(request, 'accounts/register.html', {'form': form})
