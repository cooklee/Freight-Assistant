from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, get_object_or_404, redirect
from django.views import View

from ..forms.route import RouteForm
from ..forms.stop import StopFormSet
from ..models import Route


class RouteListView(LoginRequiredMixin, View):
    def get(self, request):
        routes = Route.objects.filter(user=request.user).order_by("id")

        return render(
            request,
            "transport/route/route_list.html",
            {"routes": routes}
        )


class RouteDetailView(LoginRequiredMixin, View):
    def get(self, request, route_id):
        route = get_object_or_404(
            Route.objects.prefetch_related("stops"),
            id=route_id,
            user=request.user,
        )
        stops = route.stops.all()

        return render(
            request,
            "transport/route/route_detail.html",
            {"route": route, "stops": stops}
        )


class RouteCreateView(LoginRequiredMixin, View):
    def get(self, request):
        form = RouteForm()
        return render(request, "transport/route/route_form.html", {"form": form})

    def post(self, request):
        form = RouteForm(request.POST)
        if form.is_valid():
            route = form.save(commit=False)
            route.user = request.user
            route.save()
            return redirect("route-list")

        return render(request, "transport/route/route_form.html", {"form": form})


class RouteUpdateView(LoginRequiredMixin, View):
    def get(self, request, route_id):
        route = get_object_or_404(Route, id=route_id, user=request.user)
        form = RouteForm(instance=route)
        stops = route.stops.all().order_by("stop_number")

        return render(
            request,
            "transport/route/route_update.html",
            {
                "form": form,
                "route": route,
                "stops": stops,
            }
        )

    def post(self, request, route_id):
        route = get_object_or_404(Route, id=route_id, user=request.user)
        form = RouteForm(request.POST, instance=route)

        if form.is_valid():
            form.save()
            return redirect("route-detail", route_id=route.id)

        stops = route.stops.all().order_by("stop_number")

        return render(
            request,
            "transport/route/route_update.html",
            {
                "form": form,
                "route": route,
                "stops": stops,
            }
        )


class RouteDeleteView(LoginRequiredMixin, View):
    def get(self, request, route_id):
        route = get_object_or_404(Route, id=route_id, user=request.user)
        return render(request, "transport/route/route_delete.html", {"route": route})

    def post(self, request, route_id):
        route = get_object_or_404(Route, id=route_id, user=request.user)
        route.delete()
        return redirect("route-list")


class RouteWithStopsCreateView(LoginRequiredMixin, View):

    def get(self, request):
        form = RouteForm()
        formset = StopFormSet(prefix="stops")
        return render(
            request,
            "transport/route/route_with_stops.html",
            {
                "form": form,
                "formset": formset,
                "GOOGLE_MAPS_API_KEY": settings.GOOGLE_MAPS_API_KEY,
            }
        )

    def post(self, request):
        form = RouteForm(request.POST)
        formset = StopFormSet(request.POST, prefix="stops")

        if form.is_valid() and formset.is_valid():
            route = form.save(commit=False)
            route.user = request.user
            route.save()

            stops = formset.save(commit=False)
            for stop in stops:
                stop.route = route
                stop.save()

            return redirect("route-detail", route_id=route.id)

        return render(
            request,
            "transport/route/route_with_stops.html",
            {
                "form": form,
                "formset": formset,
                "GOOGLE_MAPS_API_KEY": settings.GOOGLE_MAPS_API_KEY,
            }
        )
