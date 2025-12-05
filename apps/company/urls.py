from django.urls import path

from .views import (CarrierAddView, CarrierDetailView,
                    CarrierUpdateView, CarrierDeleteView,
                    CarrierListView, CustomerAddView, CustomerDetailView,
                    CustomerUpdateView, CustomerDeleteView,
                    CustomerListView)

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
]
