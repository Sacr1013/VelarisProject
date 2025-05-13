from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import LoginForm, CustomPasswordResetForm, CustomSetPasswordForm, CustomUserCreationForm
from .models import CustomUser
from django.views.generic import CreateView
from django.urls import reverse_lazy
from django.db.models import Q 
from axes.decorators import axes_dispatch
from axes.models import AccessAttempt
from axes.utils import reset  # Nueva importación útil
from django.conf import settings
from flights.models import Flight, Booking, Airline 
from django.db.models import Count
from datetime import datetime, timedelta

def login_view(request):
    if request.user.is_authenticated:
        # Redirige a admin_dashboard si es staff, o al dashboard normal
        return redirect('admin_dashboard' if request.user.is_staff else 'dashboard')

    form = LoginForm(request, data=request.POST or None)
    attempts_left = 3  # Valor por defecto

    if request.method == 'POST':
        email = request.POST.get('username', '')
        
        # Verificar intentos fallidos previos
        attempt = AccessAttempt.objects.filter(username=email).first()
        if attempt:
            attempts_left = max(0, settings.AXES_FAILURE_LIMIT - attempt.failures_since_start)
            
            if attempt.failures_since_start >= settings.AXES_FAILURE_LIMIT:
                messages.error(request, f'Cuenta bloqueada. Espere {settings.AXES_COOLOFF_TIME} hora(s) o contacte al administrador.')
                return render(request, 'accounts/login.html', {
                    'form': form,
                    'attempts_left': 0,
                    'account_locked': True
                })

        if form.is_valid():
            user = authenticate(request, username=email, password=form.cleaned_data['password'])
            
            if user is not None:
                if not user.email_verified:
                    messages.warning(request, 'Verifique su email antes de iniciar sesión.')
                    return redirect('login')
                
                # Resetear intentos fallidos si existen
                if attempt:
                    reset(username=email)
                
                login(request, user)
                # Cambio clave: Redirige a admin_dashboard si es staff
                return redirect('admin_dashboard' if user.is_staff else 'dashboard')
        
        # Mostrar intentos restantes si el formulario no es válido
        messages.error(request, f'Credenciales incorrectas. Intentos restantes: {attempts_left - 1}')
        return render(request, 'accounts/login.html', {
            'form': form,
            'attempts_left': attempts_left - 1
        })

    return render(request, 'accounts/login.html', {
        'form': form,
        'attempts_left': attempts_left
    })

@login_required
def admin_dashboard(request):
    if not request.user.is_staff:
        return redirect('dashboard')
    
    # Estadísticas principales
    total_flights = Flight.objects.count()
    active_bookings = Booking.objects.filter(status='CONFIRMED').count()
    pending_bookings = Booking.objects.filter(status='PENDING').count()
    airlines = Airline.objects.annotate(flight_count=Count('flight'))
    
    # Vuelos hoy/próximos
    today = datetime.now().date()
    flights_today = Flight.objects.filter(departure_time__date=today).count()
    flights_next_week = Flight.objects.filter(
        departure_time__range=(today, today + timedelta(days=7))
    ).count()
    
    # Últimas reservas (5 más recientes)
    recent_bookings = Booking.objects.select_related('user', 'flight').order_by('-booking_date')[:5]
    
    return render(request, 'accounts/admin_dashboard.html', {
        'total_flights': total_flights,
        'active_bookings': active_bookings,
        'pending_bookings': pending_bookings,
        'flights_today': flights_today,
        'flights_next_week': flights_next_week,
        'recent_bookings': recent_bookings,
        'airlines': airlines,
    })

def logout_view(request):
    logout(request)
    messages.success(request, 'Has cerrado sesión correctamente')
    return redirect('home')

@login_required
def dashboard(request):
    selected_bookings = request.user.booking_set.filter(status='SELECTED')
    confirmed_bookings = request.user.booking_set.exclude(status='SELECTED')
    
    return render(request, 'accounts/dashboard.html', {
        'selected_bookings': selected_bookings,
        'confirmed_bookings': confirmed_bookings
    })

def password_reset_request(request):
    if request.method == 'POST':
        form = CustomPasswordResetForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            try:
                user = CustomUser.objects.get(email=email)
                user.send_password_reset_email()
                messages.success(
                    request, 
                    'Se ha enviado un correo con instrucciones para restablecer tu contraseña. ' +
                    'Revisa tu bandeja de entrada.'
                )
                return redirect('login')
            except CustomUser.DoesNotExist:
                messages.error(request, 'No existe una cuenta con este correo electrónico')
    else:
        form = CustomPasswordResetForm()
    return render(request, 'accounts/password_reset.html', {'form': form})

def password_reset_confirm(request, token):
    try:
        user = CustomUser.objects.get(verification_token=token)
    except CustomUser.DoesNotExist:
        messages.error(request, 'El enlace de restablecimiento no es válido o ha expirado')
        return redirect('login')
    
    if request.method == 'POST':
        form = CustomSetPasswordForm(user, request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, '¡Tu contraseña ha sido restablecida correctamente! Ahora puedes iniciar sesión.')
            return redirect('login')
    else:
        form = CustomSetPasswordForm(user)
    
    return render(request, 'accounts/password_reset_confirm.html', {
        'form': form,
        'validlink': True
    })

def verify_email(request, token):
    try:
        user = CustomUser.objects.get(verification_token=token)
        if not user.email_verified:
            user.email_verified = True
            user.is_active = True
            user.save()
            messages.success(
                request,
                '¡Tu correo electrónico ha sido verificado correctamente! ' +
                'Ahora puedes iniciar sesión.'
            )
        else:
            messages.info(request, 'Este correo electrónico ya había sido verificado anteriormente')
    except CustomUser.DoesNotExist:
        messages.error(request, 'El enlace de verificación no es válido o ha expirado')
    
    return redirect('login')

class RegisterView(CreateView):
    form_class = CustomUserCreationForm
    template_name = 'accounts/register.html'
    success_url = reverse_lazy('login')

    def form_valid(self, form):
        response = super().form_valid(form)
        user = form.instance
        user.is_active = False  # Usuario inactivo hasta verificación
        user.save()
        
        # Enviar correo de verificación
        try:
            user.send_verification_email()
            messages.success(
                self.request,
                '¡Registro exitoso! ' +
                'Por favor revisa tu correo electrónico y haz clic en el enlace de verificación.'
            )
        except Exception as e:
            messages.error(
                self.request,
                'Ocurrió un error al enviar el correo de verificación. ' +
                'Por favor contacta al soporte técnico.'
            )
        
        return response

    def form_invalid(self, form):
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(self.request, f"{field}: {error}")
        return super().form_invalid(form)
