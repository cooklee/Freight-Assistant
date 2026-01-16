from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count
from django.shortcuts import render
from django.urls import reverse
from django.views import View

from apps.company.models import Carrier, Customer
from apps.drivers.models import Driver
from apps.transport.models import Calculation, Route, TransportOrder


class DashboardView(LoginRequiredMixin, View):
    def get(self, request):
        user = request.user

        orders_qs = (
            TransportOrder.objects
            .select_related("customer", "carrier", "driver_1", "driver_2")
            .filter(user=user)
            .order_by("-id")
        )

        calculations_qs = (
            Calculation.objects
            .select_related("route", "carrier", "driver_1", "driver_2")
            .filter(user=user)
            .order_by("-id")
        )

        routes_qs = (
            Route.objects
            .filter(user=user)
            .annotate(stops_count=Count("stops"))
            .order_by("-id")
        )

        carriers_qs = Carrier.objects.all()
        customers_qs = Customer.objects.all()
        drivers_qs = Driver.objects.all()

        counts = {
            "orders": orders_qs.count(),
            "calculations": calculations_qs.count(),
            "routes": routes_qs.count(),
            "drivers": drivers_qs.count(),
            "customers": customers_qs.count(),
            "carriers": carriers_qs.count(),
        }

        recent_orders = orders_qs[:5]
        recent_calculations = calculations_qs[:5]

        alerts = []

        negative_profit_count = orders_qs.filter(profit__lt=0).count()
        if negative_profit_count:
            alerts.append({
                "title": "Negative profit orders",
                "text": f"{negative_profit_count} order(s) have negative profit.",
                "url": reverse("order-list"),
            })

        invalid_routes_count = routes_qs.filter(stops_count__lt=2).count()
        if invalid_routes_count:
            alerts.append({
                "title": "Routes need at least 2 stops",
                "text": f"{invalid_routes_count} route(s) have less than 2 stops.",
                "url": reverse("route-list")
            })

        missing_schedule_count = calculations_qs.filter(schedule__isnull=True).count()
        #todo tutaj warto zrobić tak: filter(Q(schedule__isnull=True) | Q(schedule="")) ponieważ schedyke jest polem tekstowym ktore ma blank=True wiec zapisze sie do bazy ""
        if missing_schedule_count:
            alerts.append({
                "title": "Calculations missing schedule",
                "text": f"{missing_schedule_count} calculation(s) have no schedule generated.",
                "url": reverse("calculation-list")
            })

        context = {
            "counts": counts,
            "recent_orders": recent_orders,
            "recent_calculations": recent_calculations,
            "alerts": alerts,
        }
        return render(request, 'core/dashboard.html', context)
