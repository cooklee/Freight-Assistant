from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect, get_object_or_404
from django.views import View

from ..forms import TransportOrderForm, TransportOrderUpdateForm
from ..models import TransportOrder


class TransportOrderListView(LoginRequiredMixin, View):
    def get(self, request):
        orders = TransportOrder.objects.select_related(
            "customer", "carrier", "driver_1", "driver_2"
        ).filter(user=request.user).order_by("-id")
        # TODO (perf/ux): Dodaj paginację, jeśli orderów może być dużo.

        return render(request, "transport/order/order_list.html", {
            "orders": orders,
        })


class TransportOrderDetailView(LoginRequiredMixin, View):
    def get(self, request, order_id):
        qs = TransportOrder.objects.select_related(
            "customer", "carrier", "driver_1", "driver_2"
        )
        order = get_object_or_404(qs, id=order_id, user=request.user)

        return render(request, "transport/order/order_detail.html", {
            "order": order,
        })


class TransportOrderCreateView(LoginRequiredMixin, View):
    def get(self, request):
        form = TransportOrderForm()
        return render(request, "transport/order/order_form.html", {"form": form})

    def post(self, request):
        form = TransportOrderForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            order.user = request.user
            order.save()
            return redirect("order-detail", order_id=order.id)

        return render(request, "transport/order/order_form.html", {"form": form})


class TransportOrderUpdateView(LoginRequiredMixin, View):
    def get(self, request, order_id):
        order = get_object_or_404(TransportOrder, id=order_id, user=request.user)
        form = TransportOrderUpdateForm(instance=order)
        return render(request, "transport/order/order_form.html", {"form": form})

    def post(self, request, order_id):
        order = get_object_or_404(TransportOrder, id=order_id, user=request.user)
        form = TransportOrderUpdateForm(request.POST, instance=order)

        if form.is_valid():
            form.save()
            return redirect("order-detail", order_id=order_id)

        return render(request, "transport/order/order_form.html", {"form": form})


class TransportOrderDeleteView(LoginRequiredMixin, View):
    def get(self, request, order_id):
        order = get_object_or_404(TransportOrder, id=order_id, user=request.user)
        return render(request, "transport/order/order_delete.html", {"order": order})

    def post(self, request, order_id):
        order = get_object_or_404(TransportOrder, id=order_id, user=request.user)
        order.delete()
        return redirect("order-list")
        # TODO (ux): Rozważ messages.success po usunięciu.
