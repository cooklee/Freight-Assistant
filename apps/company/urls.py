from django.urls import path

from .views import (CarrierAddView, CarrierDetailView,
                    CarrierUpdateView, CarrierDeleteView,
                    CarrierListView, CustomerAddView, CustomerDetailView,
                    CustomerUpdateView, CustomerDeleteView,
                    CustomerListView, CustomerBranchAddView, CustomerBranchDetailView,
                    CustomerBranchUpdateView, CustomerBranchDeleteView,
                    CustomerBranchListView)

urlpatterns = [
    path('carrier/add/', CarrierAddView.as_view(), name='carrier-add'),
    path('carrier/detail/<int:carrier_id>/', CarrierDetailView.as_view(), name='carrier-detail'),
    path('carrier/update/<int:carrier_id>/', CarrierUpdateView.as_view(), name='carrier-update'),
    path('carrier/delete/<int:carrier_id>/', CarrierDeleteView.as_view(), name='carrier-delete'),
    path('carrier/all/', CarrierListView.as_view(), name='carrier-list'),
    path('customer/add/', CustomerAddView.as_view(), name='customer-add'),
    path('customer/detail/<int:customer_id>/', CustomerDetailView.as_view(), name='customer-detail'),
    path('customer/update/<int:customer_id>/', CustomerUpdateView.as_view(), name='customer-update'),
    path('customer/delete/<int:customer_id>/', CustomerDeleteView.as_view(), name='customer-delete'),
    path('customer/all/', CustomerListView.as_view(), name='customer-list'),
    path('branch/add/<int:customer_id>/', CustomerBranchAddView.as_view(), name='branch-add'),
    path('branch/detail/<int:branch_id>/', CustomerBranchDetailView.as_view(), name='branch-detail'),
    path('branch/update/<int:branch_id>/', CustomerBranchUpdateView.as_view(), name='branch-update'),
    path('branch/delete/<int:branch_id>/', CustomerBranchDeleteView.as_view(), name='branch-delete'),
    path('branch/all/', CustomerBranchListView.as_view(), name='branch-list'),
]
