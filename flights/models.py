# flights/models.py
import logging
logger = logging.getLogger(__name__)
import pytz
import qrcode
import random
import string
from io import BytesIO
from datetime import datetime, timedelta
from django.db import models
from django.db.models import F, Q
from django.core.mail import send_mail
from django.core.files.base import ContentFile
from django.conf import settings
from django.core.validators import MinValueValidator
from accounts.models import CustomUser
from django.utils import timezone

class Airport(models.Model):
    """
    Modelo para aeropuertos con información de zona horaria para cálculo automático de horas
    """
    code = models.CharField(max_length=3, unique=True, verbose_name="Código IATA")
    name = models.CharField(max_length=100, verbose_name="Nombre del aeropuerto")
    city = models.CharField(max_length=100, verbose_name="Ciudad")
    country = models.CharField(max_length=100, verbose_name="País")
    timezone = models.CharField(
        max_length=50, 
        default='UTC',
        verbose_name="Zona Horaria",
        help_text="Ejemplo: America/Bogota"
    )
    
    class Meta:
        ordering = ['city']
        verbose_name = "Aeropuerto"
        verbose_name_plural = "Aeropuertos"
    
    def __str__(self):
        return f"{self.code} - {self.city}"
    
    def get_timezone(self):
        """Devuelve el objeto timezone para cálculos horarios"""
        return pytz.timezone(self.timezone)

class Airline(models.Model):
    """
    Modelo para aerolíneas con logo
    """
    name = models.CharField(max_length=100, verbose_name="Nombre")
    logo = models.ImageField(
        upload_to='airlines/', 
        blank=True, 
        null=True,
        verbose_name="Logo"
    )
    
    class Meta:
        verbose_name = "Aerolínea"
        verbose_name_plural = "Aerolíneas"
    
    def __str__(self):
        return self.name

