# flights/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('search/', views.flight_search, name='flight_search'),
    path('book/<int:flight_id>/', views.book_flight, name='book_flight'),
    path('select/<int:flight_id>/', views.select_flight, name='select_flight'),
    path('confirm/<int:booking_id>/', views.confirm_booking, name='confirm_booking'),
    path('management/flights/', views.admin_flight_list, name='admin_flight_list'),
    path('management/flights/create/', views.admin_create_flight, name='admin_create_flight'),
    path('management/flights/edit/<int:flight_id>/', views.admin_edit_flight, name='admin_edit_flight'),
    path('management/flights/delete/<int:flight_id>/', views.admin_delete_flight, name='admin_delete_flight'),
    
]