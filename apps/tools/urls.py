from django.urls import path
from .views import LeasingView, SalaryView, ProfitView
#todo klasyk
urlpatterns = [
    path('leasing/', LeasingView.as_view(), name='leasing'),
    path('salary/', SalaryView.as_view(), name='salary'),
    path('profit/', ProfitView.as_view(), name='profit'),
]
