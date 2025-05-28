# flights/urls.py
from django.urls import path
from django.contrib.admin.views.decorators import staff_member_required
from . import views



urlpatterns = [
    # Vistas públicas
    path('', views.home, name='home'), 
    path('search/', views.flight_search, name='flight_search'),
    path('book/<int:flight_id>/', views.book_flight, name='book_flight'),
    path('booking/<int:booking_id>/', views.booking_detail, name='booking_detail'),
    path('select/<int:flight_id>/', views.select_flight, name='select_flight'),
    path('confirm/<int:booking_id>/', views.confirm_booking, name='confirm_booking'),
    path('payment/<int:booking_id>/', views.payment_confirmation, name='payment_confirmation'),
    
    # Vistas de administración - Vuelos
    path('management/flights/', views.admin_flight_list, name='admin_flight_list'),
    path('management/flights/create/', views.admin_create_flight, name='admin_create_flight'),
    path('management/flights/edit/<int:flight_id>/', views.admin_edit_flight, name='admin_edit_flight'),
    path('management/flights/delete/<int:flight_id>/', views.admin_delete_flight, name='admin_delete_flight'),
    path('api/calculate-arrival/', views.calculate_arrival_time, name='calculate_arrival'),
    path('management/flights/export/', views.admin_export_flights, name='admin_export_flights'),
    # path('management/flights/import/', views.admin_import_flights, name='admin_import_flights'),

    # Vistas de administración - Usuarios
    path('management/users/', views.admin_user_list, name='admin_user_list'),
    path('management/users/<int:user_id>/', views.admin_user_detail, name='admin_user_detail'),
    path('management/users/<int:user_id>/edit/', views.admin_user_edit, name='admin_user_edit'),
    path('management/users/<int:user_id>/delete/', views.admin_user_delete, name='admin_user_delete'),
    path('management/users/<int:user_id>/notify-payment/', views.notify_pending_payment, name='notify_pending_payment'),
    
    # Vistas de administración - Aeropuertos
    path('management/airports/', views.admin_airport_list, name='admin_airport_list'),
    path('management/airports/create/', views.admin_airport_create, name='admin_airport_create'),
    path('management/airports/<int:airport_id>/edit/', views.admin_airport_edit, name='admin_airport_edit'),
    path('management/airports/<int:airport_id>/delete/', views.admin_airport_delete, name='admin_airport_delete'),
    
    # Vistas de administración - Pagos
    path('management/payments/', views.admin_payment_list, name='admin_payment_list'),
    path('management/payments/<int:payment_id>/', views.admin_payment_detail, name='admin_payment_detail'),
]