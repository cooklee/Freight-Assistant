from django.shortcuts import render, redirect
from django.views import View

from ..forms import CarrierAddForm


class CarrierAddView(View):
    template_name = 'company/carrier_add.html'

    def get(self, request):
        form = CarrierAddForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = CarrierAddForm(request.POST)

        if form.is_valid():
            form.save()
            return redirect('dashboard')

        return render(request, self.template_name, {'form': form})
