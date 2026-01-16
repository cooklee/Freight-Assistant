from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, get_object_or_404, redirect
from django.views import View

from ..forms import StopForm
from ..models import Route, Stop


class StopCreateView(LoginRequiredMixin, View):
    def get(self, request, route_id):
        route = get_object_or_404(Route, id=route_id, user=request.user)
        form = StopForm()
        return render(request, "transport/stop/stop_form.html", {
            "form": form,
            "route": route,
            "title": "Add Stop",
            "GOOGLE_MAPS_API_KEY": settings.GOOGLE_MAPS_API_KEY,
            # TODO (security): Wystawianie API key do frontu jest OK tylko jeśli klucz jest odpowiednio restricted
            # TODO (security): (HTTP referrers + ograniczone API). Inaczej ktoś może go wyciągnąć i nabić koszty.
        })

    def post(self, request, route_id):
        route = get_object_or_404(Route, id=route_id, user=request.user)
        form = StopForm(request.POST)

        if form.is_valid():
            stop = form.save(commit=False)
            stop.route = route
            stop.save()
            # TODO (data): Rozważ wymuszenie spójności stop_number (unikalny w obrębie route) i min liczby stopów.
            return redirect("route-detail", route_id=route.id)

        return render(request, "transport/stop/stop_form.html", {
            "form": form,
            "route": route,
            "title": "Add Stop",
            "GOOGLE_MAPS_API_KEY": settings.GOOGLE_MAPS_API_KEY,
            # TODO (security): Jak wyżej — upewnij się, że key jest restricted.
        })


class StopUpdateView(LoginRequiredMixin, View):
    def get(self, request, stop_id):
        stop = get_object_or_404(
            Stop, id=stop_id, route__user=request.user
        )
        form = StopForm(instance=stop)
        return render(request, "transport/stop/stop_form.html", {
            "form": form,
            "route": stop.route,
            "title": f"Update Stop #{stop.stop_number}",
            "GOOGLE_MAPS_API_KEY": settings.GOOGLE_MAPS_API_KEY,
        })

    def post(self, request, stop_id):
        stop = get_object_or_404(
            Stop, id=stop_id, route__user=request.user
        )
        form = StopForm(request.POST, instance=stop)

        if form.is_valid():
            form.save()
            # TODO (data): Jeśli stop_number może się zmieniać, rozważ walidację konfliktów (unikalność w obrębie route).
            return redirect("route-detail", route_id=stop.route.id)

        return render(request, "transport/stop/stop_form.html", {
            "form": form,
            "route": stop.route,
            "title": f"Update Stop #{stop.stop_number}",
            "GOOGLE_MAPS_API_KEY": settings.GOOGLE_MAPS_API_KEY,
        })


class StopDeleteView(LoginRequiredMixin, View):
    """Deletes a stop."""

    def get(self, request, stop_id):
        stop = get_object_or_404(
            Stop,
            id=stop_id,
            route__user=request.user
        )

        return render(request, "transport/stop/stop_delete.html", {
            "stop": stop,
            "route": stop.route,
        })

    def post(self, request, stop_id):
        stop = get_object_or_404(
            Stop,
            id=stop_id,
            route__user=request.user
        )
        route_id = stop.route.id
        stop.delete()
        return redirect("route-detail", route_id=route_id)