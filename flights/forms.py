# flights/forms.py
from django import forms
from django.core.validators import MinValueValidator
from django.utils import timezone
from datetime import date, datetime, timedelta
from .models import Flight, Booking, Airport, Seat, Payment
import random
import string


class FlightSearchForm(forms.Form):
    origin = forms.ModelChoiceField(
        queryset=Airport.objects.all(),
        label="Origen",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    destination = forms.ModelChoiceField(
        queryset=Airport.objects.all(),
        label="Destino",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    departure_date = forms.DateField(
        label="Fecha de salida",
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date',
            'min': date.today().isoformat(),
        })
    )
    
    def clean(self):
        cleaned_data = super().clean()
        origin = cleaned_data.get('origin')
        destination = cleaned_data.get('destination')
        
        if origin and destination and origin == destination:
            raise forms.ValidationError("El origen y el destino no pueden ser iguales")
        
        return cleaned_data

class SeatSelectionForm(forms.Form):
    seats = forms.MultipleChoiceField(
        widget=forms.CheckboxSelectMultiple,
        required=True,
        label="Selecciona tus asientos"
    )
    
    def __init__(self, *args, **kwargs):
        flight = kwargs.pop('flight', None)
        super().__init__(*args, **kwargs)
        
        if flight:
            available_seats = Seat.objects.filter(
                flight=flight,
                status='AVAILABLE'
            ).values_list('seat_number', 'seat_number')
            
            self.fields['seats'].choices = available_seats

