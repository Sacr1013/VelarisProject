from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import LoginForm, CustomPasswordResetForm, CustomSetPasswordForm, CustomUserCreationForm
from .models import CustomUser
from django.views.generic import CreateView
from django.urls import reverse_lazy, reverse
from django.db.models import Q, Sum
from axes.decorators import axes_dispatch
from axes.models import AccessAttempt
from axes.utils import reset  # Nueva importación útil
from django.conf import settings
from flights.models import Flight, Booking, Airline, Airport 
from django.db.models import Count
from datetime import datetime, timedelta
from django.db.models import Case, When, IntegerField
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa

def login_view(request):
    if request.user.is_authenticated:
        return redirect('admin_dashboard' if request.user.is_staff else 'dashboard')

    form = LoginForm(request, data=request.POST or None)
    attempts_left = settings.AXES_FAILURE_LIMIT

    if request.method == 'POST':
        email = request.POST.get('username', '')
        attempt = AccessAttempt.objects.filter(username=email).first()
        
        if attempt:
            attempts_left = max(0, settings.AXES_FAILURE_LIMIT - attempt.failures_since_start)
            
            if attempt.failures_since_start >= settings.AXES_FAILURE_LIMIT:
                messages.error(request, 'Cuenta bloqueada. Espere 1 hora o contacte al administrador.', 
                             extra_tags='auth axes-lockout')
                return render(request, 'accounts/login.html', {'form': form, 'account_locked': True})

        if form.is_valid():
            user = authenticate(request, username=email, password=form.cleaned_data['password'])
            if user is not None:
                if not user.email_verified:
                    messages.warning(request, 'Verifique su email antes de iniciar sesión.',
                                   extra_tags='auth email-verification')
                    return redirect('login')
                
                if attempt:
                    reset(username=email)
                
                login(request, user)
                messages.success(request, f'Bienvenido, {user.get_short_name()}!', 
                               extra_tags='auth login-success')
                return redirect('admin_dashboard' if user.is_staff else 'dashboard')
        
        remaining_attempts = attempts_left - 1
        messages.error(request, f'Credenciales incorrectas. Intentos restantes: {remaining_attempts}', 
                     extra_tags='auth login-failed')
        return redirect(f"{reverse('login')}?login_failed=true&attempts={remaining_attempts}")

    return render(request, 'accounts/login.html', {'form': form, 'attempts_left': attempts_left})

# views.py (actualización)
@login_required
def admin_dashboard(request):
    if not request.user.is_staff:
        return render(request, 'accounts/admin_dashboard.html', {
            'show_permission_denied': True
        })
    
    # Estadísticas principales (CORRECCIÓN DE CLAVES Y NUEVAS ESTADÍSTICAS)
    today = datetime.now().date()
    stats = {
        'active_flights': Flight.objects.filter(departure_time__date=today).count(),
        'today_bookings': Booking.objects.filter(booking_date__date=today).count(),
        'total_users': CustomUser.objects.count(),
        'today_income': Booking.objects.filter(
            status='CONFIRMED',
            booking_date__date=today
        ).aggregate(Sum('total_price'))['total_price__sum'] or 0,
        'monthly_income': Booking.objects.filter(
            status='CONFIRMED',
            booking_date__month=today.month
        ).aggregate(Sum('total_price'))['total_price__sum'] or 0,
    }
    
    # Aeropuertos más populares (NUEVA CONSULTA)
    airports = Airport.objects.annotate(
        total_flights=Count('departures')
    ).order_by('-total_flights')[:6]
    
    # Resto de datos
    recent_flights = Flight.objects.select_related(
        'airline', 'departure_airport', 'arrival_airport'
    ).order_by('departure_time')[:5]
    
    recent_bookings = Booking.objects.select_related(
        'user', 'flight'
    ).order_by('-booking_date')[:5]
    
    return render(request, 'accounts/admin_dashboard.html', {
        'stats': stats,
        'recent_flights': recent_flights,
        'recent_bookings': recent_bookings,
        'airports': airports,  # NOMBRE CORRECTO DE VARIABLE
        'show_admin_messages': True
    })

def logout_view(request):
    logout(request)
    messages.success(request, 'Has cerrado sesión correctamente')
    return redirect('home')

@login_required
def dashboard(request):
    hidden_bookings = request.session.get('hidden_bookings', [])
    
    selected_bookings = request.user.booking_set.filter(status='SELECTED').exclude(id__in=hidden_bookings)
    
    recent_bookings = request.user.booking_set.exclude(status='SELECTED').exclude(id__in=hidden_bookings).annotate(
        status_priority=Case(
            When(status='CONFIRMED', then=0),
            default=1,
            output_field=IntegerField(),
        )
    ).order_by('status_priority', '-flight__departure_time')
    
    confirmed_upcoming = request.user.booking_set.filter(status='CONFIRMED').exclude(id__in=hidden_bookings).order_by('flight__departure_time')
    
    return render(request, 'accounts/dashboard.html', {
        'selected_bookings': selected_bookings,
        'recent_bookings': recent_bookings,
        'confirmed_upcoming': confirmed_upcoming
    })
def booking_detail_dashboard(request, booking_id):
    booking = get_object_or_404(
        request.user.booking_set.select_related('flight__departure_airport', 'flight__arrival_airport').prefetch_related('seats'), 
        id=booking_id
    )
    return render(request, 'accounts/user_dashboard/booking_detail_dsh.html', {'booking': booking})

def hide_booking(request, booking_id):
    hidden_bookings = request.session.get('hidden_bookings', [])
    if booking_id not in hidden_bookings:
        hidden_bookings.append(booking_id)
        request.session['hidden_bookings'] = hidden_bookings
    return redirect('dashboard')

def booking_pdf(request, booking_id):
    booking = get_object_or_404(request.user.booking_set, id=booking_id)
    
    template_path = 'accounts/user_dashboard/booking_pdf.html'
    context = {'booking': booking, 'user': request.user}
    
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'filename="reserva_{booking.booking_reference}.pdf"'
    
    template = get_template(template_path)
    html = template.render(context)

    # Generar PDF
    pisa_status = pisa.CreatePDF(
        html, 
        dest=response,
        encoding='UTF-8'
    )
    
    if pisa_status.err:
        return HttpResponse('Error al generar el PDF', status=500)
    return response

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
                return redirect('password_reset_done')
            except CustomUser.DoesNotExist:
                messages.error(request, 'No existe una cuenta con este correo electrónico')
    else:
        form = CustomPasswordResetForm()
    return render(request, 'accounts/password_reset_form.html', {'form': form})

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

def password_reset_complete(request):
    return render(request, 'accounts/password_reset_done.html')

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