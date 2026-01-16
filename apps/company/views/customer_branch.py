from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect, get_object_or_404
from django.views import View

from ..forms import CustomerBranchForm
from ..models import CustomerBranch, Customer


class CustomerBranchListView(LoginRequiredMixin, View):
    def get(self, request):
        branches = CustomerBranch.objects.all()
        #todo jestes tego pewien dodział wsztstjue bez kontekstu klienta ?
        return render(request, 'company/customer_branch/customer_branch_list.html', {'branches': branches})


class CustomerBranchAddView(LoginRequiredMixin, View):

    def get(self, request, customer_id):
        #todo warto tutaj by pobrać kilenta i wyświetlić informacje na jego temat
        form = CustomerBranchForm()
        return render(request, 'company/customer_branch/customer_branch_add.html', {'form': form})

    def post(self, request, customer_id):
        customer = get_object_or_404(Customer, id=customer_id)
        form = CustomerBranchForm(request.POST)

        if form.is_valid():
            branch = form.save(commit=False)
            branch.customer = customer
            branch.save()
            return redirect('customer-detail', customer_id=customer.id)

        return render(request, 'company/customer_branch/customer_branch_add.html', {'form': form})


class CustomerBranchDetailView(LoginRequiredMixin, View):
    def get(self, request, branch_id):
        branch = get_object_or_404(
            CustomerBranch, id=branch_id
        )
        return render(request, 'company/customer_branch/customer_branch_detail.html',
                      {'branch': branch})


class CustomerBranchUpdateView(LoginRequiredMixin, View):
    def get(self, request, branch_id):
        branch = get_object_or_404(
            CustomerBranch, id=branch_id
        )
        form = CustomerBranchForm(instance=branch)
        return render(request, 'company/customer_branch/customer_branch_update.html', {'form': form})

    def post(self, request, branch_id):
        branch = get_object_or_404(
            CustomerBranch, id=branch_id
        )
        form = CustomerBranchForm(request.POST, instance=branch)

        if form.is_valid():
            branch = form.save(commit=False)
            branch.customer = branch.customer
            #todo mam dzwine wrażenie ze to babol :P
            branch.save()
            return redirect('customer-detail', customer_id=branch.customer.id)

        return render(request, 'company/customer_branch/customer_branch_update.html', {'form': form})


class CustomerBranchDeleteView(LoginRequiredMixin, View):
    def get(self, request, branch_id):
        branch = get_object_or_404(
            CustomerBranch, id=branch_id
        )
        return render(request, 'company/customer_branch/customer_branch_delete.html', {'branch': branch})

    def post(self, request, branch_id):
        branch = get_object_or_404(
            CustomerBranch, id=branch_id
        )
        customer_id = branch.customer.id
        branch.delete()
        return redirect('customer-detail', customer_id=customer_id)
