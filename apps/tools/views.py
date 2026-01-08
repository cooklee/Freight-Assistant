from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.views import View

from .forms import LeasingForm, SalaryForm, ProfitForm
from .services.leasing import calculate_leasing
from .services.salary import calculate_salary
from .services.profit import calculate_profit


class LeasingView(LoginRequiredMixin, View):

    def get(self, request):
        return render(request, "tools/leasing.html", {"form": LeasingForm()})

    def post(self, request):
        form = LeasingForm(request.POST)
        if form.is_valid():
            result = calculate_leasing(form.cleaned_data)
            return render(request, "tools/leasing.html", {"form": form, "result": result})
        return render(request, "tools/leasing.html", {"form": form})


class SalaryView(LoginRequiredMixin, View):
    template_name = "tools/salary.html"

    def get(self, request):
        return render(request, self.template_name, {"form": SalaryForm()})

    def post(self, request):
        form = SalaryForm(request.POST)
        if form.is_valid():
            result = calculate_salary(form.cleaned_data)
            return render(request, self.template_name, {"form": form, "result": result})
        return render(request, self.template_name, {"form": form})


class ProfitView(LoginRequiredMixin, View):
    template_name = "tools/profit.html"

    def get(self, request):
        return render(request, self.template_name, {"form": ProfitForm()})

    def post(self, request):
        form = ProfitForm(request.POST)
        if form.is_valid():
            result = calculate_profit(form.cleaned_data)
            return render(request, self.template_name, {"form": form, "result": result})
        return render(request, self.template_name, {"form": form})
