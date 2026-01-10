from pathlib import Path

from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from django.views import View
from weasyprint import HTML, CSS

from apps.transport.forms import CalculationForm
from apps.transport.models import Calculation
from apps.transport.services.calculation_service import apply_schedule


class CalculationListView(LoginRequiredMixin, View):
    def get(self, request):
        calculations = Calculation.objects.filter(user=request.user)

        return render(request, "transport/calculation/calculation_list.html", {
            "calculations": calculations,
        })


class CalculationDetailView(LoginRequiredMixin, View):
    def get(self, request, calculation_id):
        qs = (
            Calculation.objects
            .select_related("route", "carrier", "driver_1", "driver_2")
            .filter(user=request.user)
        )

        calculation = get_object_or_404(qs, id=calculation_id)

        schedule_rows = calculation.schedule.splitlines() if calculation.schedule else []

        work_minutes = sum(filter(None, [
            calculation.total_drive_time_minutes,
            calculation.total_other_work_time_minutes,
        ]))

        total_duration_minutes = sum(filter(None, [
            calculation.total_drive_time_minutes,
            calculation.total_break_time_minutes,
            calculation.total_rest_time_minutes,
            calculation.total_other_work_time_minutes,
        ]))

        return render(request, "transport/calculation/calculation_detail.html", {
            "calculation": calculation,
            "schedule_rows": schedule_rows,
            "work_minutes": work_minutes,
            "total_duration_minutes": total_duration_minutes,
        })


class CalculationCreateView(LoginRequiredMixin, View):
    def get(self, request):
        form = CalculationForm(user=request.user)
        return render(request, "transport/calculation/calculation_form.html", {"form": form})

    def post(self, request):
        form = CalculationForm(request.POST, user=request.user)

        if not form.is_valid():
            return render(request, "transport/calculation/calculation_form.html", {"form": form})

        calculation = form.save(commit=False)
        calculation.user = request.user
        apply_schedule(calculation)
        calculation.save()

        return redirect("calculation-detail", calculation_id=calculation.id)


class CalculationUpdateView(LoginRequiredMixin, View):
    def get(self, request, calculation_id):
        calculation = get_object_or_404(Calculation, id=calculation_id, user=request.user)
        form = CalculationForm(instance=calculation, user=request.user)
        return render(request, "transport/calculation/calculation_form.html", {
            "form": form,
            "update": True,
        })

    def post(self, request, calculation_id):
        calculation = get_object_or_404(Calculation, id=calculation_id, user=request.user)
        form = CalculationForm(request.POST, instance=calculation, user=request.user)

        if not form.is_valid():
            return render(request, "transport/calculation/calculation_form.html", {
                "form": form,
                "update": True,
            })

        calculation = form.save(commit=False)

        apply_schedule(calculation)
        calculation.save()

        return redirect("calculation-detail", calculation_id=calculation.id)


class CalculationDeleteView(LoginRequiredMixin, View):
    def get(self, request, calculation_id):
        calculation = get_object_or_404(Calculation, id=calculation_id, user=request.user)
        return render(request, "transport/calculation/calculation_delete.html", {
            "calculation": calculation,
        })

    def post(self, request, calculation_id):
        calculation = get_object_or_404(Calculation, id=calculation_id, user=request.user)
        calculation.delete()
        return redirect("calculation-list")


class CalculationPdfView(LoginRequiredMixin, View):
    def get(self, request, calculation_id):
        calculation = get_object_or_404(
            Calculation,
            id=calculation_id,
            user=request.user,
        )

        schedule_rows = calculation.schedule.splitlines() if calculation.schedule else []

        work_minutes = (calculation.total_drive_time_minutes or 0) + (calculation.total_other_work_time_minutes or 0)
        total_duration_minutes = (
                (calculation.total_drive_time_minutes or 0)
                + (calculation.total_break_time_minutes or 0)
                + (calculation.total_rest_time_minutes or 0)
                + (calculation.total_other_work_time_minutes or 0)
        )

        html = render_to_string(
            "transport/calculation/calculation_pdf.html",
            {
                "calculation": calculation,
                "schedule_rows": schedule_rows,
                "work_minutes": work_minutes,
                "total_duration_minutes": total_duration_minutes,
            }
        )

        css_path = Path(settings.BASE_DIR).parent / "static" / "css" / "pdf.css"

        pdf = HTML(string=html, base_url=request.build_absolute_uri()).write_pdf(
            stylesheets=[CSS(filename=str(css_path))]
        )

        response = HttpResponse(pdf, content_type="application/pdf")
        response["Content-Disposition"] = f'inline; filename="calculation_{calculation.id}.pdf"'
        return response
