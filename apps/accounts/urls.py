# todo nie bede pisał wiecj togo w innych plikach ale przerobie ci ten plik tak jak uważam ze powinnien wygladać i po mojemu DLA MNIE jest wygodniej
from django.urls import path

from apps.accounts import views

urlpatterns = [
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('register/', views.RegisterView.as_view(), name='register'),
    path('profile/', views.ProfileView.as_view(), name='profile'),
    path('profile/delete-image/', views.ProfileImageDeleteView.as_view(), name='profile-delete-image'),
]
