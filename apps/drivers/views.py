from django.shortcuts import render, redirect, get_object_or_404
from django.views import View

from .forms import DriverForm
from .models import Driver


class DriverListView(View):
    def get(self, request):
        drivers = Driver.objects.all()
        return render(request, 'drivers/driver_list.html', {'drivers': drivers})


class DriverAddView(View):
    def get(self, request, carrier_id):
        form = DriverForm()
        return render(request, 'drivers/driver_add.html', {'form': form})

    def post(self, request, carrier_id):
        form = DriverForm(request.POST)
        if form.is_valid():
            driver = form.save(commit=False)
            driver.carrier_id = carrier_id
            driver.save()
            return redirect('carrier-detail', carrier_id=carrier_id)
        return render(request, 'drivers/driver_add.html', {'form': form})


class DriverDetailView(View):
    def get(self, request, driver_id):
        driver = get_object_or_404(
            Driver,
            id=driver_id
        )
        return render(request, 'drivers/driver_detail.html', {'driver': driver})


class DriverUpdateView(View):
    def get(self, request, driver_id):
        driver = get_object_or_404(
            Driver,
            id=driver_id
        )
        form = DriverForm(instance=driver)
        return render(request, 'drivers/driver_update.html', {'form': form, 'driver': driver})

    def post(self, request, driver_id):
        driver = get_object_or_404(
            Driver,
            id=driver_id
        )
        form = DriverForm(request.POST, instance=driver)
        if form.is_valid():
            driver = form.save(commit=False)
            driver.carrier = driver.carrier
            driver.save()
            return redirect('carrier-detail', carrier_id=driver.carrier.id)
        return render(request, 'drivers/driver_update.html', {'form': form, 'driver': driver})


class DriverDeleteView(View):
    def get(self, request, driver_id):
        driver = get_object_or_404(
            Driver,
            id=driver_id
        )
        return render(request, 'drivers/driver_delete.html', {'driver': driver})

    def post(self, request, driver_id):
        driver = get_object_or_404(
            Driver,
            id=driver_id
        )
        carrier_id = driver.carrier.id
        driver.delete()
        return redirect('carrier-detail', carrier_id=carrier_id)
