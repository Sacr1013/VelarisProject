from pathlib import Path
import os
from dotenv import load_dotenv

# Cargar variables del .env
load_dotenv(os.path.join(Path(__file__).resolve().parent.parent, '.env'))
DB_SSLMODE = 'require' if 'neon.tech' in os.environ.get('DB_HOST', '') else 'disable'
# Configuración de la base de datos
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB_NAME'),
        'USER':  os.environ.get('DB_USER'),
        'PASSWORD':  os.environ.get('DB_PASSWORD'),
        'HOST': os.environ.get('DB_HOST'),
        'PORT': os.environ.get('DB_PORT', '5432'),  # Puerto por defecto de PostgreSQL
        'OPTIONS': {
            'sslmode': 'require',  # Opcional: si usas archivo de contraseñas
        },
    }
}

# Email
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD')
SUPPORT_EMAIL = 'soporte@tudominio.com'
# Clave secreta
SECRET_KEY = os.getenv('SECRET_KEY')

# Debug (solo desarrollo)
DEBUG = True