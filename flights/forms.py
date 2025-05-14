# flights/forms.py
from django import forms
from django.core.validators import MinValueValidator
from django.utils import timezone
from datetime import date, datetime
from .models import Flight, Booking, Airport, Seat, Payment

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
        widgets = {
            'departure_time': forms.DateTimeInput(attrs={
                'type': 'datetime-local',
                'min': datetime.now().strftime('%Y-%m-%dT%H:%M')
            }),
            'arrival_time': forms.DateTimeInput(attrs={
                'type': 'datetime-local',
                'min': datetime.now().strftime('%Y-%m-%dT%H:%M')
            }),
            'total_seats': forms.NumberInput(attrs={'min': 1}),
            'available_seats': forms.NumberInput(attrs={'min': 0}),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        departure_airport = cleaned_data.get('departure_airport')
        arrival_airport = cleaned_data.get('arrival_airport')
        departure_time = cleaned_data.get('departure_time')
        arrival_time = cleaned_data.get('arrival_time')
        
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
        widgets = {
            'departure_time': forms.DateTimeInput(
                attrs={'type': 'datetime-local'},
                format='%Y-%m-%dT%H:%M'
            ),
            'arrival_time': forms.DateTimeInput(
                attrs={'type': 'datetime-local'},
                format='%Y-%m-%dT%H:%M'
            ),
            'total_seats': forms.NumberInput(attrs={'min': 1}),
            'available_seats': forms.NumberInput(attrs={'min': 0}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            self.initial['departure_time'] = self.instance.departure_time.strftime('%Y-%m-%dT%H:%M')
            self.initial['arrival_time'] = self.instance.arrival_time.strftime('%Y-%m-%dT%H:%M')
    
    def clean(self):
        cleaned_data = super().clean()
        departure_airport = cleaned_data.get('departure_airport')
        arrival_airport = cleaned_data.get('arrival_airport')
        departure_time = cleaned_data.get('departure_time')
        arrival_time = cleaned_data.get('arrival_time')
        
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