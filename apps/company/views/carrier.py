from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect, get_object_or_404
from django.views import View

from ..forms import CarrierForm
from ..models import Carrier
from ...drivers.models import Driver
#todo importy dla mnie jedna kropka jest dopiszczalna wiecej juz nie bo skaczesz i zaburzasz czytelność


class CarrierListView(LoginRequiredMixin, View):
    def get(self, request):
        carriers = Carrier.objects.all()
        return render(request, 'company/carrier/carrier_list.html', {'carriers': carriers})


class CarrierAddView(LoginRequiredMixin, View):

    def get(self, request):
        form = CarrierForm()
        return render(request, 'company/carrier/carrier_add.html', {'form': form})

    def post(self, request):
        form = CarrierForm(request.POST)

        if form.is_valid():
            carrier = form.save()
            return redirect('carrier-detail', carrier_id=carrier.id)
        return render(request, 'company/carrier/carrier_add.html', {'form': form})


class CarrierDetailView(LoginRequiredMixin, View):
    def get(self, request, carrier_id):
        carrier = get_object_or_404(
            Carrier, id=carrier_id
        )
        drivers = Driver.objects.filter(carrier=carrier)
        return render(request, 'company/carrier/carrier_detail.html', {'carrier': carrier, 'drivers': drivers})
#todo tego tak nie musisz robic
#todo warto tez dodać prefetch_related
"""
draviers = carrier.drivers.all() mozesz zastąpić carrier.driver_set.all() -> ale skoro potrzebujesz tego w szablonie to w szablonie mozesz to zrobić tak samo 
a optymalnie jest zrobienie tego tak:
carrier = get_object_or_404(
    Carrier.objects.prefetch_related("driver_set"),
    id=carrier_id
)
dzieku temu wszyscy driverrzy beda juz w carreierze i nie bedzie trzeba robić kolejnego uderzenia do bazy dancyh 
"""


class CarrierUpdateView(LoginRequiredMixin, View):
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
            return redirect('carrier-detail', carrier_id=carrier.id)
        return render(request, 'company/carrier/carrier_update.html', {'form': form})


class CarrierDeleteView(LoginRequiredMixin, View):
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
        return redirect('carrier-list')

#todo warto tez ustawić sortowanie .order_by("name") albo w modelach + paginacja