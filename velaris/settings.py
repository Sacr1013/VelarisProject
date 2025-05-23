from pathlib import Path
import os
from dotenv import load_dotenv
from django.contrib import messages

# Cargar variables de entorno
load_dotenv(os.path.join(Path(__file__).resolve().parent.parent, '.env'))

BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = os.environ.get('SECRET_KEY', default="b1w0)3-k#i=-bviw&z)=d8u0m9nvp0iz3=dzp+irml#2av&9&r")  # Asegúrate de tenerla en .env
DEBUG = 'RENDER' not in os.environ
ALLOWED_HOSTS = []
RENDER_EXTERNAL_HOSTNAME = os.environ.get('RENDER_EXTERNAL_HOSTNAME')
if RENDER_EXTERNAL_HOSTNAME:
    ALLOWED_HOSTS.append(RENDER_EXTERNAL_HOSTNAME)

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.humanize',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'accounts',
    'flights',
    'crispy_forms',
    'crispy_bootstrap4',
    'axes',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'velaris.middleware.AuthMessageMiddleware',
    'axes.middleware.AxesMiddleware',
]

ROOT_URLCONF = 'velaris.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'velaris.wsgi.application'

PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.PBKDF2PasswordHasher',
    'django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher',
    'django.contrib.auth.hashers.Argon2PasswordHasher',
    'django.contrib.auth.hashers.BCryptSHA256PasswordHasher',
]

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

LANGUAGE_CODE = 'es-co'
TIME_ZONE = 'America/Bogota'
USE_I18N = True
USE_L10N = True
USE_TZ = True

STATIC_URL = '/static/'
if not DEBUG:
    STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles') 
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

AUTH_USER_MODEL = 'accounts.CustomUser'
CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap4"
CRISPY_TEMPLATE_PACK = 'bootstrap4'


MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

LOGIN_URL = '/accounts/login/'
LOGIN_REDIRECT_URL = '/accounts/dashboard/'
LOGOUT_REDIRECT_URL = '/'

AUTHENTICATION_BACKENDS = [
    'axes.backends.AxesBackend',
    'django.contrib.auth.backends.ModelBackend',
]

BASE_URL = 'http://127.0.0.1:8000'  # Para desarrollo

MESSAGE_TAGS = {
    messages.DEBUG: 'info',
    messages.INFO: 'info',
    messages.SUCCESS: 'success',
    messages.WARNING: 'warning',
    messages.ERROR: 'danger',
}

# Configuración de Axes
AXES_ENABLED = True
AXES_FAILURE_LIMIT = 4
AXES_COOLOFF_TIME = 1
AXES_RESET_ON_SUCCESS = True
AXES_USERNAME_FORM_FIELD = 'username'
AXES_LOCKOUT_TEMPLATE = None
AXES_LOCKOUT_URL = None
AXES_VERBOSE = True
AXES_LOCKOUT_PARAMETERS = ["username"]
AXES_MESSAGES = {
    'account_locked': "Tu cuenta ha sido bloqueada por múltiples intentos fallidos. Por favor espera 1 hora e intenta nuevamente.",
    'credentials_wrong': "Correo o contraseña incorrectos.",
}
USE_L10N = False
DATETIME_INPUT_FORMATS = [
    '%Y-%m-%d %H:%M:%S',    # '2006-10-25 14:30:59'
    '%Y-%m-%d %H:%M',       # '2006-10-25 14:30'
    '%Y-%m-%dT%H:%M',       # '2006-10-25T14:30' (para datetime-local)
    '%Y-%m-%d',             # '2006-10-25'
]
# Importar configuraciones locales (al final del archivo)
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
DEFAULT_FROM_EMAIL = 'Velaris <no-reply@velaris.com>' 
try:
    from .local_settings import *
except ImportError:
    pass