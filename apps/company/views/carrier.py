from django.shortcuts import render, redirect, get_object_or_404
from django.views import View

from ..forms import CarrierForm
from ..models import Carrier
from ...drivers.models import Driver


class CarrierListView(View):
    def get(self, request):
        carriers = Carrier.objects.all()
        return render(request, 'company/carrier/carrier_list.html', {'carriers': carriers})


class CarrierAddView(View):

    def get(self, request):
        form = CarrierForm()
        return render(request, 'company/carrier/carrier_add.html', {'form': form})

    def post(self, request):
        form = CarrierForm(request.POST)

        if form.is_valid():
            form.save()
            return redirect('dashboard')
        return render(request, 'company/carrier/carrier_add.html', {'form': form})


class CarrierDetailView(View):
    def get(self, request, carrier_id):
        carrier = get_object_or_404(
            Carrier, id=carrier_id
        )
        drivers = Driver.objects.filter(carrier=carrier)
        return render(request, 'company/carrier/carrier_detail.html', {'carrier': carrier, 'drivers': drivers})


class CarrierUpdateView(View):
    def get(self, request, carrier_id):
        carrier = get_object_or_404(
            Carrier, id=carrier_id
        )
        form = CarrierForm(instance=carrier)
        return render(request, 'company/carrier/carrier_update.html', {'form': form})

    def post(self, request, carrier_id):
        carrier = get_object_or_404(
            Carrier, id=carrier_id
        )
        form = CarrierForm(request.POST, instance=carrier)
        if form.is_valid():
            form.save()
            return redirect('dashboard')
        return render(request, 'company/carrier/carrier_update.html', {'form': form})


class CarrierDeleteView(View):
    def get(self, request, carrier_id):
        carrier = get_object_or_404(
            Carrier, id=carrier_id
        )
        return render(request, 'company/carrier/carrier_delete.html', {'carrier': carrier})

    def post(self, request, carrier_id):
        carrier = get_object_or_404(
            Carrier, id=carrier_id
        )
        carrier.delete()
        return redirect('dashboard')
