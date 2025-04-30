from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.mail import send_mail
from django.conf import settings
import secrets
import string
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.contrib.auth.hashers import make_password, check_password


def generate_token(length=32):
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))

class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, blank=True)
    is_active = models.BooleanField(default=False)
    email_verified = models.BooleanField(default=False)
    verification_token = models.CharField(max_length=32, default=generate_token)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def set_password(self, raw_password):
        self.password = make_password(raw_password)

    def check_password(self, raw_password):
        return check_password(raw_password, self.password)
    
    def send_verification_email(self):
        subject = 'Verifica tu cuenta en Velaris 2.0'
        message = f'''
        Hola {self.username},
        
        Por favor verifica tu cuenta haciendo clic en el siguiente enlace:
        {settings.BASE_URL}/accounts/verify-email/{self.verification_token}/
        
        Gracias,
        El equipo de Velaris 2.0
        '''
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [self.email],
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