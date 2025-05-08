from pathlib import Path
import os
from dotenv import load_dotenv

# Cargar variables del .env
load_dotenv(os.path.join(Path(__file__).resolve().parent.parent, '.env'))

# Configuración de la base de datos
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DB_NAME'),
        'USER': os.getenv('DB_USER'),
        'PASSWORD': os.getenv('DB_PASSWORD'),
        'HOST': 'localhost',
        'PORT': '5432',
        'OPTIONS': {
            'passfile': '.pgpass',  # Opcional: si usas archivo de contraseñas
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

# Clave secreta
SECRET_KEY = os.getenv('SECRET_KEY')

# Debug (solo desarrollo)
DEBUG = True