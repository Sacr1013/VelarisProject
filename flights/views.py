from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Flight, Booking, Airport, Airline
from .forms import FlightSearchForm, BookingForm, FlightSelectForm
from django.db.models import Q
from datetime import date
from django.contrib.auth.decorators import user_passes_test
from .forms import FlightCreateForm, FlightEditForm
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.conf import settings
from django.core.mail import send_mail

def home(request):
    today = date.today()
    featured_flights = Flight.objects.filter(
        is_active=True,
        departure_time__gte=date.today()
    ).order_by('departure_time')[:6]
    
    airports = Airport.objects.all()
    
    if request.method == 'POST':
        form = FlightSearchForm(request.POST)
        if form.is_valid():
            origin = form.cleaned_data['origin']
            destination = form.cleaned_data['destination']
            departure_date = form.cleaned_data['departure_date']
            
            flights = Flight.objects.filter(
                departure_airport=origin,
                arrival_airport=destination,
                departure_time__date=departure_date,
                is_active=True,
                available_seats__gt=0
            ).order_by('departure_time')
            
            return render(request, 'flights/flight_list.html', {
                'flights': flights,
                'origin': origin,
                'destination': destination,
                'departure_date': departure_date,
            })
    else:
        form = FlightSearchForm()
    
    return render(request, 'home.html', {
        'today': today,
        'featured_flights': featured_flights,
        'airports': airports,
        'form': form,
    })

def flight_search(request):
    if request.method == 'POST':
        form = FlightSearchForm(request.POST)
        if form.is_valid():
            origin = form.cleaned_data['origin']
            destination = form.cleaned_data['destination']
            departure_date = form.cleaned_data['departure_date']
            
            flights = Flight.objects.filter(
                Q(departure_airport=origin) &
                Q(arrival_airport=destination) &
                Q(departure_time__date=departure_date) &
                Q(is_active=True) &
                Q(available_seats__gt=0)
            ).order_by('departure_time')
            
            return render(request, 'flights/flight_list.html', {
                'flights': flights,
                'origin': origin,
                'destination': destination,
                'departure_date': departure_date,
                'form': form
            })
    else:
        form = FlightSearchForm()
    
    return render(request, 'flights/flight_list.html', {'form': form})


@login_required
def book_flight(request, flight_id):
    flight = get_object_or_404(Flight, id=flight_id, is_active=True)
    
    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.user = request.user
            booking.flight = flight
            booking.save()
            
            booking.send_confirmation_email()
            
            messages.success(request, 'Tu reserva ha sido confirmada. Hemos enviado un correo con los detalles.')
            return redirect('dashboard')
    else:
        form = BookingForm()
    
    return render(request, 'flights/booking_form.html', {
        'flight': flight,
        'form': form,
    })

@login_required
def select_flight(request, flight_id):
    flight = get_object_or_404(Flight, id=flight_id, is_active=True)
    
    if request.method == 'POST':
        form = FlightSelectForm(request.POST)
        if form.is_valid():
            # Crear booking en estado "seleccionado"
            booking = Booking.objects.create(
                user=request.user,
                flight=flight,
                passengers=form.cleaned_data['passengers'],
                total_price=flight.price * form.cleaned_data['passengers'],
                status='SELECTED'
            )
            
            messages.success(request, 'Vuelo seleccionado. Puedes completar la reserva cuando desees.')
            return redirect('dashboard')
    
    else:
        form = FlightSelectForm()
    
    return render(request, 'flights/select_flight.html', {
        'flight': flight,
        'form': form
    })

@login_required
def confirm_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    
    if booking.status == 'SELECTED':
        booking.status = 'PENDING'  # O 'CONFIRMED' si el pago es inmediato
        booking.save()
        booking.send_confirmation_email()
        messages.success(request, 'Reserva confirmada con éxito!')
    
    return redirect('dashboard')

def is_admin(user):
    return user.is_authenticated and user.is_staff

