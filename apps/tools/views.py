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
        # TODO (style): Masz tu powtórkę renderowania w GET/POST. Rozważ template_name jak w innych klasach

    def post(self, request):
        form = LeasingForm(request.POST)
        if form.is_valid():
            result = calculate_leasing(form.cleaned_data)
            return render(request, "tools/leasing.html", {"form": form, "result": result})
        return render(request, "tools/leasing.html", {"form": form})
    #todo render jest powielony spokojnie mozesz zrobic
    """
    def post(self, request):
        form = LeasingForm(request.POST)
        result = {}
        if form.is_valid():
            result = calculate_leasing(form.cleaned_data)
        return render(request, "tools/leasing.html", {"form": form, "result": result})
   
    """



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
        # TODO (style): Jak wyżej — da się uprościć do jednego render na końcu.


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
        # TODO (style): Jak wyżej — uprość do jednego render na końcu.

# TODO (maint): Wszystkie trzy widoki są prawie identyczne (Form + Service + Template).
# TODO (maint): Rozważ wspólną klasę bazową albo generyczny widok typu:
# TODO (maint): - atrybuty: form_class, template_name, calculate_fn
# TODO (maint): - jedna implementacja get/post
# TODO (maint): Zmniejszy to duplikację i ryzyko rozjazdu w przyszłości.