class Flight(models.Model):
    """
    Modelo principal para vuelos con gestión de asientos y validaciones
    """
    flight_number = models.CharField(
        max_length=10, 
        unique=True,
        verbose_name="Número de vuelo"
    )
    airline = models.ForeignKey(
        Airline, 
        on_delete=models.CASCADE,
        verbose_name="Aerolínea"
    )
    departure_airport = models.ForeignKey(
        Airport, 
        on_delete=models.CASCADE, 
        related_name='departures',
        verbose_name="Aeropuerto de salida"
    )
    arrival_airport = models.ForeignKey(
        Airport, 
        on_delete=models.CASCADE, 
        related_name='arrivals',
        verbose_name="Aeropuerto de llegada"
    )
    departure_time = models.DateTimeField(verbose_name="Hora de salida")
    arrival_time = models.DateTimeField(verbose_name="Hora de llegada")
    price = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name="Precio (COP)",
        help_text="Precio en pesos colombianos"
    )
    total_seats = models.PositiveIntegerField(
        default=180,
        verbose_name="Total de asientos"
    )
    available_seats = models.PositiveIntegerField(
        verbose_name="Asientos disponibles"
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name="Activo",
        help_text="Indica si el vuelo está disponible para reservas"
    )
    
    class Meta:
        ordering = ['departure_time']
        verbose_name = "Vuelo"
        verbose_name_plural = "Vuelos"
        indexes = [
            models.Index(fields=['departure_time']),
            models.Index(fields=['is_active']),
        ]
    
    def __str__(self):
        return f"{self.airline} {self.flight_number}: {self.departure_airport.code} → {self.arrival_airport.code}"
    
    def save(self, *args, **kwargs):
        """
        Genera número de vuelo automático si no existe y valida datos antes de guardar
        """
        if not self.flight_number:
            # Generar número de vuelo automático: AA123
            prefix = ''.join(random.choices(string.ascii_uppercase, k=2))
            suffix = ''.join(random.choices(string.digits, k=3))
            self.flight_number = f"{prefix}{suffix}"
            
            while Flight.objects.filter(flight_number=self.flight_number).exists():
                prefix = ''.join(random.choices(string.ascii_uppercase, k=2))
                suffix = ''.join(random.choices(string.digits, k=3))
                self.flight_number = f"{prefix}{suffix}"
    
    # Para nuevos vuelos, establecer asientos disponibles igual al total
        is_new = not self.pk
        if is_new:
            self.available_seats = self.total_seats
    
        super().save(*args, **kwargs)
    
    # Crear asientos si es un nuevo vuelo
        if is_new:
            self.create_seats()
        
    def create_seats(self):
        """Crea todos los asientos para este vuelo de manera más robusta"""
        try:
            # Primero eliminar cualquier asiento existente (por si acaso)
            Seat.objects.filter(flight=self).delete()
            
            rows = range(1, (self.total_seats // 6) + 2)  # 6 asientos por fila
            letters = 'ABCDEF'
            seat_numbers = [
                f"{row}{letter}" 
                for row in rows 
                for letter in letters[:6]
            ][:self.total_seats]
            
            seats_to_create = [
                Seat(
                    flight=self,
                    seat_number=seat_num,
                    status='AVAILABLE'
                ) for seat_num in seat_numbers
            ]
            
            # Crear en lotes de 50 para mejor performance
            batch_size = 50
            for i in range(0, len(seats_to_create), batch_size):
                Seat.objects.bulk_create(seats_to_create[i:i+batch_size])
                
            return True
        except Exception as e:
            logger.error(f"Error creando asientos para vuelo {self.id}: {str(e)}")
            return False
    
    @property
    def duration(self):
        """Duración del vuelo como propiedad"""
        return self.arrival_time - self.departure_time
    
    @property
    def seat_map(self):
        """Genera un mapa de asientos para el vuelo"""
        rows = range(1, (self.total_seats // 6) + 2)  # 6 asientos por fila
        letters = 'ABCDEF'
        return [f"{row}{letter}" for row in rows for letter in letters[:6]][:self.total_seats]
    
    def get_seat_percentage(self):
        """Porcentaje de ocupación del vuelo"""
        return ((self.total_seats - self.available_seats) / self.total_seats) * 100
    
    def deactivate_if_past(self):
        """Desactiva el vuelo si la fecha de salida ya pasó"""
        if self.departure_time < timezone.now() and self.is_active:
            self.is_active = False
            self.save()
            return True
        return False
    def delete(self, *args, **kwargs):
        # Cancelar todas las reservas asociadas de forma eficiente
        bookings = self.booking_set.all()
        for booking in bookings:
            booking.cancel(notify_user=True)
        super().delete(*args, **kwargs)

class Seat(models.Model):
    """
    Modelo para asientos individuales con estado y relación a vuelos
    """
    STATUS_CHOICES = [
        ('AVAILABLE', 'Disponible'),
        ('RESERVED', 'Reservado'),
        ('OCCUPIED', 'Ocupado'),
    ]
    
    flight = models.ForeignKey(
        Flight,
        on_delete=models.CASCADE,
        related_name='seats',
        verbose_name="Vuelo"
    )
    seat_number = models.CharField(
        max_length=4,
        verbose_name="Número de asiento"
    )
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='AVAILABLE',
        verbose_name="Estado"
    )
    booking = models.ForeignKey(
        'Booking',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='booked_seats',
        verbose_name="Reserva asociada"
    )
    
    class Meta:
        unique_together = ('flight', 'seat_number')
        verbose_name = "Asiento"
        verbose_name_plural = "Asientos"
        indexes = [
            models.Index(fields=['flight', 'status']),
            models.Index(fields=['booking']),
        ]
    def __str__(self):
        return f"Asiento {self.seat_number} - {self.flight}"

class Booking(models.Model):
    """
    Modelo para reservas con gestión de pagos y estados
    """
    STATUS_CHOICES = [
        ('SELECTED', 'Seleccionado'),
        ('PENDING', 'Pendiente de pago'),
        ('CONFIRMED', 'Confirmado'),
        ('CANCELLED', 'Cancelado'),
    ]
    
    user = models.ForeignKey(
        CustomUser, 
        on_delete=models.CASCADE, 
        db_index=True,
        verbose_name="Usuario"
    )
    flight = models.ForeignKey(
        Flight, 
        on_delete=models.CASCADE, 
        db_index=True,
        verbose_name="Vuelo"
    )
    booking_date = models.DateTimeField(
        auto_now_add=True, 
        db_index=True,
        verbose_name="Fecha de reserva"
    )
    passengers = models.IntegerField(
        default=1,
        verbose_name="Número de pasajeros"
    )
    total_price = models.DecimalField(
        max_digits=12, 
        decimal_places=2,
        verbose_name="Precio total"
    )
    booking_reference = models.CharField(
        max_length=8, 
        unique=True,
        verbose_name="Referencia de reserva"
    )
    status = models.CharField(
        max_length=10, 
        choices=STATUS_CHOICES, 
        default='SELECTED',
        db_index=True,
        verbose_name="Estado"
    )
    
    class Meta:
        ordering = ['-booking_date']
        verbose_name = "Reserva"
        verbose_name_plural = "Reservas"
        indexes = [
            models.Index(fields=['flight', 'status']),
            models.Index(fields=['user', 'booking_date']),
            models.Index(fields=['status', 'booking_date']),
            models.Index(fields=['user', 'status']),
        ]
    
    def __str__(self):
        return f"Reserva {self.booking_reference} - {self.user.username}"
    
    def save(self, *args, **kwargs):
        """
        Genera referencia de reserva automática y calcula precio total
        """
        if not self.booking_reference:
            self.booking_reference = self.generate_reference()
        
        if not self.total_price and hasattr(self, 'flight'):
            self.total_price = self.flight.price * self.passengers
        
        super().save(*args, **kwargs)
        
        # Si la reserva se confirma, crear el pago asociado
        if self.status == 'CONFIRMED' and not hasattr(self, 'payment'):
            Payment.objects.create(
                booking=self,
                amount=self.total_price,
                payment_method='QR'  # Método por defecto
            )

    def generate_reference(self):
        """Genera una referencia única de 8 caracteres alfanuméricos"""
        return ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
    
    def send_confirmation_email(self):
        """Envía email de confirmación de reserva"""
        subject = 'Confirmación de reserva en Velaris'
        message = f'''
        Hola {self.user.username},
        
        Tu reserva ha sido confirmada:
        
        Número de reserva: {self.booking_reference}
        Vuelo: {self.flight}
        Fecha: {self.flight.departure_time.strftime('%d/%m/%Y %H:%M')}
        Pasajeros: {self.passengers}
        Precio total: ${self.total_price:,.2f} COP
        
        Gracias por elegir Velaris!
        '''
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [self.user.email],
            fail_silently=False,
        )
    
    def send_cancellation_email(self):
        """Envía email de cancelación de reserva"""
        subject = 'Cancelación de reserva en Velaris'
        message = f'''
        Hola {self.user.username},
        
        Lamentamos informarte que tu reserva ha sido cancelada:
        
        Detalles:
        - Número: {self.booking_reference}
        - Vuelo: {self.flight}
        - Fecha: {self.flight.departure_time.strftime('%d/%m/%Y %H:%M')}
        - Pasajeros: {self.passengers}
        '''
        
        if self.status == 'CONFIRMED':
            message += '''
            
            Nuestro equipo se comunicará contigo en las próximas 48 horas
            para gestionar el proceso de reembolso.
            '''
        elif self.status == 'PENDING':
            message += '''
            
            El pago no fue procesado completamente.
            Si tienes alguna duda sobre tu transacción, contáctanos.
            '''
        
        message += '''
        
        Atentamente,
        El equipo de Velaris
        '''
        
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [self.user.email],
            fail_silently=False,
        )
    
    # flights/models.py
    def cancel(self, notify_user=True):
        """Cancela la reserva y notifica al usuario según el estado"""
        try:
            # Actualizar los asientos en una sola operación
            Seat.objects.filter(booking=self).update(status='AVAILABLE', booking=None)
            
            # Si hay pago asociado, marcarlo como reembolsado (solo en estado)
            if hasattr(self, 'payment'):
                self.payment.status = 'REFUNDED'
                self.payment.save()
            
            # Notificar al usuario si es necesario
            if notify_user:
                self.send_cancellation_email_async()
            
            # Eliminar la reserva
            self.delete()
            return True
        except Exception as e:
            logger.error(f"Error al cancelar reserva {self.id}: {str(e)}")
            return False

    def send_cancellation_email_async(self):
        """Envía email de cancelación de forma asíncrona según el estado"""
        from django.core.mail import send_mail
        from django.conf import settings
        from threading import Thread
        
        def send_email():
            try:
                subject = 'Cancelación de reserva en Velaris'
                
                # Mensaje base
                message = f'''
                Hola {self.user.username},
                
                Lamentamos informarte que tu reserva ha sido cancelada:
                
                Detalles:
                - Número: {self.booking_reference}
                - Vuelo: {self.flight}
                - Fecha: {self.flight.departure_time.strftime('%d/%m/%Y %H:%M')}
                - Pasajeros: {self.passengers}
                '''
                
                # Mensajes específicos por estado
                if self.status == 'CONFIRMED':
                    message += '''
                    
                    Nuestro equipo se comunicará contigo en las próximas 48 horas
                    para gestionar el proceso de reembolso correspondiente.
                    '''
                elif self.status == 'PENDING':
                    message += '''
                    
                    El proceso de pago fue cancelado. Si tienes alguna duda
                    sobre tu transacción, por favor contáctanos.
                    '''
                else:  # SELECTED u otros estados
                    message += '''
                    
                    Tu selección ha sido cancelada. Si fue un error, puedes
                    realizar una nueva reserva cuando lo desees.
                    '''
                
                message += '''
                
                Atentamente,
                El equipo de Velaris
                '''
                
                send_mail(
                    subject,
                    message,
                    settings.DEFAULT_FROM_EMAIL,
                    [self.user.email],
                    fail_silently=False,
                )
            except Exception as e:
                logger.error(f"Error enviando email de cancelación: {str(e)}")
        
        # Iniciar el hilo para enviar el email
        Thread(target=send_email).start()

class Payment(models.Model):
    """
    Modelo para gestionar pagos con generación de QR
    """
    STATUS_CHOICES = [
        ('PENDING', 'Pendiente'),
        ('COMPLETED', 'Completado'),
        ('FAILED', 'Fallido'),
        ('REFUNDED', 'Reembolsado'),
    ]
    
    PAYMENT_METHODS = [
        ('QR', 'Pago con QR'),
        ('CARD', 'Tarjeta de crédito'),
        ('CASH', 'Efectivo'),
        ('TRANSFER', 'Transferencia bancaria'),
    ]
    
    booking = models.OneToOneField(
        Booking,
        on_delete=models.CASCADE,
        related_name='payment',
        verbose_name="Reserva"
    )
    amount = models.DecimalField(
        max_digits=12, 
        decimal_places=2,
        verbose_name="Monto"
    )
    payment_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Fecha de pago"
    )
    transaction_id = models.CharField(
        max_length=100,
        unique=True,
        verbose_name="ID de transacción"
    )
    status = models.CharField(
        max_length=10, 
        choices=STATUS_CHOICES, 
        default='PENDING',
        verbose_name="Estado"
    )
    payment_method = models.CharField(
        max_length=10,
        choices=PAYMENT_METHODS,
        default='QR',
        verbose_name="Método de pago"
    )
    qr_code = models.ImageField(
        upload_to='payments/qr/',
        blank=True,
        null=True,
        verbose_name="Código QR"
    )
    
    class Meta:
        ordering = ['-payment_date']
        verbose_name = "Pago"
        verbose_name_plural = "Pagos"
    
    def __str__(self):
        return f"Pago {self.transaction_id} - {self.get_status_display()}"
    
    def save(self, *args, **kwargs):
        """
        Genera ID de transacción y código QR al guardar
        """
        if not self.transaction_id:
            self.transaction_id = self.generate_transaction_id()
        
        if not self.qr_code and self.payment_method == 'QR':
            self.generate_qr_code()
        
        super().save(*args, **kwargs)
    
    def generate_transaction_id(self):
        """Genera un ID de transacción único"""
        date_part = timezone.now().strftime('%Y%m%d')
        random_part = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
        return f"PAY-{date_part}-{random_part}"
    
    def generate_qr_code(self):
        """Genera un código QR con la información del pago"""
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        
        # Datos para el QR (podría ser un enlace de pago real)
        qr_data = f"""
        Velaris Airlines - Pago de reserva
        Referencia: {self.booking.booking_reference}
        Monto: ${self.amount:,.2f} COP
        ID Transacción: {self.transaction_id}
        """
        
        qr.add_data(qr_data)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        
        buffer = BytesIO()
        img.save(buffer, format="PNG")
        filename = f"qr_{self.transaction_id}.png"
        
        self.qr_code.save(filename, ContentFile(buffer.getvalue()), save=False)
    
    def mark_as_completed(self):
        """Marca el pago como completado"""
        self.status = 'COMPLETED'
        self.save()
        
        # Actualizar estado de la reserva
        self.booking.status = 'CONFIRMED'
        self.booking.save()
        
        # Actualizar estado de los asientos
        self.booking.seats.update(status='OCCUPIED')
    
    def mark_as_failed(self):
        """Marca el pago como fallido"""
        self.status = 'FAILED'
        self.save()
        
        # Cancelar la reserva asociada
        self.booking.cancel(notify_user=True)
    
    def process_refund(self):
        """Procesa un reembolso del pago"""
        if self.status != 'COMPLETED':
            raise ValueError("Solo se pueden reembolsar pagos completados")
        
        self.status = 'REFUNDED'
        self.save()
        
        # Cancelar la reserva asociada
        self.booking.cancel(notify_user=True)