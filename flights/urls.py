# flights/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('search/', views.flight_search, name='flight_search'),
    path('book/<int:flight_id>/', views.book_flight, name='book_flight'),
]