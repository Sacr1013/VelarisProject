# accounts/urls.py
from django.urls import path
from .views import (
    login_view, logout_view, dashboard,
    password_reset_request, password_reset_confirm,
    verify_email, RegisterView, 
    password_reset_complete,  # <-- Usa la clase
    admin_dashboard,
    booking_detail_dashboard, hide_booking, booking_pdf,
    profile_view, user_bookings,jetlag_calculator, anxiety_tips 
)


urlpatterns = [
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('dashboard/', dashboard, name='dashboard'),
    path('profile/', profile_view, name='profile'),
    path('bookings/', user_bookings, name='user_bookings'),
    path('jetlag/', jetlag_calculator, name='jetlag'),
    path('anxiety/', anxiety_tips, name='anxiety'),
    path('booking/<int:booking_id>/', booking_detail_dashboard, name='booking_detail_dashboard'),
    path('booking/hide/<int:booking_id>/', hide_booking, name='hide_booking'),
    path('booking/pdf/<int:booking_id>/', booking_pdf, name='booking_pdf'),
    path('register/', RegisterView.as_view(), name='register'),    
    path('reset-password/', password_reset_request, name='password_reset'),
    path('reset-password/done/', password_reset_complete, name='password_reset_done'),
    path('reset-password/<token>/', password_reset_confirm, name='password_reset_confirm'),
    path('verify-email/<token>/', verify_email, name='verify_email'),
    path('admin-dashboard/', admin_dashboard, name='admin_dashboard'),
]