from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Flight, Booking, Airport, Airline
from .forms import FlightSearchForm, BookingForm
from django.db.models import Q
from datetime import date

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