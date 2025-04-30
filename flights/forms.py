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