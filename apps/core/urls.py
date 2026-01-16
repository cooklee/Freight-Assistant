from django.urls import path

from .views import DashboardView
#todo jak wyżej
urlpatterns = [
    path("", DashboardView.as_view(), name="dashboard"),
]
