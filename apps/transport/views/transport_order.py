from django.shortcuts import render, redirect, get_object_or_404
from django.views import View

from ..forms import TransportOrderForm, TransportOrderUpdateForm
from ..models import TransportOrder


class TransportOrderListView(View):
    def get(self, request):
        orders = TransportOrder.objects.select_related(
            "customer", "carrier", "driver_1", "driver_2"
        ).order_by("-id")

        return render(request, "transport/order/order_list.html", {
            "orders": orders,
        })


class TransportOrderDetailView(View):
    def get(self, request, order_id):
        qs = TransportOrder.objects.select_related(
            "customer", "carrier", "driver_1", "driver_2"
        )
        order = get_object_or_404(qs, id=order_id)

        return render(request, "transport/order/order_detail.html", {
            "order": order,
        })


class TransportOrderCreateView(View):
    def get(self, request):
        form = TransportOrderForm()
        return render(request, "transport/order/order_form.html", {"form": form})

    def post(self, request):
        form = TransportOrderForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("order-list")

        return render(request, "transport/order/order_form.html", {"form": form})


class TransportOrderUpdateView(View):
    def get(self, request, order_id):
        order = get_object_or_404(TransportOrder, id=order_id)
        form = TransportOrderUpdateForm(instance=order)
        return render(request, "transport/order/order_form.html", {"form": form})

    def post(self, request, order_id):
        order = get_object_or_404(TransportOrder, id=order_id)
        form = TransportOrderUpdateForm(request.POST, instance=order)

        if form.is_valid():
            form.save()
            return redirect("order-detail", order_id=order_id)

        return render(request, "transport/order/order_form.html", {"form": form})


class TransportOrderDeleteView(View):
    def get(self, request, order_id):
        order = get_object_or_404(TransportOrder, id=order_id)
        return render(request, "transport/order/order_delete.html", {"order": order})

    def post(self, request, order_id):
        order = get_object_or_404(TransportOrder, id=order_id)
        order.delete()
        return redirect("order-list")
