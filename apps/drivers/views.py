from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect, get_object_or_404
from django.views import View

from .forms import DriverForm
from .models import Driver


class DriverListView(LoginRequiredMixin, View):
    def get(self, request):
        drivers = Driver.objects.all()
        # TODO: dla wydajności, jeśli w template sięgasz do driver.carrier, rozważ:
        #       drivers = Driver.objects.select_related("carrier").all()
        return render(request, "drivers/driver_list.html", {"drivers": drivers})


class DriverAddView(LoginRequiredMixin, View):
    def get(self, request, carrier_id):
        # TODO: Rozważ walidację, czy carrier_id istnieje oraz czy user ma do niego dostęp.
        #       Teraz możesz stworzyć Drivera pod dowolny carrier_id
        #       ja tutaj bym pobrał carriera i wypisywał info o nim na stronie.
        form = DriverForm()
        return render(
            request,
            "drivers/driver_add.html",
            {
                "form": form,
                "carrier_id": carrier_id,  # TODO: tutaj przekazał bym całego carriera
            },
        )

    def post(self, request, carrier_id):
        form = DriverForm(request.POST)
        if form.is_valid():
            driver = form.save(commit=False)
            driver.carrier_id = carrier_id
            driver.save()

            return redirect("carrier-detail", carrier_id=carrier_id)

        return render(
            request,
            "drivers/driver_add.html",
            {
                "form": form,
                "carrier_id": carrier_id,
            },
        )


class DriverDetailView(LoginRequiredMixin, View):
    def get(self, request, driver_id):
        # TODO: Jak wyżej – brak filtrowania po userze / carrierze. Każdy zalogowany user
        #       może podejrzeć dowolnego Drivera po ID.
        driver = get_object_or_404(
            Driver.objects.select_related("carrier"),  # mały boost, jeśli używasz carrier w template
            id=driver_id,
        )
        return render(request, "drivers/driver_detail.html", {"driver": driver})


class DriverUpdateView(LoginRequiredMixin, View):
    def get(self, request, driver_id):
        driver = get_object_or_404(
            Driver.objects.select_related("carrier"),
            id=driver_id,
        )

        form = DriverForm(instance=driver)
        return render(
            request,
            "drivers/driver_update.html",
            {"form": form, "driver": driver},
        )

    def post(self, request, driver_id):
        driver = get_object_or_404(
            Driver.objects.select_related("carrier"),
            id=driver_id,
        )
        form = DriverForm(request.POST, instance=driver)
        if form.is_valid():
            # TODO: commit=False jest tu zbędny, o ile form nie nadpisuje carrier.
            # carriera i tak nie mozesz zmienić
            driver = form.save()

            return redirect("carrier-detail", carrier_id=driver.carrier_id)

        return render(
            request,
            "drivers/driver_update.html",
            {"form": form, "driver": driver},
        )


class DriverDeleteView(LoginRequiredMixin, View):
    def get(self, request, driver_id):
        driver = get_object_or_404(
            Driver.objects.select_related("carrier"),
            id=driver_id,
        )
        return render(request, "drivers/driver_delete.html", {"driver": driver})

    def post(self, request, driver_id):
        driver = get_object_or_404(
            Driver.objects.select_related("carrier"),
            id=driver_id,
        )
        carrier_id = driver.carrier_id
        driver.delete()

        return redirect("carrier-detail", carrier_id=carrier_id)

#todo całościowo znow domyslne zachowania nie widze sensu pisania z palca tego lepiej użyć widoków generycznych