class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['passengers']
        widgets = {
            'passengers': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1,
                'max': 10,
                'id': 'passengers-input'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        self.flight = kwargs.pop('flight', None)
        super().__init__(*args, **kwargs)
        
        if self.flight:
            self.fields['passengers'].widget.attrs['max'] = self.flight.available_seats

class PaymentConfirmationForm(forms.ModelForm):  # ¡Asegúrate de que hereda de ModelForm!
    class Meta:
        model = Payment
        fields = ['payment_method']
        widgets = {
            'payment_method': forms.RadioSelect(choices=Payment.PAYMENT_METHODS)
        }
    
    def __init__(self, *args, **kwargs):
        # Elimina el argumento 'booking' si existe para evitar conflictos
        kwargs.pop('booking', None)
        super().__init__(*args, **kwargs)
        self.fields['payment_method'].initial = 'QR'


class AirportForm(forms.ModelForm):
    class Meta:
        model = Airport
        fields = '__all__'
        widgets = {
            'code': forms.TextInput(attrs={
                'class': 'form-control', 
                'maxlength': '3', 
                'style': 'text-transform:uppercase'
            }),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'city': forms.TextInput(attrs={'class': 'form-control'}),
            'country': forms.TextInput(attrs={'class': 'form-control'}),
            'timezone': forms.Select(attrs={'class': 'form-control'}, choices=[
                ('America/Bogota', 'Bogotá (GMT-5)'),
                ('America/New_York', 'Nueva York (GMT-5/-4)'),
                ('America/Los_Angeles', 'Los Ángeles (GMT-8/-7)'),
                ('Europe/Madrid', 'Madrid (GMT+1/+2)'),
                ('UTC', 'UTC'),
            ]),
        }
    
    def clean_code(self):
        code = self.cleaned_data['code']
        return code.upper()

class FlightCreateForm(forms.ModelForm):
    class Meta:
        model = Flight
        fields = '__all__'
        exclude = ['airline']
        widgets = {
            'departure_time': forms.DateTimeInput(attrs={
                'type': 'datetime-local',
                'min': datetime.now().strftime('%Y-%m-%dT%H:%M')
            }),
            'arrival_time': forms.DateTimeInput(attrs={
                'type': 'datetime-local',
                'min': datetime.now().strftime('%Y-%m-%dT%H:%M')
            }),
            'total_seats': forms.NumberInput(attrs={
                'min': 1,
                'max': 200  # Límite máximo realista
            }),
            'available_seats': forms.NumberInput(attrs={
                'min': 0,
                'max': 200  # Debe coincidir con total_seats
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.instance.pk:
            self.fields['flight_number'].initial = self.generate_unique_flight_number()
            self.fields['flight_number'].widget.attrs['readonly'] = True
            self.fields['flight_number'].required = True

    def generate_unique_flight_number(self):
        while True:
            suffix = ''.join(random.choices(string.digits, k=4))
            flight_number = f"VL{suffix}"
            if not Flight.objects.filter(flight_number=flight_number).exists():
                return flight_number
    
    def clean(self):
        cleaned_data = super().clean()
        departure_airport = cleaned_data.get('departure_airport')
        arrival_airport = cleaned_data.get('arrival_airport')
        departure_time = cleaned_data.get('departure_time')
        arrival_time = cleaned_data.get('arrival_time')
        flight_number = cleaned_data.get('flight_number')
        total_seats = cleaned_data.get('total_seats')
        available_seats = cleaned_data.get('available_seats')

        if departure_time and departure_time < timezone.now() + timedelta(hours=1):
            self.add_error('departure_time', 
                "¡Los vuelos deben crearse al menos con 1 hora de anticipación!")
            
        if total_seats and available_seats:
            if available_seats > total_seats:
                self.add_error('available_seats', 
                    "¡Los asientos disponibles no pueden ser mayores al total!")
        if total_seats <= 0:
                self.add_error('total_seats',
                    "¡El total de asientos debe ser mayor a 0!")

        if flight_number and Flight.objects.filter(flight_number=flight_number).exists():
            self.add_error('flight_number', 'Este número de vuelo ya existe. Recarga para generar uno nuevo.')
        
        if departure_airport and arrival_airport and departure_airport == arrival_airport:
            raise forms.ValidationError("El aeropuerto de origen y destino no pueden ser iguales")
        
        if departure_time and arrival_time and departure_time >= arrival_time:
            raise forms.ValidationError("La hora de llegada debe ser posterior a la de salida")
        
        if departure_time and departure_time < timezone.now():
            raise forms.ValidationError("No se pueden crear vuelos en fechas pasadas")
        

        return cleaned_data

class FlightEditForm(forms.ModelForm):
    class Meta:
        model = Flight
        fields = '__all__'
        exclude = ['airline']
        widgets = {
            'departure_time': forms.DateTimeInput(
                attrs={'type': 'datetime-local'},
                format='%Y-%m-%dT%H:%M'
            ),
            'arrival_time': forms.DateTimeInput(
                attrs={'type': 'datetime-local'},
                format='%Y-%m-%dT%H:%M'
            ),
            'total_seats': forms.NumberInput(attrs={
                'min': 1,
                'max': 200  # Límite máximo realista
            }),
            'available_seats': forms.NumberInput(attrs={
                'min': 0,
                'max': 200  # Debe coincidir con total_seats
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            if 'flight_number' in self.fields:
                self.fields['flight_number'].disabled = True
                local_departure = timezone.localtime(self.instance.departure_time)
                local_arrival = timezone.localtime(self.instance.arrival_time)
                self.initial['departure_time'] = local_departure.strftime('%Y-%m-%dT%H:%M')
                self.initial['arrival_time'] = local_arrival.strftime('%Y-%m-%dT%H:%M')
    def clean_departure_time(self):
        departure_time = self.cleaned_data['departure_time']
        if self.instance.departure_time < timezone.now():
            raise forms.ValidationError("¡No se puede modificar un vuelo histórico!")
        return departure_time

    def clean(self):
        cleaned_data = super().clean()
        departure_airport = cleaned_data.get('departure_airport')
        arrival_airport = cleaned_data.get('arrival_airport')
        departure_time = cleaned_data.get('departure_time')
        arrival_time = cleaned_data.get('arrival_time')
        total_seats = cleaned_data.get('total_seats')
        available_seats = cleaned_data.get('available_seats')

        if total_seats and available_seats:
            if available_seats > total_seats:
                self.add_error('available_seats', 
                    "¡Los asientos disponibles no pueden ser mayores al total!")
        if self.instance.pk:
            booked_seats = self.instance.total_seats - self.instance.available_seats
            if cleaned_data.get('total_seats') < booked_seats:
                self.add_error('total_seats', 
                    f"No puede reducir la capacidad debajo de {booked_seats} asientos reservados!")
        if departure_airport and arrival_airport and departure_airport == arrival_airport:
            raise forms.ValidationError("El aeropuerto de origen y destino no pueden ser iguales")
        
        if departure_time and arrival_time and departure_time >= arrival_time:
            raise forms.ValidationError("La hora de llegada debe ser posterior a la de salida")
        
        return cleaned_data
    
class FlightSelectForm(forms.Form):
    passengers = forms.IntegerField(
        label="Número de pasajeros",
        min_value=1,
        max_value=10,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'min': 1,
            'max': 10,
            'id': 'passengers-input'
        })
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)