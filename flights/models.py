from django.db import models
from accounts.models import CustomUser
from django.core.validators import MinValueValidator
from django.core.mail import send_mail
from django.conf import settings
import random
import string

class Airport(models.Model):
    code = models.CharField(max_length=3, unique=True)
    name = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    
    class Meta:
        ordering = ['city']
    
    def __str__(self):
        return f"{self.code} - {self.city}"

class Airline(models.Model):
    name = models.CharField(max_length=100)
    logo = models.ImageField(upload_to='airlines/', blank=True, null=True)
    
    def __str__(self):
        return self.name

class Flight(models.Model):
    flight_number = models.CharField(max_length=10)
    airline = models.ForeignKey(Airline, on_delete=models.CASCADE)
    departure_airport = models.ForeignKey(Airport, on_delete=models.CASCADE, related_name='departures')
    arrival_airport = models.ForeignKey(Airport, on_delete=models.CASCADE, related_name='arrivals')
    departure_time = models.DateTimeField()
    arrival_time = models.DateTimeField()
    price = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        validators=[MinValueValidator(0)],
        help_text="Precio en pesos colombianos (COP)"
    )
    available_seats = models.IntegerField()
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['departure_time']
    
    def __str__(self):
        return f"{self.airline} {self.flight_number}: {self.departure_airport.code} → {self.arrival_airport.code}"
    
    @property
    def duration(self):
        return self.arrival_time - self.departure_time

class Booking(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    flight = models.ForeignKey(Flight, on_delete=models.CASCADE)
    booking_date = models.DateTimeField(auto_now_add=True)
    passengers = models.IntegerField(default=1)
    total_price = models.DecimalField(max_digits=12, decimal_places=2)
    booking_reference = models.CharField(max_length=8, unique=True)
    
    class Meta:
        ordering = ['-booking_date']
    
    def __str__(self):
        return f"Reserva {self.booking_reference} - {self.user.username}"
    
    def save(self, *args, **kwargs):
        if not self.booking_reference:
            self.booking_reference = self.generate_reference()
        if not self.total_price:
            self.total_price = self.flight.price * self.passengers
        super().save(*args, **kwargs)
    
    def generate_reference(self):
        return ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
    
    def send_confirmation_email(self):
        subject = 'Confirmación de reserva en Velaris 2.0'
        message = f'''
        Hola {self.user.username},
        
        Tu reserva ha sido confirmada:
        
        Número de reserva: {self.booking_reference}
        Vuelo: {self.flight}
        Fecha: {self.flight.departure_time.strftime('%d/%m/%Y %H:%M')}
        Pasajeros: {self.passengers}
        Precio total: ${self.total_price:,.2f} COP
        
        Gracias por elegir Velaris 2.0!
        '''
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [self.user.email],
            fail_silently=False,
        )