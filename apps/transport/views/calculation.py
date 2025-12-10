from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, get_object_or_404, redirect
from django.views import View

from apps.transport.forms import CalculationForm
from apps.transport.models import Calculation
from apps.transport.services.schedule_builder import generate_schedule


class CalculationListView(LoginRequiredMixin, View):
    def get(self, request):
        calculations = (
            Calculation.objects
            .select_related("route", "carrier", "driver_1", "driver_2")
            .order_by("-id")
        )

        return render(request, "transport/calculation/calculation_list.html", {
            "calculations": calculations,
        })


class CalculationDetailView(LoginRequiredMixin, View):
    def get(self, request, calculation_id):
        qs = Calculation.objects.select_related(
            "route", "carrier", "driver_1", "driver_2"
        )

        calculation = get_object_or_404(qs, id=calculation_id)

        schedule_rows = calculation.schedule.splitlines() if calculation.schedule else []

        total_work_time_minutes = sum(filter(None, [
            calculation.total_drive_time_minutes,
            calculation.total_break_time_minutes,
            calculation.total_rest_time_minutes,
            calculation.total_other_work_time_minutes,
        ]))

        return render(request, "transport/calculation/calculation_detail.html", {
            "calculation": calculation,
            "schedule_rows": schedule_rows,
            "total_work_hours": total_work_time_minutes / 60,
        })


class CalculationCreateView(LoginRequiredMixin, View):
    def get(self, request):
        form = CalculationForm()
        return render(request, "transport/calculation/calculation_form.html", {"form": form})

    def post(self, request):
        form = CalculationForm(request.POST)

        if not form.is_valid():
            return render(request, "transport/calculation/calculation_form.html", {"form": form})

        calculation = form.save(commit=False)

        route = calculation.route
        stops = list(route.stops.order_by("stop_number"))

        driver_count = 2 if calculation.driver_2 else 1
        result = generate_schedule(stops=stops, driver_count=driver_count)

        calculation.total_km = result["total_km"]
        calculation.total_drive_time_minutes = result["total_drive_time_minutes"]
        calculation.total_break_time_minutes = result["total_break_time_minutes"]
        calculation.total_rest_time_minutes = result["total_rest_time_minutes"]
        calculation.total_other_work_time_minutes = result["total_work_time_minutes"]

        rows = []
        for day, task, minutes in result["schedule_table"]:
            hours = minutes // 60
            mins = minutes % 60
            rows.append(f"{day}: {task} – {hours}h {mins}min")

        calculation.schedule = "\n".join(rows)

        calculation.save()

        return redirect("calculation-detail", calculation_id=calculation.id)


class CalculationUpdateView(LoginRequiredMixin, View):
    def get(self, request, calculation_id):
        calculation = get_object_or_404(Calculation, id=calculation_id)
        form = CalculationForm(instance=calculation)
        return render(request, "transport/calculation/calculation_form.html", {
            "form": form,
            "update": True,
        })

    def post(self, request, calculation_id):
        calculation = get_object_or_404(Calculation, id=calculation_id)
        form = CalculationForm(request.POST, instance=calculation)

        if not form.is_valid():
            return render(request, "transport/calculation/calculation_form.html", {
                "form": form,
                "update": True,
            })

        calculation = form.save(commit=False)

        route = calculation.route
        stops = list(route.stops.order_by("stop_number"))
        driver_count = 2 if calculation.driver_2 else 1
        result = generate_schedule(stops=stops, driver_count=driver_count)

        calculation.total_km = result["total_km"]
        calculation.total_drive_time_minutes = result["total_drive_time_minutes"]
        calculation.total_break_time_minutes = result["total_break_time_minutes"]
        calculation.total_rest_time_minutes = result["total_rest_time_minutes"]
        calculation.total_other_work_time_minutes = result["total_work_time_minutes"]

        rows = []
        for day, task, minutes in result["schedule_table"]:
            hours = minutes // 60
            mins = minutes % 60
            rows.append(f"{day}: {task} – {hours}h {mins}min")

        calculation.schedule = "\n".join(rows)

        calculation.save()
        return redirect("calculation-detail", calculation_id=calculation.id)


class CalculationDeleteView(LoginRequiredMixin, View):
    def get(self, request, calculation_id):
        calculation = get_object_or_404(Calculation, id=calculation_id)
        return render(request, "transport/calculation/calculation_delete.html", {
            "calculation": calculation,
        })

    def post(self, request, calculation_id):
        calculation = get_object_or_404(Calculation, id=calculation_id)
        calculation.delete()
        return redirect("calculation-list")
