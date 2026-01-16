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
        # TODO (perf/ux): Dodaj sortowanie (np. .order_by("-id") albo "-created_at") i paginację, jeśli rekordów będzie dużo.
        # TODO (perf): Jeśli lista pokazuje powiązania (route/carrier/drivers), dodaj select_related na liście,
        # TODO (perf): żeby uniknąć N+1 w template.

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
        # TODO (data): schedule jest trzymany jako string. Jeśli plan ma być tabelą w UI/PDF, rozważ JSONField w modelu,
        # TODO (data): żeby nie parsować stringów w wielu miejscach.

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
        # TODO (style): Masz tę samą logikę w apps.transport.views.calculation.CalculationPdfView, ale tam inaczej policzoną.
        # TODO (maint): Wyciągnij liczenie work_minutes/total_duration_minutes do helpera (np. methoda na modelu
        # TODO (maint): albo funkcja utils), żeby nie dublować i nie rozjechać implementacji.

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
        # TODO (perf/robustness): apply_schedule może robić dużo pracy i wołać Google API (zależnie od implementacji).
        # TODO (perf): Rozważ uruchamianie asynchroniczne (Django Q/Celery) albo cache wyników,
        # TODO (perf): jeśli generowanie planu ma być szybkie dla użytkownika.
        # TODO (robustness): Jeśli apply_schedule może rzucać wyjątki, obsłuż to (messages.error + render form),
        # TODO (robustness): żeby nie kończyć 500 dla użytkownika.

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
        # TODO (perf/robustness): Jak w CreateView — potencjalnie ciężkie i podatne na błędy zewnętrzne.
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
        # TODO (maint): Duplikacja liczenia z CalculationDetailView. Wyciągnij do wspólnej funkcji/helpera.

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
        # TODO (bug): Path(settings.BASE_DIR).parent może nie wskazywać tego co myślisz (zależy gdzie jest BASE_DIR).
        # TODO (bug): Jeśli static jest w projekcie inaczej, to PDF straci style. Rozważ settings.STATIC_ROOT/STATICFILES_DIRS
        # TODO (bug): albo trzymanie ścieżki do css w settings.

        pdf = HTML(string=html, base_url=request.build_absolute_uri()).write_pdf(
            stylesheets=[CSS(filename=str(css_path))]
        )
        # TODO (security): base_url opiera się o host z requestu. Upewnij się, że masz poprawnie ALLOWED_HOSTS/proxy headers.
        # TODO (robustness): WeasyPrint potrafi rzucać wyjątki (brak fontów, brak zasobów). Rozważ try/except i sensowną odpowiedź.
        # TODO (perf): Generowanie PDF jest kosztowne. Jeśli często generujesz ten sam PDF, rozważ cache (np. per calculation_id).

        response = HttpResponse(pdf, content_type="application/pdf")
        response["Content-Disposition"] = f'inline; filename="calculation_{calculation.id}.pdf"'
        return response
        # TODO (ux): Jeśli chcesz wymusić pobranie, użyj attachment zamiast inline.
