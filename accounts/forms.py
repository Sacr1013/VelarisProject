from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.forms import AuthenticationForm, PasswordResetForm, SetPasswordForm
from django.core.exceptions import ValidationError
from .models import CustomUser
from django.db.models import Q
from axes.models import AccessAttempt 

class LoginForm(AuthenticationForm):
    username = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'form-control'}),
        label="Correo electrónico"
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        label="Contraseña"
    )

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get('username')
        
        if email:
            try:
                user = CustomUser.objects.get(email=email)
                if not user.is_active:
                    raise ValidationError("Su cuenta está inactiva.")
                if not user.email_verified:
                    raise ValidationError("Por favor verifique su email antes de iniciar sesión.")
            except CustomUser.DoesNotExist:
                pass  # Django-axes manejará el intento fallido
        
        return cleaned_data



class CustomPasswordResetForm(PasswordResetForm):
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'form-control'}),
        label="Correo electrónico"
    )

class CustomSetPasswordForm(SetPasswordForm):
    new_password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        label="Nueva contraseña"
    )
    new_password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        label="Confirmar nueva contraseña"
    )

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True, label="Correo Electrónico")
    phone = forms.CharField(max_length=20, required=False, label="Teléfono")

    class Meta:
        model = CustomUser
        fields = ("username", "email", "phone", "password1", "password2")

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if CustomUser.objects.filter(email=email).exists():
            raise ValidationError("Este correo electrónico ya está registrado")
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.is_active = False  # Usuario inactivo hasta verificación
        if commit:
            user.save()
            user.send_verification_email()  # Enviar correo de verificación
        return user