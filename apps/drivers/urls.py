from django.urls import path

from .views import DriverListView, DriverAddView, DriverDetailView, DriverUpdateView, DriverDeleteView
#todo jak w poprzednich plikach
urlpatterns = [
    path('add/<int:carrier_id>/', DriverAddView.as_view(), name='driver-add'),
    path('detail/<int:driver_id>/', DriverDetailView.as_view(), name='driver-detail'),
    path('update/<int:driver_id>/', DriverUpdateView.as_view(), name='driver-update'),
    path('delete/<int:driver_id>/', DriverDeleteView.as_view(), name='driver-delete'),
    path('all/', DriverListView.as_view(), name='driver-list'),
]