@user_passes_test(is_admin)
def admin_flight_list(request):
    if not request.user.is_staff:
        return redirect('dashboard')
    
    # Filtros
    flight_number = request.GET.get('flight_number')
    origin = request.GET.get('origin')
    destination = request.GET.get('destination')
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    airline = request.GET.get('airline')
    status = request.GET.get('status', 'active')  # active/inactive/all
    
    # Consulta base con select_related
    flights = Flight.objects.all().select_related(
        'airline', 'departure_airport', 'arrival_airport'
    )
    
    # Aplicar filtros
    if flight_number:
        flights = flights.filter(flight_number__icontains=flight_number)
    if origin:
        flights = flights.filter(departure_airport__code__icontains=origin)
    if destination:
        flights = flights.filter(arrival_airport__code__icontains=destination)
    if date_from:
        flights = flights.filter(departure_time__date__gte=date_from)
    if date_to:
        flights = flights.filter(departure_time__date__lte=date_to)
    if airline:
        flights = flights.filter(airline__name__icontains=airline)
    if status == 'active':
        flights = flights.filter(is_active=True)
    elif status == 'inactive':
        flights = flights.filter(is_active=False)
    
    flights = flights.order_by('-departure_time')
    
    # Paginación
    paginator = Paginator(flights, 15)
    page = request.GET.get('page')
    
    try:
        flights = paginator.page(page)
    except PageNotAnInteger:
        flights = paginator.page(1)
    except EmptyPage:
        flights = paginator.page(paginator.num_pages)
    
    # Obtener aeropuertos para el dropdown de filtros
    airports = Airport.objects.all().order_by('city')
    airlines = Airline.objects.all().order_by('name')
    
    return render(request, 'flights/admin/flight_list.html', {
        'flights': flights,
        'airports': airports,
        'airlines': airlines,
        'filter_values': {
            'origin': origin or '',
            'destination': destination or '',
            'date_from': date_from or '',
            'date_to': date_to or '',
            'airline': airline or '',
            'status': status,
        }
    })

@user_passes_test(is_admin)
def admin_create_flight(request):
    if request.method == 'POST':
        form = FlightCreateForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Vuelo creado exitosamente!')
            return redirect('admin_flight_list')
    else:
        form = FlightCreateForm()
    
    return render(request, 'flights/admin/flight_form.html', {
        'form': form,
        'title': 'Crear nuevo vuelo'
    })

@user_passes_test(is_admin)
def admin_edit_flight(request, flight_id):
    flight = get_object_or_404(Flight.objects.select_related('airline', 'departure_airport', 'arrival_airport'), id=flight_id)
    
    if request.method == 'POST':
        # Manejar eliminación de reserva
        if 'remove_booking' in request.POST:
            booking_id = request.POST.get('remove_booking')
            try:
                booking = Booking.objects.get(id=booking_id, flight=flight)
                booking.cancel(notify_user=True)
                messages.success(request, 'Reserva eliminada correctamente.')
                return redirect('admin_edit_flight', flight_id=flight.id)
            except Booking.DoesNotExist:
                messages.error(request, 'La reserva no existe')
            except Exception as e:
                messages.error(request, f'Error al eliminar: {str(e)}')
            return redirect('admin_edit_flight', flight_id=flight.id)
        
        # Manejar actualización de vuelo
        form = FlightEditForm(request.POST, instance=flight)
        if form.is_valid():
            form.save()
            messages.success(request, 'Vuelo actualizado exitosamente!')
            return redirect('admin_edit_flight', flight_id=flight.id)
    else:
        form = FlightEditForm(instance=flight)
    
    bookings = Booking.objects.filter(flight=flight).select_related('user')
    return render(request, 'flights/admin/flight_form.html', {
        'form': form,
        'title': 'Editar Vuelo',
        'flight': flight,
        'bookings': bookings,
    })

def send_cancellation_email(self, booking):
    subject = 'Cancelación de tu reserva en Velaris'
    message = f'''
    Hola {booking.user.username},
    
    Lamentamos informarte que tu reserva ha sido cancelada:
    
    Número de reserva: {booking.booking_reference}
    Vuelo: {booking.flight}
    Fecha: {booking.flight.departure_time.strftime('%d/%m/%Y %H:%M')}
    
    {'El equipo de Velaris se comunicará contigo para gestionar el reembolso.' if booking.status == 'CONFIRMED' else ''}
    
    Si tienes alguna duda, por favor contáctanos.
    
    Atentamente,
    El equipo de Velaris
    '''
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [booking.user.email],
        fail_silently=False,
    )

@user_passes_test(is_admin)
def admin_delete_flight(request, flight_id):
    flight = get_object_or_404(Flight, id=flight_id)
    
    if request.method == 'POST':
        try:
            flight.delete()
            messages.success(request, 'Vuelo eliminado correctamente.')
            return redirect('admin_flight_list')
        except Exception as e:
            messages.error(request, f'Error al eliminar: {str(e)}')
            return redirect('admin_flight_list')
    
    # Verifica si tiene reservas asociadas
    has_bookings = Booking.objects.filter(flight=flight).exists()
    
    return render(request, 'flights/admin/flight_confirm_delete.html', {
        'flight': flight,
        'has_bookings': has_bookings
    })
    