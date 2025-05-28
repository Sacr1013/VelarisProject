from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.mail import send_mail
from django.conf import settings
import secrets
import string
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.contrib.auth.hashers import make_password, check_password
from django.template.loader import render_to_string


def generate_token(length=32):
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))

class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    is_active = models.BooleanField(default=False)
    email_verified = models.BooleanField(default=False)
    verification_token = models.CharField(max_length=32, default=generate_token)
    profile_photo = models.ImageField(
        upload_to='profile_photos/',
        null=True,
        blank=True,
        verbose_name="Foto de perfil"
    )
    SEAT_PREF_CHOICES = [
        ('window', 'Ventana'),
        ('aisle', 'Pasillo'),
        ('none', 'Sin preferencia'),
    ]
    seat_preference = models.CharField(
        max_length=20,
        choices=SEAT_PREF_CHOICES,
        default='none',
        blank=True
    )
    MEAL_PREF_CHOICES = [
        ('standard', 'Estándar'),
        ('vegetarian', 'Vegetariano'),
        ('vegan', 'Vegano'),
    ]
    meal_preference = models.CharField(
        max_length=20,
        choices=MEAL_PREF_CHOICES,
        default='standard',
        blank=True
    )
    LANGUAGE_CHOICES = [
        ('es', 'Español'),
        ('en', 'English'),
    ]
    language = models.CharField(
        max_length=10,
        choices=LANGUAGE_CHOICES,
        default='es'
    )
    CURRENCY_CHOICES = [
        ('COP', 'Peso Colombiano'),
        ('USD', 'Dólar Estadounidense'),
        ('EUR', 'Euro'),
    ]
    currency = models.CharField(
        max_length=5,
        choices=CURRENCY_CHOICES,
        default='COP'
    )
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def set_password(self, raw_password):
        self.password = make_password(raw_password)

    def check_password(self, raw_password):
        return check_password(raw_password, self.password)
    
    def send_verification_email(self):
        context = {
            'user': self,
            'verification_url': f"{settings.BASE_URL}/accounts/verify-email/{self.verification_token}/",
            'support_email': settings.SUPPORT_EMAIL
        }
        
        subject = 'Verifica tu cuenta en Velaris 2.0'
        
        # Versión HTML
        html_message = render_to_string('emails/email_verification.html', context)
        
        # Versión de texto plano
        text_message = f"""Hola {self.username},
        
        Por favor verifica tu cuenta haciendo clic en el siguiente enlace:
        {context['verification_url']}

        Gracias,
        El equipo de Velaris 2.0"""

        send_mail(
            subject,
            text_message,
            settings.DEFAULT_FROM_EMAIL,
            [self.email],
            html_message=html_message,
            fail_silently=False,
        )
    
    def send_password_reset_email(self):
        token = generate_token()
        self.verification_token = token
        self.save()
        
        subject = 'Restablece tu contraseña en Velaris 2.0'
        message = f'''
        Hola {self.username},
        
        Para restablecer tu contraseña, haz clic en el siguiente enlace:
        {settings.BASE_URL}/accounts/reset-password/{token}/
        
        Si no solicitaste este cambio, ignora este mensaje.
        
        El equipo de Velaris 2.0
        '''
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [self.email],
            fail_silently=False,
        )