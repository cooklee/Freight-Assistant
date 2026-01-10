from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect, get_object_or_404
from django.views import View

from ..forms import CustomerForm
from ..models import Customer


class CustomerListView(LoginRequiredMixin, View):
    def get(self, request):
        customers = Customer.objects.all()
        return render(request, 'company/customer/customer_list.html', {'customers': customers})


class CustomerAddView(LoginRequiredMixin, View):

    def get(self, request):
        form = CustomerForm()
        return render(request, 'company/customer/customer_add.html', {'form': form})

    def post(self, request):
        form = CustomerForm(request.POST)

        if form.is_valid():
            customer = form.save()
            return redirect('customer-detail', customer_id=customer.id)

        return render(request, 'company/customer/customer_add.html', {'form': form})


class CustomerDetailView(LoginRequiredMixin, View):
    def get(self, request, customer_id):
        customer = get_object_or_404(
            Customer, id=customer_id
        )
        branches = customer.branches.all()
        return render(request, 'company/customer/customer_detail.html', {'customer': customer, 'branches': branches})


class CustomerUpdateView(LoginRequiredMixin, View):
    def get(self, request, customer_id):
        customer = get_object_or_404(
            Customer, id=customer_id
        )
        form = CustomerForm(instance=customer)
        return render(request, 'company/customer/customer_update.html', {'form': form})

    def post(self, request, customer_id):
        customer = get_object_or_404(
            Customer, id=customer_id
        )
        form = CustomerForm(request.POST, instance=customer)
        if form.is_valid():
            form.save()
            return redirect('customer-detail', customer_id=customer.id)
        return render(request, 'company/customer/customer_update.html', {'form': form})


class CustomerDeleteView(LoginRequiredMixin, View):
    def get(self, request, customer_id):
        customer = get_object_or_404(
            Customer, id=customer_id
        )
        return render(request, 'company/customer/customer_delete.html', {'customer': customer})

    def post(self, request, customer_id):
        customer = get_object_or_404(
            Customer, id=customer_id
        )
        customer.delete()
        return redirect('customer-list')
