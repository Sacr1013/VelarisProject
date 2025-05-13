from django import forms
from .models import Flight, Booking, Airport  # Importar Airport aquí
from django.core.validators import MinValueValidator
from datetime import date

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
            'min': date.today().isoformat(),  # <-- Aquí está la magia
        })
    )
    
    def clean(self):
        cleaned_data = super().clean()
        origin = cleaned_data.get('origin')
        destination = cleaned_data.get('destination')
        
        if origin and destination and origin == destination:
            raise forms.ValidationError("El origen y el destino no pueden ser iguales")
        
        return cleaned_data

class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['passengers']
        widgets = {
            'passengers': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1,
                'max': 10
            }),
        }

class FlightSelectForm(forms.Form):
    passengers = forms.IntegerField(
        min_value=1,
        max_value=10,
        initial=1,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'id': 'passengers-select'
        })
    )

# Añade estos nuevos formularios al final de flights/forms.py
class FlightCreateForm(forms.ModelForm):
    class Meta:
        model = Flight
        fields = '__all__'
        widgets = {
            'departure_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'arrival_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

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
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Formatea las fechas para el input datetime-local
        if self.instance.pk:
            self.initial['departure_time'] = self.instance.departure_time.strftime('%Y-%m-%dT%H:%M')
            self.initial['arrival_time'] = self.instance.arrival_time.strftime('%Y-%m-%dT%H:%M')