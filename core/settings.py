from pathlib import Path

from decouple import config


BASE_DIR = Path(__file__).resolve().parent.parent


SECRET_KEY = config('SECRET_KEY', cast=str)

DEBUG = True

DOMAIN = config('DOMAIN', 'http://localhost:8000')

ALLOWED_HOSTS = ['*']


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # 3rd party
    'social_django',
    'widget_tweaks',

    # project apps
    'apps.accounts.apps.AccountsConfig',
    'apps.profiles.apps.ProfilesConfig',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',

    # 3rd party
    'social_django.middleware.SocialAuthExceptionMiddleware',
]

ROOT_URLCONF = 'core.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            BASE_DIR / 'templates',
        ],
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

WSGI_APPLICATION = 'core.wsgi.application'


# Database

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# Password validation

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


# Internationalization

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Europe/Kyiv'

USE_I18N = True

USE_TZ = True


# Static files

STATIC_URL = 'static/'
STATICFILES_DIRS = [
    BASE_DIR / 'static'
]

MEDIA_URL = 'media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Default primary key field type

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# auth

AUTH_USER_MODEL = 'accounts.User'

AUTHENTICATION_BACKENDS = [
    'apps.accounts.backends.UsernameOrEmailLoginBackend',
    'django.contrib.auth.backends.ModelBackend',
]

LOGIN_URL = 'accounts:login'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'


# Email

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
EMAIL_HOST = config('EMAIL_HOST', cast=str, default='smtp.gmail.com')
EMAIL_PORT = config('EMAIL_PORT', cast=str, default='587')
EMAIL_USE_TLS = config('EMAIL_USE_TLS', cast=bool, default=True)
EMAIL_USE_SSL = config('EMAIL_USE_SSL', cast=bool, default=False)
EMAIL_HOST_USER = config('EMAIL_HOST_USER', cast=str)
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', cast=str)

EMAIL_RESEND_COOLDOWN = 5 # minutes
