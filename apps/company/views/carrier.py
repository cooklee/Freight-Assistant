from django.shortcuts import render, redirect
from django.views import View

from ..forms import CarrierForm
from ..models import Carrier


class CarrierAddView(View):

    def get(self, request):
        form = CarrierForm()
        return render(request, 'company/carrier_add.html', {'form': form})

    def post(self, request):
        form = CarrierForm(request.POST)

        if form.is_valid():
            form.save()
            return redirect('dashboard')

        return render(request, 'company/carrier_add.html', {'form': form})


class CarrierDetailView(View):
    def get(self, request):
        carriers = Carrier.objects.all()
        return render(request, 'company/carrier_detail.html', {'carriers': carriers})


class CarrierUpdateView(View):
    def get(self, request, carrier_id):
        carrier = Carrier.objects.get(id=carrier_id)
        form = CarrierForm(instance=carrier)