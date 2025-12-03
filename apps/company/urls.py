from django.urls import path
from .views import CarrierAddView

urlpatterns = [
    path('add/',CarrierAddView.as_view(), name='carrier-add'),
]
