# accounts/urls.py
from django.urls import path
from .views import (
    login_view, logout_view, dashboard,
    password_reset_request, password_reset_confirm,
    verify_email, RegisterView,   # <-- Usa la clase
    admin_dashboard
)


urlpatterns = [
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('dashboard/', dashboard, name='dashboard'),
    path('register/', RegisterView.as_view(), name='register'),    
    path('reset-password/', password_reset_request, name='password_reset'),
    path('reset-password/<token>/', password_reset_confirm, name='password_reset_confirm'),
    path('verify-email/<token>/', verify_email, name='verify_email'),
    path('admin-dashboard/', admin_dashboard, name='admin_dashboard'),
]